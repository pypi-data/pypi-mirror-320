"""
File Purpose: tools for saving/reading xarrays.
(xarray builtins fail for coords with dtype=object.)
"""
import ast
import os
import warnings

import numpy as np
import pandas as pd
import xarray as xr

from .xarray_accessors import pcAccessor, pcArrayAccessor, pcDatasetAccessor
from ..history import code_snapshot_info
from ...errors import (
    InputError, InputConflictError,
    SerializingError, DeserializingError,
)


''' --------------------- Serializing --------------------- '''

class XarrayIoSerializable():
    '''object that can be serialized when saving/reading xarrays.
    obj == XarrayIoSerializable.deserialize(obj.serialize()).
    obj.serialize() creates a dict d where ast.literal_eval(str(d)) == d,
        and also d['typename'] == obj._serial_typename,
            so that deserialize knows which type of object to create.
    '''
    SERIAL_TYPES = {}  # dict of {serialization name: cls}

    # # # SUBCLASS SHOULD IMPLEMENT # # #
    def to_dict(self):
        '''return dictionary of info about self.
        subclass must override this or override self.serialize to avoid using self.to_dict
        '''
        raise NotImplementedError(f"{type(self).__name__}.to_dict")

    # # # SUBCLASS MAY WISH TO OVERRIDE # # #
    @classmethod
    def from_dict(cls, d):
        '''return cls from dict d. 
        If 'd' contains 'typename', result is like cls.deserialize(d) instead,
            however, first require that result is an instance of cls (or subclass of cls).
            E.g. Fluid.from_dict(dict(typename='EppicDist', ...)) returns EppicDist,
            but Snap.from_dict(dict(typename='EppicDist', ...)) crashes with InputError.

        Subclasses wishing to alter deserialize behavior will probably override this method instead.
        '''
        if 'typename' in d:
            result = cls.deserialize(d)
            if isinstance(result, cls):
                return result
            else:
                errmsg = (f'cls.from_dict(d), with "typename" in d expected typename corresponding to subclass of cls,\n'
                          f'but got typename={d["typename"]!r}, which corresponds to type {type(result).__name__}, '
                          f'which is not a subclass of cls={cls.__name__}.\n'
                          f'To produce arbitrary XarrayIoSerializable objects, deserialize() instead of from_dict().')
                raise InputError(errmsg)
        else:
            return cls(**d)

    # # # SERIALIZATION BEHAVIOR DEFINED HERE # # #
    def __init_subclass__(cls, *, _serial_typename=None, **kw):
        '''register cls as a subclass of XarrayIoSerializable.

        _serial_typename: None or str
            name to use for this type, for serialization purposes.
            None --> use cls.__name__.
            This method also sets cls._serial_typename = _serial_typename.
        '''
        super().__init_subclass__(**kw)
        XarrayIoSerializable.register_type(cls, _serial_typename=_serial_typename)

    @staticmethod
    def register_type(cls_to_register, _serial_typename=None):
        '''register cls_to_register as a serializable subclass of XarrayIoSerializable.
        _serial_typename: str or None
            name to use for serialization. if None, use cls_to_register.__name__.
        '''
        cls = cls_to_register
        if _serial_typename is None: _serial_typename = cls.__name__
        # ensure uniqueness:
        if _serial_typename in XarrayIoSerializable.SERIAL_TYPES:
            errmsg = (f"cannot register {cls} as {_serial_typename!r} because that name is already in use.")
            raise KeyError(errmsg)
        # register cls!
        cls._serial_typename = _serial_typename
        XarrayIoSerializable.SERIAL_TYPES[cls._serial_typename] = cls

    def serialize(self):
        '''return dict of info about self, including 'typename' key.
        '''
        typename = self._serial_typename
        d = self.to_dict()
        return {"typename": typename, **d}

    @staticmethod
    def deserialize(serial):
        '''creates an XarrayIoSerializable object from a serialized representation.

        serial: dict or str
            str --> convert to dict via ast.literal_eval.
            dict must contain 'typename' key.

        The output here will be an instance of XarrayIoSerializable.SERIAL_TYPES[typename]
        '''
        _serial_input = serial  # for reference. Helps with debugging.
        if isinstance(serial, str):
            serial = ast.literal_eval(serial)
        serial = serial.copy()
        try:
            typename = serial.pop('typename')
        except KeyError:
            errmsg = (f"expected 'typename' key in input serial, but got keys={serial.keys()}.\n"
                      "to proceed without typename, consider using cls.from_dict.")
            raise DeserializingError(errmsg) from None
        cls_to_make = XarrayIoSerializable.SERIAL_TYPES[typename]
        return cls_to_make.from_dict(serial)


''' --------------------- io tools --------------------- '''

