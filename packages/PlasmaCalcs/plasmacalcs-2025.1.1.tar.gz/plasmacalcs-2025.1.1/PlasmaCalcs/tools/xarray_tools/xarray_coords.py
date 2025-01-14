"""
File Purpose: tools related to xarray coords
"""
import numpy as np
import xarray as xr

from .xarray_accessors import pcAccessor, pcArrayAccessor, pcDatasetAccessor
from .xarray_dimensions import xarray_promote_dim, xarray_ensure_dims
from ..arrays import ndindex_array
from ..math import float_rounding as math_float_rounding
from ...errors import (
    DimensionalityError, DimensionValueError, DimensionKeyError,
    InputError, InputConflictError, InputMissingError,
)


''' --------------------- Coords --------------------- '''

@pcAccessor.register
def nondim_coord_values(array, *, scalars_only=False):
    '''returns dict of {coord name: coord.values} for all non-dimension coords (not in array.dims).
    if scalars_only, only return coord.values with ndim==0.
    '''
    result = {cname: coord.values for cname, coord in array.coords.items() if cname not in array.dims}
    if scalars_only:
        result = {cname: val for cname, val in result.items() if np.ndim(val) == 0}
    return result

@pcAccessor.register('dims_coords')
def xarray_dims_coords(array, *, include_dims_as_coords=True):
    '''returns dict of {dim name: [coord name for all coords with this dim]}.
    result[()] will be list of all scalar coords (ndim=0 so no associated dims).
    coords associated with multiple dims will appear in multiple places in the result.

    include_dims_as_coords: bool
        whether to include dims as coord names in the result.
        Dims with no same-named coord will appear in appropriate place in result.
    '''
    result = dict()
    unused_dims = set(array.dims)
    for cname, coord in array.coords.items():
        unused_dims -= set([cname])
        if len(coord.dims) == 0:
            result.setdefault((), []).append(cname)
        for dim in coord.dims:
            result.setdefault(dim, []).append(cname)
    if include_dims_as_coords and unused_dims:
        for dim in unused_dims:
            result.setdefault(dim, []).append(dim)
    return result

@pcArrayAccessor.register('assign_self_as_coord')
def xarray_assign_self_as_coord(array):
    '''return copy of array with coord named array.name, equal to array values.
    Equivalent: array.assign_coords({array.name: array})
    '''
    if array.name is None:
        raise InputError('assign_self_coord expects non-None array.name')
    return array.assign_coords({array.name: array})

@pcAccessor.register('fill_coords')
def xarray_fill_coords(array, dim=None):
    '''return copy of array with coords filled for indicated dims.
    (if all indicated dims have coords already, return original array, not a copy.)
    E.g. array with dim_1 length 50 but no coords
        --> result is just like array but has dim_1 coords = np.arange(50)

    dim: None, str, or iterable of strs
        dims for which to consider filling coords. None --> array.dims.
    '''
    if dim is None: dim = array.dims
    elif isinstance(dim, str): dim = [dim]
    to_assign = {}
    for d in dim:
        if d not in array.coords:
            to_assign[d] = array[d]  # array[d] == np.arange(len(array[d]))
    if to_assign:
        array = array.assign_coords(to_assign)
    return array

