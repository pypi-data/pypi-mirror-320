"""
File Purpose: misc. tools related to xarray
"""
import numpy as np
import xarray as xr

from .xarray_accessors import pcAccessor, pcArrayAccessor, pcDatasetAccessor
from ...errors import InputError, DimensionKeyError


''' --------------------- Copying --------------------- '''

@pcAccessor.register('copy_kw')
def xarray_copy_kw(array, dims=None, *, name=None):
    '''return dict of info suitable for creating a similar array or dataset.
    result includes dims, coords, and attrs (unchanged, copied).

    dims: None, str, or iterable of str
        if provided, only include these dims (and related coords) in the result.
        Useful if only interested in some of the dims,
            e.g. if array has x,y,z,t dims but only want to mimic dims and coords from x,t.
    name: None, bool, or str
        whether to also include name in result
        None --> True if array has name, else False
        True --> name = array.name.
        str --> name = name.
    '''
    result = dict()
    if isinstance(dims, str): dims = [dims]
    if dims is None: dims = array.dims
    elif any(d not in array.dims for d in dims):
        errmsg = (f'cannot copy_kw for dims={dims!r} because some dims not in array.dims={array.dims}.')
        raise DimensionKeyError(errmsg)
    result['dims'] = dims
    coords = dict()
    for cname, cval in array.coords.items():
        if len(cval.dims) == 0:  # scalar coord; always keep!
            coords[cname] = cval
        elif len(cval.dims) == 1 and cval.dims[0] in dims:  # 1D coord, and relevant
            coords[cname] = cval
        elif all(d in dims for d in cval.dims):  # 2D+ coord, and all relevant dims exist
            coords[cname] = (tuple(cval.dims), cval.data)
    result['coords'] = coords
    attrs = array.attrs.copy()
    result['attrs'] = attrs
    if name is None:
        name = hasattr(array, 'name')
    if name == True:
        name = array.name
    if name != False:
        result['name'] = name
    return result


''' --------------------- Converting Dataset to Array --------------------- '''

@pcAccessor.register('as_array')
def xarray_as_array(array):
    '''return array if DataArray, else array[var] if array is Dataset with one var.
    if array is Dataset with multiple vars, crash with InputError.
    '''
    if isinstance(array, xr.DataArray):
        return array
    elif isinstance(array, xr.Dataset):
        if len(array) == 1:
            return array[list(array)[0]]
        else:
            errmsg = ('as_array(Dataset) only possible if Dataset has exactly 1 data_var, '
                     f'but got Dataset with {len(array)} vars: {list(array.data_vars)}.')
            raise InputError(errmsg)
    else:
        raise InputError(f'cannot convert object of type {type(array)} to DataArray.')


''' --------------------- Math Checks --------------------- '''

@pcAccessor.register('where_finite')
def xarray_where_finite(array):
    '''returns array, masked with NaNs anywhere that the values are not finite.'''
    return array.where(np.isfinite)


''' --------------------- Type Casting --------------------- '''

@pcDatasetAccessor.register('astypes')
def xarray_astypes(ds, var_to_dtype):
    '''return copy of ds with var.astype(dtype) for each var, dtype in var_to_dtype.items()'''
    to_assign = {dvar: ds[dvar].astype(dtype) for dvar, dtype in var_to_dtype.items()}
    return ds.assign(**to_assign)

@pcAccessor.register('convert_types')
def xarray_convert_types(array, oldtype_to_newtype):
    '''return copy of array or dataset, using var.astype(newtype) for any var with oldtype,
    for oldtype, newtype in oldtype_to_newtype.items().
    '''
    if isinstance(array, xr.Dataset):
        ds = array
        to_convert = dict()
        for var, val in ds.items():
            for oldtype, newtype in oldtype_to_newtype.items():
                if val.dtype == oldtype:
                    to_convert[var] = newtype
                    break
        return xarray_astypes(ds, to_convert)
    else:
        for oldtype, newtype in oldtype_to_newtype.items():
            if array.dtype == oldtype:
                return array.astype(newtype)
        else:  # no match found during loop
            return array


''' --------------------- Converting coords to strings --------------------- '''

@pcAccessor.register('object_coords_to_str')
def xarray_object_coords_to_str(array, *, maxlen=None, ndim_min=1):
    '''return copy of array with coords (of dtype=object) converted to string.
    maxlen: None or int>=5
        if int, truncate longer strings to this length-3, and add '...' to end.
    ndim_min: int
        minimum number of dimensions for a coord to be converted.
        e.g. ndim_min=1 --> coords with ndim=0 will not be altered
    '''
    to_assign = {}
    for cname, cc in array.coords.items():
        if cc.dtype == object and cc.ndim >= ndim_min:
            if cc.ndim >= 2:
                raise NotImplementedError('object_coords_to_str does not yet support ndim>=2.')
            cvals = [str(v) for v in cc.values]
            if maxlen is not None:
                cvals = [v[:maxlen-3] + '...' if len(v) > maxlen else v for v in cvals]
            to_assign[cname] = cc.copy(data=cvals)
    return array.assign_coords(to_assign)