def _xarray_io_filepaths(filename, *, exist_ok=False):
    '''return dict of strs for folder, basename (without extension), netcdf_file, text_file, notes_file.
    folder will be abspath of filename, with '.pcxarr' added if needed.
    exist_ok: bool. If False and folder already exists, crash with FileExistsError.
    '''
    if not filename.endswith('.pcxarr'):
        filename += '.pcxarr'
    filepath_exists = os.path.exists(filename)
    if filepath_exists and not exist_ok:
        raise FileExistsError(f"Directory {filename!r} already exists; use a different name or set exist_ok=True.")
    folder = os.path.abspath(filename)
    basename = os.path.splitext(os.path.basename(folder))[0]
    netcdf_file = os.path.join(folder, f'{basename}.nc')
    text_file = os.path.join(folder, f'{basename}.txt')
    notes_file = os.path.join(folder, f'notes.txt')
    return dict(folder=folder, basename=basename, netcdf_file=netcdf_file, text_file=text_file, notes_file=notes_file)

def _xarray_coord_serializations(array):
    '''return serializations dict, for all array coords made of XarrayIoSerializable objects.'''
    result = dict()
    for cname, carr in array.coords.items():  # carr is the array of value(s) of this coord.
        xx = carr.values  # xx is carr as a numpy array.
        if isinstance(xx.flat[0], XarrayIoSerializable):  # [TODO] xx with mixed types with xx[0] not serializable.
            # will need to save these coords to text file via serializing, not to netcdf.
            if xx.ndim == 0:
                result[cname] = xx.flat[0].serialize()
            elif xx.ndim == 1:
                result[cname] = [x.serialize() for x in xx]  # [TODO] DimensionValueList(xx).serialize() instead?
            else:
                errmsg = (f"serialization of 2D+ XarrayIoSerializable coords not yet implemented."
                         f"(cname={cname!r}; ndim={xx.ndim}.)")
                raise SerializingError(errmsg)
    return result

def _xarray_coord_deserializations(serial):
    '''return dict of coords, deserialized (result has XarrayIoSerializable objects).
    serial: dict of {cname: cserial}
        where cserial is a dict for 0d coord, or list for 1d coord.
        2d+ coords not yet implemented.
    '''
    coords = dict()
    for cname, cserial in serial.items():
        if isinstance(cserial, dict):  # 0d coord
            coords[cname] = XarrayIoSerializable.deserialize(cserial)
        elif isinstance(cserial, list):  # 1d coord
            coords[cname] = [XarrayIoSerializable.deserialize(x) for x in cserial]
        else:
            raise DeserializingError(f"unexpected serialization type for coord {cname!r}: {type(cserial)}")
    return coords

def _xarray_best_save_engine():
    '''returns the best engine (as a str) to use for xarray save operation.
    In order of preference: 'netcdf4' > 'h5netcdf' > 'scipy'.
        netcdf4 is only first for consistency with xarray preferences.
            But, it requires you separately install netcdf binary.
        h5netcdf is probably sufficient for most users,
            and you can can pip install it without the netcdf binary.
        scipy is okay, but only compatible with netcdf3, and doesn't allow compression;
            it's always better to use h5netcdf, unless you really can't stand
            the idea of doing "pip install h5netcdf" for some reason.
    '''
    try:
        import netCDF4
        return 'netcdf4'
    except ImportError:
        pass
    try:
        import h5netcdf
        return 'h5netcdf'
    except ImportError:
        pass
    try:
        import scipy
        return 'scipy'
    except ImportError:
        pass
    errmsg = ("No suitable engine found for xarray saving; checked netCDF4, h5netcdf, and scipy.\n"
              "Recommendation: pip install h5netcdf, then try again.")
    raise ImportError(errmsg)

def _xarray_engine_compression_defaults(engine):
    '''returns dict of default compression settings, or None if this engine can't do compression.
    engine: str ('netcdf4', 'h5netcdf', 'scipy')
    result will be {'zlib': True} for 'netcdf4' and 'h5netcdf', or None for 'scipy'.
    '''
    if engine == 'netcdf4' or engine == 'h5netcdf':
        return {'zlib': True}
    elif engine == 'scipy':
        return None

def _xarray_encoding_from_compress_dict(array, compress_dict):
    '''returns encoding dict for this array (or dataset), to apply compress_dict to every var.
    if DataArray, apply compress_dict to array.
    if Dataset, apply compress_dict to each data_var.
    '''
    # xarray.to_netcdf expects encoding = dict of {var: d} for each var,
    #    where d is a dict of encoding options, e.g. compress_dict.
    # in the DataArray case, var=array.name if not None and not a dimension's name,
    #    else __xarray_dataarray_variable__.
    # in the Dataset case, var will just be one of the data_vars' names
    if isinstance(array, xr.DataArray):
        if array.name is None or array.name in array.dims:
            var = '__xarray_dataarray_variable__'
        else:
            var = array.name
        result = {var: compress_dict}
    elif isinstance(array, xr.Dataset):
        result = {var: compress_dict for var in array.data_vars}
    else:
        raise InputError(f"unexpected array type {type(array)} in _xarray_encoding_from_compress_dict.")
    return result

