"""
File Purpose: FluidsLoader
"""

from ..quantity_loader import QuantityLoader

from ...tools import (
    xarray_sum,
)

class FluidsLoader(QuantityLoader):
    '''load fluid-related quantities, e.g. fluids_sum_{var}'''

    @known_pattern(r'sum_(s|fluid)_(.+)', deps=[1], reduces_dims=['fluid'])  # e.g. sum_s_n, sum_fluid_T
    def get_sum_fluid_var(self, var, *, _match=None):
        '''var summed across self.fluid. Equivalent: self(var).pc.sum('fluid').
        (if not self.fluid_is_iterable(), result numerically equivalent to self(var).)
        aliases: sum_fluid_var or sum_s_var.
        '''
        _s_or_fluid, var, = _match.groups()
        return xarray_sum(self(var), dim='fluid')
    
    @known_pattern(r'sum_fluids_(.+)', deps=[0], ignores_dims=['fluid'])  # e.g. sum_fluids_n
    def get_sum_fluids_var(self, var, *, _match=None):
        '''var summed across self.fluids. Equivalent: self(var, fluid=None).pc.sum('fluid').'''
        var, = _match.groups()
        return xarray_sum(self(var), dim='fluid')

    @known_pattern(r'sum_(j|jfluid)_(.+)', deps=[1], reduces_dims=['jfluid'])  # e.g. sum_j_n, sum_jfluid_T
    def get_sum_jfluid_var(self, var, *, _match=None):
        '''var summed across self.jfluid. Equivalent: self(var).pc.sum('jfluid').
        (if not self.jfluid_is_iterable(), result numerically equivalent to self(var).)
        aliases: sum_jfluid_var or sum_j_var.
        '''
        _j_or_jfluid, var, = _match.groups()
        return xarray_sum(self(var), dim='jfluid')

    @known_pattern(r'sum_jfluids_(.+)', deps=[0], ignores_dims=['jfluid'])  # e.g. sum_jfluids_n
    def get_sum_jfluids_var(self, var, *, _match=None):
        '''var summed across self.jfluids. Equivalent: self(var, jfluid=None).pc.sum('jfluid').'''
        var, = _match.groups()
        return xarray_sum(self(var), dim='jfluid')

    @known_pattern(r'sum_ions_(.+)', deps=[0], ignores_dims=['fluid'])  # e.g. sum_ions_n
    def get_sum_ions_var(self, var, *, _match=None):
        '''var summed across all ions in self.fluids.
        Equivalent: self(var, fluid=self.fluids.ions()).pc.sum('fluid').
        '''
        var, = _match.groups()
        return xarray_sum(self(var, fluid=self.fluids.ions()), dim='fluid')

    @known_pattern(r'sum_neutrals_(.+)', deps=[0], ignores_dims=['fluid'])  # e.g. sum_neutrals_n
    def get_sum_neutrals_var(self, var, *, _match=None):
        '''var summed across all neutrals in self.fluids.
        Equivalent: self(var, fluid=self.fluids.neutrals()).pc.sum('fluid').
        '''
        var, = _match.groups()
        return xarray_sum(self(var, fluid=self.fluids.neutrals()), dim='fluid')