@pcAccessor.register('index_coords')
def xarray_index_coords(array, coords=None, newname='{coord}_index', *,
                        drop=False, promote=False, exist_ok=False):
    '''return copy of array with coord_index coords telling np.arange() for each coord.
    0D coords' index will be 0 if provided explicitly in coords input, else ignored.
    1D coords' index will be np.arange, e.g. coord_index[i] == i.
    2D+ coords' index will be reshaped np.ndindex, such that coord_index[i,j] == (i,j).

    coords: None or iterable of strs
        if None, use all coords and dims which don't already have coord_index.
        (e.g. 'fluid' --> make 'fluid_index', unless 'fluid_index' already exists.)
    newname: str
        string for new (index) coord names: newname.format(coord=coord).
        Default: '{coord}_index'. To keep original names, use '{coord}'
    drop: bool
        whether to drop original coords after creating coord_index coords.
        (e.g. 'fluid' --> drop 'fluid' after making 'fluid_index')
    promote: bool
        whether to promote all non-dim new index coords to dimensions.
        if True, xarray_promote_dim for all new index coords.
    exist_ok: bool
        whether it is okay if newname for coord (e.g. 'fluid_index') already exists.
        True --> replace existing coord with new coord_index.
    '''
    if coords is None:
        nonscalar_coords = [cname for cname, cval in array.coords.items() if cval.ndim >= 1]
        coords = list(set(nonscalar_coords).union(array.dims))
    elif isinstance(coords, str):
        coords = [coords]
    newnames = {cname: newname.format(coord=cname) for cname in coords}
    if len(set(newnames.values())) != len(newnames):  # crash if any newname apears multiple times:
        raise InputConflictError(f'old to new name map must have unique values but got: {newnames!r}')
    if not exist_ok:
        existing = set(array.coords).intersection(newnames.values())
        if existing:
            raise InputConflictError(f'some new coord names already exist in array.coords: {existing!r}')
    # computing new coords
    to_assign = {}
    for cname in coords:
        cc = array.coords[cname]
        if cc.ndim == 0:
            if skip_scalars:
                continue
            else:
                index = np.array(0, dtype=np.min_scalar_type(0))
        else:
            index = ndindex_array(cc.shape)
        newval = cc.copy(data=index)
        if drop:
            newval = newval.drop_vars(coords, errors='ignore')  # 'ignore' if newval missing any coords
        to_assign[newnames[cname]] = newval
    # creating result
    if drop:
        array = array.drop_vars(coords, errors='ignore')
    result = array.assign_coords(to_assign)
    if promote:
        result = xarray_ensure_dims(result, list(newnames.values()))
    #raise Exception('boom')
    return result

@pcAccessor.register('scale_coords')
def xarray_scale_coords(array, scale=None, *, missing_ok=True, **scale_as_kw):
    '''return copy of array with coords multiplied by scale.
    scale: None or dict of {coord: scale}
        dict --> multiply each coord by the corresponding number.
        None --> provide as kwargs (scale_as_kw) instead.
    scale_as_kw: if scale is None, can provide scale dict as kwargs instead.
    missing_ok: bool
        whether it is okay if some coords are missing (if yes, skip missing coords).
    '''
    if scale is None and len(scale_as_kw) == 0:
        raise InputMissingError('must provide either "scale" or "scale_as_kw".')
    if scale is not None and len(scale_as_kw) > 0:
        raise InputConflictError('cannot provide both "scale" and "scale_as_kw".')
    if scale is None:
        scale = scale_as_kw
    assign_coords = {}
    for cname, cscale in scale.items():
        try:
            cvals = array.coords[cname]
        except KeyError:
            if not missing_ok:
                raise DimensionKeyError(f'coord={cname!r} not found in array.coords.') from None
            continue
        assign_coords[cname] = cvals * cscale
    return array.assign_coords(assign_coords)

@pcAccessor.register('shift_coords')
def xarray_shift_coords(array, shift=None, *, missing_ok=True, **shift_as_kw):
    '''return copy of array with coords shifted by shift.
    shift: None or dict of {coord: shift}
        dict --> shift each coord by the corresponding number.
        None --> provide as kwargs (shift_as_kw) instead.
    shift_as_kw: if shift is None, can provide shift dict as kwargs instead.
    missing_ok: bool
        whether it is okay if some coords are missing (if yes, skip missing coords).
    '''
    if shift is None and len(shift_as_kw) == 0:
        raise InputMissingError('must provide either "shift" or "shift_as_kw".')
    if shift is not None and len(shift_as_kw) > 0:
        raise InputConflictError('cannot provide both "shift" and "shift_as_kw".')
    if shift is None:
        shift = shift_as_kw
    assign_coords = {}
    for cname, cshift in shift.items():
        try:
            cvals = array.coords[cname]
        except KeyError:
            if not missing_ok:
                raise DimensionKeyError(f'coord={cname!r} not found in array.coords.') from None
            continue
        assign_coords[cname] = cvals + cshift
    return array.assign_coords(assign_coords)

