"""
File Purpose: xarray stats, math, and any other aggregation functions.
(aggregation: reducing array along one or more dims)
"""
import numpy as np
import xarray as xr

from .xarray_accessors import pcAccessor, pcArrayAccessor, pcDatasetAccessor
from .xarray_dimensions import (
    xarray_ensure_dims, _paramdocs_ensure_dims,
)
from ..pytools import format_docstring
from ...errors import InputConflictError
from ...defaults import DEFAULTS


''' --------------------- Docstrings --------------------- '''

_paramdocs_aggregator = {
    'dim': '''None, str, or iterable of strs
        apply operation along these dimensions''',
    'keep': '''None, str, or iterable of strs
        apply operation along all except for these dimensions.
        (can provide keep or dim, but not both.)''',
    'promote_dims_if_needed': _paramdocs_ensure_dims['promote_dims_if_needed'],
}


''' --------------------- Aggregators setup --------------------- '''

@format_docstring(**_paramdocs_aggregator)
def _xarray_aggregator_setup(array, dim=None, keep=None, promote_dims_if_needed=True):
    '''returns (array, dim, keep), adjusted appropriately.
    adjustments include:
        - result dim & keep will be None or list of str. (replace str input s with [s])
        - if keep provided, infer dim from array.
        - can provide dim or keep but not both.
        - (if dim or keep provided) ensure all dim in array.dims.
            promote relevant scalar coords if promote_dims_if_needed.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    if dim is not None and keep is not None:
        raise InputConflictError('cannot provide both "dim" and "keep".')
    if keep is not None:
        keep = [keep] if isinstance(keep, str) else list(keep)
        dim = set(array.dims) - set(keep)
    if dim is not None:
        dim = [dim] if isinstance(dim, str) else list(dim)
        array = xarray_ensure_dims(array, dim, promote_dims_if_needed=promote_dims_if_needed)
    return array, dim, keep

@pcAccessor.register('aggregate', aliases=['agg'])
@format_docstring(**_paramdocs_aggregator)
def xarray_aggregate(array, f, dim=None, *, keep=None, promote_dims_if_needed=True, **kw):
    '''returns array aggregated along dim using f.

    f: callable or str
        function to aggregate along dim. E.g. xarray.DataArray.sum, or 'mean'.
        Call signature should be like: f(array, dim, **kw).
        str --> will call getattr(array, f)(dim, **kw).
    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}

    additional kwargs are passed to f.
    '''
    __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
    array, dim, keep = _xarray_aggregator_setup(array, dim, keep, promote_dims_if_needed)
    if isinstance(f, str):
        g = getattr(array, f)
        return g(dim, **kw)
    else:
        return f(array, dim, **kw)


''' --------------------- Math (except stats) --------------------- '''

@pcAccessor.register('sum')
@format_docstring(**_paramdocs_aggregator)
def xarray_sum(array, dim=None, *, keep=None, promote_dims_if_needed=True, **kw):
    '''Like xarray sum but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}

    additional kwargs are passed to array.sum.
    '''
    return xarray_aggregate(array, 'sum', dim=dim, keep=keep, promote_dims_if_needed=promote_dims_if_needed, **kw)


''' --------------------- Stats --------------------- '''

@pcArrayAccessor.register('stats')  # ArrayAccessor because this fails for Datasets
@format_docstring(**_paramdocs_aggregator)
def xarray_stats(array, dim=None, stats=None, *, keep=None, promote_dims_if_needed=True, **kw):
    '''returns Dataset of stats for array: min, mean, median, max, std, rms.

    dim: {dim}
    stats: None or iterable of str from ('min', 'mean', 'median', 'max', 'std', 'rms')
        which stats to compute & include in the result.
        None --> equivalent to stats=['min', 'mean', 'median', 'max', 'std', 'rms'].
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}

    additional kwargs are passed to array.min, mean, median, max, and std.
    Can provide skipna=True/False to skip NaNs or not; default True for float dtypes.
    '''
    array, dim, keep = _xarray_aggregator_setup(array, dim, keep, promote_dims_if_needed)
    stats = ['min', 'mean', 'median', 'max', 'std', 'rms'] if stats is None else list(stats)
    results = dict()
    if 'min' in stats: results['min'] = array.min(dim, **kw)
    if 'mean' in stats: results['mean'] = array.mean(dim, **kw)
    if 'median' in stats: results['median'] = array.median(dim, **kw)
    if 'max' in stats: results['max'] = array.max(dim, **kw)
    if 'std' in stats: results['std'] = array.std(dim, **kw)
    if 'rms' in stats: results['rms'] = (array**2).mean(dim, **kw)**0.5
    results = {k: results[k] for k in stats}  # <-- style: put in same order as stats.
    attrs = array.attrs.copy() if xr.get_options()['keep_attrs'] else None
    return xr.Dataset(results, attrs=attrs)

@pcAccessor.register('min')
@format_docstring(**_paramdocs_aggregator)
def xarray_min(array, dim=None, *, keep=None, promote_dims_if_needed=True, **kw):
    '''Like xarray min but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}

    additional kwargs are passed to array.min.
    '''
    return xarray_aggregate(array, 'min', dim=dim, keep=keep, promote_dims_if_needed=promote_dims_if_needed, **kw)

@pcAccessor.register('mean')
@format_docstring(**_paramdocs_aggregator)
def xarray_mean(array, dim=None, *, keep=None, promote_dims_if_needed=True, **kw):
    '''Like xarray mean but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}

    additional kwargs are passed to array.mean.
    '''
    return xarray_aggregate(array, 'mean', dim=dim, keep=keep, promote_dims_if_needed=promote_dims_if_needed, **kw)

@pcAccessor.register('median')
@format_docstring(**_paramdocs_aggregator)
def xarray_median(array, dim=None, *, keep=None, promote_dims_if_needed=True, **kw):
    '''Like xarray median but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}

    additional kwargs are passed to array.median.
    '''
    return xarray_aggregate(array, 'median', dim=dim, keep=keep, promote_dims_if_needed=promote_dims_if_needed, **kw)

@pcAccessor.register('max')
@format_docstring(**_paramdocs_aggregator)
def xarray_max(array, dim=None, *, keep=None, promote_dims_if_needed=True, **kw):
    '''Like xarray max but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}

    additional kwargs are passed to array.max.
    '''
    return xarray_aggregate(array, 'max', dim=dim, keep=keep, promote_dims_if_needed=promote_dims_if_needed, **kw)

@pcAccessor.register('std')
@format_docstring(**_paramdocs_aggregator)
def xarray_std(array, dim=None, *, keep=None, promote_dims_if_needed=True, **kw):
    '''Like xarray std but first promotes dims if needed, and accepts 'keep' option.

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}

    additional kwargs are passed to array.std.
    '''
    return xarray_aggregate(array, 'std', dim=dim, keep=keep, promote_dims_if_needed=promote_dims_if_needed, **kw)

@pcAccessor.register('rms')
@format_docstring(**_paramdocs_aggregator)
def xarray_rms(array, dim=None, *, keep=None, promote_dims_if_needed=True, **kw):
    '''(array**2).mean(dim, **kw)**0.5

    dim: {dim}
    keep: {keep}
    promote_dims_if_needed: {promote_dims_if_needed}
    '''
    mean2 = xarray_mean(array**2, dim=dim, keep=keep, promote_dims_if_needed=promote_dims_if_needed, **kw)
    return mean2**0.5
