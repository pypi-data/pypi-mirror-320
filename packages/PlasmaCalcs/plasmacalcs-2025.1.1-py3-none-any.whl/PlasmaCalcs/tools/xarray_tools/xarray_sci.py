"""
File Purpose: high-level xarray functions. May be especially useful for science.
E.g., gaussian filter, polynomial fit.
"""

import numpy as np
import xarray as xr

from ..imports import ImportFailed
try:
    import scipy.ndimage as scipy_ndimage
except ImportError as err:
    scipy_ndimage = ImportFailed('scipy.ndimage',
            'This module is required for some filtering functions.', err=err)


from .xarray_accessors import pcAccessor, pcArrayAccessor, pcDatasetAccessor
from .xarray_coords import xarray_is_sorted
from .xarray_dimensions import (
    xarray_promote_dim, xarray_ensure_dims, _paramdocs_ensure_dims,
    xarray_coarsened,
)
from .xarray_indexing import xarray_isel
from ..pytools import format_docstring
from ..sentinels import UNSET
from ...errors import (
    DimensionalityError, DimensionValueError, DimensionKeyError,
    InputError, InputConflictError, InputMissingError,
)
from ...defaults import DEFAULTS


''' --------------------- Interpolation --------------------- '''

@pcArrayAccessor.register('interp_inverse')
@format_docstring(**_paramdocs_ensure_dims)
def xarray_interp_inverse(array, interpto=None, output=None, *,
                          promote_dims_if_needed=True,
                          assume_sorted=None, assume_sorted_values=None,
                          method=None, kw_interp=None, **interpto_as_kw):
    '''interpolate a DataArray but using the array values as one of the interpolation variables;
    the result is the array of the unused interpolation coordinate.

    Example: if array has dims {{'x', 'y'}} and name 'T', and interpto specifies 'x' and 'T',
        then result will be a DataArray with dims {{'x', 'T'}} and values for 'y'.
        Special case: if interpto specifications are single values,
            the result will be scalar along that key instead of a dimension,
            e.g. if interpto['x'] = 7 (as a opposed to a 1D array like [1,2,3]),
                then result would have coordinate 'x'=7 but not have an 'x' dimension.

    [EFF] note: inefficient if choosing many values along vars other than array.name.
        each result value along those vars corresponds to its own interp call.

    The internal steps are roughly:
        (1) array.interp(all interpto vars except array.name)
        (2) array.assign_coords({{array.name: array}})
        (3) for each index along all interpto vars except array.name:
                tmp = array.isel(index).interp({{array.name: interpto[array.name]}})
                result[index] = tmp[output var]
        [TODO] still need to implement step 3 for 3D+ arrays instead of only 2D or less.

    array: xarray.DataArray
        must have non-None array.name.
    interpto: None or dict
        dictionary of {{var: value or 1D array of values}} to interpolate to.
        Keys must correspond to array.name, and coords for all except 1 dim of array.
        None --> provide interpto dict as kwargs to this function.
    output: None or str
        name for the result variable.
        None --> use the key from array.dims which is missing from interpto (after xarray_ensure_dims).
    promote_dims_if_needed: {promote_dims_if_needed}
    assume_sorted: None or bool
        whether to assume_sorted during step (1),
            i.e. during the initial interp for all interpto vars except array.name
        None --> assume_sorted if xarray_is_sorted.
        True --> assume_sorted without checking. CAUTION: only do this if you're 100% sure!
        False --> don't assume sorted. May be noticeably slower for large arrays.
    assume_sorted_values: None or bool
        whether to assume_sorted during step (3),
            i.e. during the interp using array.name as a coordinate.
        None --> assume_sorted if xarray_is_sorted. check at each index in step 3;
                 if False multiple times in a row, stop checking and just assume False.
        True --> assume_sorted without checking. CAUTION: only do this if you're 100% sure!
        False --> don't assume sorted. May be noticeably slower for large arrays.
    method: None or str
        method to pass to xarray.interp for all interpolations.
        if None, use xarray.interp method default.
    kw_interp: None or dict
        if provided, pass these kwargs to all calls of xarray.interp.
        These will eventually go to the internal interpolator method e.g. from scipy.

    interpto_as_kw: optionally, provide interpto dict as kwargs to this function.
    '''
    # misc. bookkeeping
    if array.name is None:
        raise InputError('interp_inverse expects non-None array.name.')
    if interpto and interpto_as_kw:
        raise InputConflictError('cannot provide both interpto and interpto_as_kw.')
    if interpto_as_kw:
        interpto = interpto_as_kw
    if interpto is None:
        raise InputMissingError('must provide interpto.')
    hard_var = array.name
    easy_vars = set(interpto.keys()) - {hard_var}
    interpto_easy = {k: v for k, v in interpto.items() if k != hard_var}
    interpto_hard = {hard_var: interpto[hard_var]}
    array = xarray_ensure_dims(array, easy_vars, promote_dims_if_needed=promote_dims_if_needed)
    if output is None:
        output = set(array.dims) - easy_vars - {hard_var}
        if len(output) == 0:
            errmsg = ('no acceptable output var found.'
                      f'dims={array.dims}, easy_vars={easy_vars}, hard_var={hard_var!r}')
            raise InputError(errmsg)  # [TODO] clearer debugging suggestions in errmsg.
        if len(output) >= 2:
            errmsg = ('too many acceptable output vars found.'
                      f'dims={array.dims}, easy_vars={easy_vars}, hard_var={hard_var!r}')
            raise InputError(errmsg)  # [TODO] clearer debugging suggestions in errmsg.
        output = output.pop()
    # bookkeeping of kwargs for interp
    if assume_sorted is None:
        assume_sorted = all(xarray_is_sorted(array[v]) for v in easy_vars)
    kw_interp = dict() if kw_interp is None else kw_interp.copy()
    if method is not None:
        if 'method' in kw_interp and method != kw_interp['method']:
            errmsg = f'method={method!r} but kw_interp["method"]={kw_interp["method"]!r}.'
            raise InputConflictError(errmsg)
        # else
        kw_interp['method'] = method
    # (1) intial interpolation
    array = array.interp(interpto_easy, assume_sorted=assume_sorted, **kw_interp)
    if np.any(np.isnan(array)):
        errmsg = ('initial interpolation (step 1 in xarray_interp_inverse) resulted in NaNs.\n'
                  f'This is likely due to some "out of bounds" interpto values ({easy_vars}),\n'
                  'i.e. lower than min or larger than max values of corresponding coords in array.\n'
                  'To fix, adjust requested interpolation coords for interpto vars.\n'
                  '(There is no way to find inverse when step 1 gives nans.)')
        raise DimensionValueError(errmsg)
    # (2) assign
    array = array.assign_coords({hard_var: array})
    # (3) iterating interpolations
    if array.ndim == 1:  # nothing to iterate - hard_var coord corresponds to exactly 1 dim already.
        array = xarray_promote_dim(array, hard_var)
        if assume_sorted_values is None:
            assume_sorted_values = xarray_is_sorted(array)
        array = array.interp(interpto_hard, assume_sorted=assume_sorted_values, **kw_interp)
        result = array[output].drop_vars(output)  # don't need output as a coord, it is result.values.
    elif array.ndim == 2:  # iterate over the 1 easy_var.
        if len(easy_vars) != 1:
            raise NotImplementedError('[TODO] figure out what is happening in this case & handle it.')
        easy_var = easy_vars.pop()
        easy_dim = array[easy_var].dims[0]  # not necessarily easy_var;
            # e.g. if interpto value for easy_var is DataArray with different dim.
        result = []
        if assume_sorted_values is None:
            _prev_assume_sorted = None
        else:
            _assume_sorted = assume_sorted_values
        for i_easy in range(array.sizes[easy_dim]):
            tmp = array.isel({easy_dim: i_easy})
            if assume_sorted_values is None:
                _assume_sorted = xarray_is_sorted(tmp)
                if _prev_assume_sorted == False and _assume_sorted == False:
                    assume_sorted_values = False
                _prev_assume_sorted = _assume_sorted
            tmp = xarray_promote_dim(tmp, hard_var)
            if not _assume_sorted:
                tmp = tmp.sortby(hard_var)
            tmp = tmp.drop_duplicates(hard_var)  # drop duplicates, since interp can't handle them.
            tmp = tmp.interp(interpto_hard, assume_sorted=True, **kw_interp)  # sorted=False handled above.
            tmp = tmp[output].drop_vars(output)  # don't need output as a coord, it is tmp.values.
            result.append(tmp)
        result = xr.concat(result, easy_dim)
    else:
        raise NotImplementedError('[TODO] xarray_interp_inverse with 3D+ array.')
    return result