@pcAccessor.register('log_coords')
def xarray_log_coords(array, coords=None, newname='log_{coord}', *,
                      base=10, drop=True, promote=False):
    '''return copy of array with coords replaced by log coords (& renamed to log_coord)

    coords: None, str, or iterable of strs
        coords to replace with log. None --> all coords.
    newcoord: str
        string for new (logged) coord names: newcoord.format(coord=coord).
        Default: 'log_{coord}'. To keep original names, use '{coord}'
    base: number or 'e'
        log in this base. default 10.
        if not 10, result.assign_attrs({'log_base': base}).
    drop: bool
        whether to drop original coords' values.
        True --> drop original coords.
        False --> add new coords but do not adjust original coords.
    promote: bool
        whether to promote all non-dim new log coords to dimensions.
        if True, xarray_promote_dim for all new log coords.
    '''
    # bookkeeping
    if coords is None:
        coords = array.coords
    elif isinstance(coords, str):
        coords = [coords]
    newnames = {cname: newname.format(coord=cname) for cname in coords}
    if len(set(newnames.values())) != len(newnames):  # crash if any newname apears multiple times:
        raise InputConflictError(f'old to new name map must have unique values but got: {newnames!r}')
    if base == 10:
        f_log = np.log10
    else:
        array = array.assign_attrs({'log_base': base})
        if base == 'e':
            f_log = np.log
        elif base == 2:
            f_log = np.log2
        else:
            f_log = lambda x: np.log(x) / np.log(base)
    # computing new coords
    newcoords = {}
    for cname in coords:
        cvals = array.coords[cname]
        if drop:
            cvals = cvals.drop_vars(coords, errors='ignore')
        newvals = f_log(cvals)
        newcoords[newnames[cname]] = newvals
    # creating result appropriately
    if drop:
        array = array.drop_vars(coords, errors='ignore')
    result = array.assign_coords(newcoords)
    if promote:
        result = xarray_ensure_dims(result, list(newnames.values()))
    return result

@pcArrayAccessor.register('is_sorted')
def xarray_is_sorted(array, *, increasing=True):
    '''returns whether array is sorted; array must be 1D.

    increasing: bool
        True --> check for increasing order. vals[i] <= vals[i+1]
        False --> check for decreasing order. vals[i] >= vals [i+1]
    '''
    if array.ndim != 1:
        raise DimensionalityError('is_sorted expects 1D array.')
    vals = array.data
    if increasing:
        return np.all(vals[:-1] <= vals[1:])
    else:
        return np.all(vals[:-1] >= vals[1:])


''' --------------------- Coord Math --------------------- '''

@pcAccessor.register('get_dx_along')
def xarray_get_dx_along(array, coord, *, atol=0, rtol=1e-5, float_rounding=False):
    '''returns number equal to the diff along array.coords[coord], after checking that it is constant.
    result will be a single number, equal to array.coords[coord].diff(coord)[0].item().

    (Technically, also promotes coord to dim during calculations if coord was a non-dimension coordinate.)
    
    before returning result, ensure that np.allclose(array.diff(dim), atol=atol, rtol=rtol);
        if that fails, raise DimensionValueError.

    float_rounding: bool
        if True, re-create floating point result if it seems to be wrong by only a small amount,
        e.g. 0.20000000001 --> float(0.2); 0.39999999999 --> float(0.4); 0.123456781234 --> unchanged
        This sometimes improves "exact" float comparisons, if float was input from a string.
        See tools.float_rounding for more details.
    '''
    carr = array.coords[coord]
    carr = xarray_promote_dim(carr, coord)
    diff = carr.diff(coord)
    if len(diff) == 0:
        raise DimensionValueError(f'expected non-empty diff({coord!r})')
    result = diff[0].item()
    if not np.allclose(diff, result, atol=atol, rtol=rtol):
        errmsg = f'expected evenly-spaced coordinates along coord {coord!r}, but got diff={diff}'
        raise DimensionValueError(errmsg)
    if float_rounding:
        result = math_float_rounding(result)
    return result

@pcAccessor.register('differentiate')
def xarray_differentiate(array, coord, *, keep_attrs=True, **kw__differentiate):
    '''differentiate array along coord, treating array like it is an xarray.DataArray.
    more lenient than xarray.DataArray.differentiate;
        returns 0 if can't differentiate along coord (due to coord having size 1 or not existing.)

    keep_attrs: bool
        whether to copy attrs from array into the result. Default True.

    requires that array.coords and array.differentiate exist, otherwise raises AttributeError.
    '''
    coords = array.coords
    try:
        coords_x = coords[coord]
    except KeyError:
        return xr.zeros_like(array)
    size_x = np.size(coords_x)
    if size_x <= 1:
        return xr.zeros_like(array)
    else:
        result = array.differentiate(coord, **kw__differentiate)
        if keep_attrs:
            result = result.assign_attrs(array.attrs.copy())
        return result