def _to_netcdf_engine_and_encoding_kws(array, engine, compress, encoding):
    '''return dict of values for engine and encoding, based on inputs,
    converting defaults to usable values wherever values not provided explicitly.
    '''
    if compress is not None and encoding is not None:
        errmsg = ("cannot provide both compress and encoding; "
                  f"but got compress={compress!r} and encoding={encoding!r}.")
        raise InputConflictError(errmsg)
    if engine is None:
        engine = _xarray_best_save_engine()
    else:
        KNOWN_ENGINES = {'netcdf4', 'h5netcdf', 'scipy'}
        if engine not in KNOWN_ENGINES:
            raise InputError(f"Got engine={engine!r}; expected one of {KNOWN_ENGINES}.")
    if compress is None:
        compress = _xarray_engine_compression_defaults(engine)
        if compress is None:
            compress = False
    if compress == True:
        compress = _xarray_engine_compression_defaults(engine)
        if compress is None:
            raise InputConflictError(f"engine {engine!r} incompatible with compress=True")
    # <-- hopefully at this point, compress is a dict, or False.
    if compress != False:
        encoding = _xarray_encoding_from_compress_dict(array, compress)
    return dict(engine=engine, encoding=encoding)

def _xarray_reset_multi_indexes(array):
    '''return array with all MultiIndex indexes reset, and relevant info added to array.attrs.
    the relevant info will be added as array.assign_attrs(info), where
        info = {'reset_multi_index:{d}': (tuple of associated coords)) for each reset index d}
    '''
    reset_info = {}
    for (idx, _idict) in array.indexes.group_by_index():
        if isinstance(idx, pd.MultiIndex):
            reset_info[f'reset_multi_index:{idx.name}'] = tuple(idx.names)
            array = array.reset_index(idx.name)
    if reset_info:
        array = array.assign_attrs(reset_info)
    return array

def _xarray_restore_multi_indexes(array):
    '''return array with MultiIndex indexes restored, based on 'reset_multi_index:{d}' attrs.
    also pops 'reset_multi_index:{d}' from attrs.
    See _xarray_reset_multi_indexes for more details.
    '''
    array = array.copy()  # to avoid modifying original array.
    for key, names in list(array.attrs.items()):
        if key.startswith('reset_multi_index:'):
            #name = key[len('reset_multi_index:'):]
            array = array.set_xindex(names)  # xarray figures out the appropriate name automatically.
            array.attrs.pop(key)
    return array


''' --------------------- saving & loading --------------------- '''

def _xarray_save_prep(array, *, exist_ok=False, add_meta=True,
                      reset_multi_index=True,
                      engine=None, compress=None, encoding=None, **kw_to_netcdf):
    '''return array (prepped for saving), serializations, and to_netcdf kwargs.
    provided as a separate function to help with debugging.
    '''
    # to_netcdf kwargs bookkeeping
    kw_to_netcdf.update(_to_netcdf_engine_and_encoding_kws(array, engine, compress, encoding))
    # add code meta attrs bookkeeping
    if add_meta: array = array.assign_attrs(code_snapshot_info())
    # serialize XarrayIoSerializable coords
    serializations = _xarray_coord_serializations(array)
    # reset multi indexes, if requested (and any multi indexes present)
    if reset_multi_index: array = _xarray_reset_multi_indexes(array)
    # drop serializations
    array = array.drop_vars(list(serializations.keys()))
    return array, serializations, kw_to_netcdf