''' --------------------- Gaussian Filter --------------------- '''

@pcAccessor.register('gaussian_filter', aliases=['blur'])
@format_docstring(**_paramdocs_ensure_dims, default_sigma=DEFAULTS.GAUSSIAN_FILTER_SIGMA)
def xarray_gaussian_filter(array, dim=None, sigma=None, *,
                           promote_dims_if_needed=True, missing_dims='raise',
                           **kw_scipy_gaussian_filter):
    '''returns array after applying scipy.ndimage.gaussian_filter to it.

    array: xarray.DataArray or Dataset
        filters this array, or each data_var in a dataset.
    dim: None or str or iterable of strs
        dimensions to filter along.
        if None, filter along all dims.
    sigma: None, number, or iterable of numbers
        standard deviation for Gaussian kernel.
        if iterable, must have same length as dim.
        if None, will use DEFAULTS.GAUSSIAN_FILTER_SIGMA (default: {default_sigma}).
    promote_dims_if_needed: {promote_dims_if_needed}
    missing_dims: {missing_dims}

    additional kwargs go to scipy.ndimage.gaussian_filter.
    '''
    if sigma is None:
        sigma = DEFAULTS.GAUSSIAN_FILTER_SIGMA
    return xarray_map(array, scipy_ndimage.gaussian_filter, sigma, axes=dim,
                      promote_dims_if_needed=promote_dims_if_needed,
                      missing_dims=missing_dims, **kw_scipy_gaussian_filter)


''' --------------------- polyfit --------------------- '''

@pcAccessor.register('polyfit')
@format_docstring(xr_polyfit_docs=xr.DataArray.polyfit.__doc__)
def xarray_polyfit(array, coord, degree, *, stddev=False, full=False, cov=False, **kw_polyfit):
    '''returns array.polyfit(coord, degree, **kw_polyfit), after swapping coord to be a dimension, if needed.
    E.g. for an array with dimension 'snap' and associated non-dimension coordinate 't',
        xarray_polyfit(array, 't', 1) is equivalent to array.swap_dims(dict(snap='t')).polyfit('t', 1).

    stddev: bool
        whether to also return the standard deviations of each coefficient in the fit.
        if True, assign the variable 'polyfit_stddev' = diagonal(polyfit_covariance)**0.5,
            mapping the diagonal (across 'cov_i', 'cov_j') to the dimension 'degree'.
            if cov False when stddev True, do not keep_cov in the result.
        Not compatible with full=True.
    full: bool
        passed into polyfit; see below.
    cov: bool
        passed into polyfit; see below.
        Note: if stddev=True when cov=False, still use cov=True during array.polyfit,
            however then remove polyfit_covariance & polyfit_residuals from result.

    Docs for xr.DataArray.polyfit copied below:
    -------------------------------------------
    {xr_polyfit_docs}
    '''
    array = xarray_promote_dim(array, coord)
    if stddev and full:
        raise InputConflictError('stddev=True incompatible with full=True.')
    cov_input = cov
    if stddev:
        cov = True
    result = array.polyfit(coord, degree, full=full, cov=cov, **kw_polyfit)
    if stddev:
        result = xarray_assign_polyfit_stddev(result, keep_cov=cov_input)
    return result

@pcDatasetAccessor.register
def xarray_assign_polyfit_stddev(dataset, *, keep_cov=True):
    '''assign polyfit stddev to dataset['polyfit_stddev'], treating dataset like a result of polyfit.
    These provide some measure of "goodness of fit"; smaller stddev means better fit.

    Specifically, stddev[k] = (covariance matrix)[k,k]**0.5 for k in range(len(dataset['degree']));
        one might quote +-stddev[k] as the error bar for the coefficient at degree=dataset['degree'][k].

    dataset: xarray.Dataset
        dataset to use for calculating polyfit_stderr and in which to assign the result.
        must contain variable 'polyfit_covariance' and dimension 'degree'.
    keep_cov: bool
        whether to keep the 'polyfit_covariance' and 'polyfit_residuals' vars in the result.

    The original dataset will not be altered; a new dataset will be returned.
    '''
    cov = dataset['polyfit_covariance']
    degree = dataset['degree']
    ndeg = len(degree)
    stddev = [cov.isel(cov_i=k, cov_j=k)**0.5 for k in range(ndeg)]
    stddev = xr.concat(stddev, 'degree').assign_coords({'degree': degree})
    result = dataset.assign(polyfit_stddev=stddev)
    if not keep_cov:
        result = result.drop_vars(['polyfit_covariance', 'polyfit_residuals'])
    return result