@pcAccessor.register('save')
def xarray_save(array, filename=None, *, exist_ok=False, add_meta=True, notes=None,
                reset_multi_index=True,
                engine=None, compress=None, encoding=None, **kw_to_netcdf):
    '''saves the array or dataset as filename.nc with a companion text file filename.txt.
    Both will be saved into a new directory named filename.pcxarr
    ("pcxarr" stands for "PlasmaCalcs xarray.DataArray or xarray.Dataset object")

    array: xarray.DataArray or xarray.Dataset
        the array or dataset to save
    filename: None or str
        where to save the array. Extension ".pcxarr" will be added if not present.
        None --> infer filename=array.name, or "unnamed_array" if array.name is None.
                (actually: array.name.replace('/', '÷'). To avoid interpreting division as directories.)
        if filename implies directories, those directories will be created, as per os.makedirs.
    exist_ok: bool, default False
        whether it's okay if directory with the target name to already exist.
        False --> crash with FileExistsError if directory exists.
        True --> might overwrite files in that directory!
    add_meta: bool
        whether to array.assign_attrs(details about current version of PlasmaCalcs code)
        Those details include 'pc__version__', 'pc__commit_hash', and 'datetime'.
    notes: None or object to convert to str
        if provided, also save a notes.txt file containing str(notes).
        Feel free to use this to write anything, e.g. describe what array means, in words.
    reset_multi_index: bool
        whether to array.reset_index(idx) for all MultiIndex idx, before saving.
        if True, also add info to array.attrs['reset_multi_index:{d}' for reset d].
        if False, may crash with NotImplementedError if any MultiIndex present.

    additional kwargs relate to internal strategy for to_netcdf:
        engine: None or str ('netcdf4', 'h5netcdf', 'scipy')
            which engine to use for saving.
            None --> use _xarray_best_save_engine()
                    (picks first available, from netcdf4 > h5netcdf > scipy)
        compress: None, bool, or dict
            whether to compress data when writing.
            None --> True if engine can do compression, else False.
                    ('scipy' engine is not compatible with compression.)
            bool --> get dict from _xarray_engine_compression_defaults(engine)
                    (crash with InputConflictError if engine can't do compression.)
                    (default {'zlib': True} for 'netcdf4' and 'h5netcdf')
            dict --> apply this strategy to each data variable.
                    equivalent: encoding={var1: compress, var2: compress, ...}
        encoding: None or dict
            dict of {var: {encoding options for var}} across data vars.
            determined automatically if provided compress.

    returns abspath to filename.pcxarr directory where the array was saved.
    '''
    # filename/bookkeeping
    if filename is None:
        if array.name is None:
            filename = "unnamed_array"
        else:
            filename = array.name.replace('/', '÷')  # slashes in array name represent division, not file paths!
    paths = _xarray_io_filepaths(filename, exist_ok=exist_ok)
    # prepare array for saving. Also computes serializations.
    kw_prep = dict(exist_ok=exist_ok, add_meta=add_meta,
                   reset_multi_index=reset_multi_index,
                   engine=engine, compress=compress, encoding=encoding, **kw_to_netcdf)
    array, serializations, kw_to_netcdf = _xarray_save_prep(array, **kw_prep)
    # make folder (if needed) and save files. First, array without serialized coords:
    os.makedirs(paths['folder'], exist_ok=True)
    if os.path.exists(paths['netcdf_file']):
        os.remove(paths['netcdf_file'])  # (some engines require to delete old file first)
    array.to_netcdf(paths['netcdf_file'], **kw_to_netcdf)
    # save serialized coords to text file. (also, first, set xarray_object_type='DataArray' or 'Dataset')
    serializations['xarray_object_type'] = type(array).__name__
    with open(paths['text_file'], 'w') as f:
        print(serializations, file=f)  # write to file
    # save notes to text file, if relevant.
    if notes is not None:
        with open(paths['notes_file'], 'w') as f:
            print(notes, file=f)
    # return abspath to directory where array was saved
    return paths['folder']

def xarray_load(filename, *, restore_multi_index=True, **kw__xarray_open):
    '''load the array or dataset from filename.pcxarr.
    filename: str
        where to load the array from. Extension ".pcxarr" will be added if not present.
    restore_multi_index: bool
        whether to restore MultiIndexes if 'reset_multi_index:{d}' in attrs (for some d)

    additional kwargs go to xarray.open_dataarray, or xarray.open_dataset
    '''
    # filename/bookkeeping
    paths = _xarray_io_filepaths(filename, exist_ok=True)
    # load xarray type & coords info from text file then deserialize:
    with open(paths['text_file'], 'r') as f:
        serial_str = f.read()
    serial = ast.literal_eval(serial_str)
    xarray_object_type = serial.pop('xarray_object_type', 'DataArray')  # default DataArray for backwards compatibility
    # deserialize coords (do this first in case of crash to avoid loading lots of data before crashing.)
    coords = _xarray_coord_deserializations(serial)
    # load array or dataset from netcdf file:
    if xarray_object_type == 'DataArray':
        array = xr.open_dataarray(paths['netcdf_file'], **kw__xarray_open)
    elif xarray_object_type == 'Dataset':
        array = xr.open_dataset(paths['netcdf_file'], **kw__xarray_open)
    else:
        raise DeserializingError(f"unexpected xarray_object_type {xarray_object_type!r}, from {text_filename!r}.")
    # assign coords to array or dataset:
    array = array.assign_coords(coords)
    # restore MultiIndexes if requested:
    if restore_multi_index: array = _xarray_restore_multi_indexes(array)
    return array