@pcAccessor.register('coarsened_polyfit')
@format_docstring(xr_polyfit_docs=xr.DataArray.polyfit.__doc__)
def xarray_coarsened_polyfit(array, coord, degree, window_len, *,
                             dim_coarse='window', keep_coord='middle',
                             assign_coarse_coords=True,
                             boundary=UNSET, side=UNSET,
                             stride=UNSET, fill_value=UNSET, keep_attrs=UNSET,
                             **kw_polyfit
                             ):
    '''returns result of coarsening array, then polyfitting along the fine dimension, in each window.
    E.g., make windows of length 10 along 't', then polyfit each window along 't',
    then concat the results from each window, along dim_coarse (default: 'window').

    coord: str
        coordinate to polyfit along.
    degree: int
        degree of polynomial to fit.
    window_len: int or None
        length of window to coarsen over.
        None --> polyfit without coarsening; equivalent to window_len = len(array.coords[coord])
    dim_coarse: str, default 'window'
        name of coarse dimension; the i'th value here corresponds to the i'th window.
    keep_coord: False or str in ('left', 'right', 'middle')
        along the dim_coarse dimension, also provide some of the original coord values.
        'left' --> provide the left-most value in each window.
        'middle' --> provide the middle value in each window.
        'right' --> provide the right-most value in each window.
        False --> don't provide any of the original coord values.
        if not False, result will swap dims such that coord is a dimension instead of dim_coarse.
    assign_coarse_coords: bool or coords
        coords to assign along the dim_coarse dimension.
        True --> use np.arange.
        False --> don't assign coords.
    boundary, side: UNSET or value
        if provided (not UNSET), pass this value to coarsen().
    stride, fill_value, keep_attrs: UNSET or value
        if provided (not UNSET), pass this value to construct().

    additional **kw are passed to polyfit.

    Docs for xr.DataArray.polyfit copied below:
    -------------------------------------------
    {xr_polyfit_docs}
    '''
    # bookkeeping
    if keep_coord not in ('left', 'middle', 'right', False):
        raise InputError(f'invalid keep_coord={keep_coord!r}; expected "left", "middle", "right", or False.')
    # if window_len is None or <1, don't coarsen at all.
    if window_len is None:
        return xarray_polyfit(array, coord, degree, **kw_polyfit)
    # coarsen
    coarsened = xarray_coarsened(array, coord, window_len,
                                dim_coarse=dim_coarse,
                                assign_coarse_coords=assign_coarse_coords,
                                boundary=boundary, side=side,
                                stride=stride, fill_value=fill_value, keep_attrs=keep_attrs)
    # bookkeeping
    n_windows = len(coarsened[dim_coarse])
    if n_windows < 1:
        errmsg = f'coarsened array has n_windows={n_windows} < 1; cannot polyfit.'
        raise DimensionValueError(errmsg)
    # polyfitting
    promoted = []
    for i_window in range(n_windows):
        prom = xarray_promote_dim(coarsened.isel({dim_coarse: i_window}), coord)
        promoted.append(prom)
    polyfits = []
    for arr in promoted:
        pfit = xarray_polyfit(arr, coord, degree, **kw_polyfit)
        polyfits.append(pfit)
    if keep_coord:
        results = []
        for i_window, (arr, prom) in enumerate(zip(polyfits, promoted)):  # i_window just for debugging
            i_keep = {'left': 0, 'middle': 0.5, 'right': -1}[keep_coord]
            # isel from coords[coord] instead of prom, to ensure associated coords are included too,
            #   e.g. t & snap are associated --> this will keep t & snap in the result.
            # if i_keep = 0.5, it is handled by xarray_isel fractional indexing.
            keep = xarray_isel(prom.coords[coord], {coord: i_keep})
            here = arr.assign_coords({coord: keep})
            results.append(here)
    else:
        results = polyfits
    result = xr.concat(results, dim_coarse)
    if keep_coord:
        result = xarray_promote_dim(result, coord)
    return result

