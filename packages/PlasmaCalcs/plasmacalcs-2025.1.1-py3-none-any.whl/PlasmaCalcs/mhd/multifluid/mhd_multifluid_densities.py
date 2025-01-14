"""
File Purpose: densities for multifluid analysis of single-fluid mhd
"""
import numpy as np
import xarray as xr

from .mhd_multifluid_ionization import MhdMultifluidIonizationLoader
from .species import Specie
from ..elements import Element
from ..mhd_eos_loader import MhdEosLoader
from ...defaults import DEFAULTS
from ...dimensions import SINGLE_FLUID
from ...errors import (
    FluidValueError, FluidKeyError,
    InputError, FormulaMissingError, LoadingNotImplementedError,
)
from ...quantities import QuantityLoader
from ...tools import (
    alias, simple_property,
    UNSET,
    Partition,
    xarray_promote_dim,
)

class MhdMultifluidDensityLoader(MhdMultifluidIonizationLoader, MhdEosLoader):
    '''density quantities based on mhd single-fluid values, & inferred multifluid properties.'''

    # [TODO] (check is this actually correct?) inheritance notes:
    #   implementation here expects that EosLoader will be one of the parents.
    #   However, specifying it as a parent here directly will mess up the pattern of hookups
    #   which use, e.g. BifrostMultifluidCalculator(BifrostMultifluidStuff,
    #                           MhdMultifluidCalculator, BifrostCalculator),
    #   with BifrostCalculator inheriting from BifrostEosLoader which overrides some MhdEosLoader stuff.
    #   (if MhdMultifluidDensityLoader inherited from MhdEosLoader,
    #    then the BifrostMultifluidCalculator example above would use MhdEosLoader
    #    instead of BifrostEosLoader overrides.)


    # # # MISC DENSITY-RELATED VARS, OTHER THAN NUMBER DENSITY # # #

    @known_var(load_across_dims=['fluid'])
    def get_m(self):
        '''average mass of fluid particle.
        if SINGLE_FLUID, m computed as abundance-weighted average mass:
            m = self.elements.mtot() * (mass of 1 atomic mass unit).
            The "abundance-weighting" is as follows:
                m = sum_x(mx ax) / sum_x(ax), where ax = nx / nH, and x is any elem from self.elements.
                note: ax is related to abundance Ax via Ax = 12 + log10(ax).
            see help(self.elements.mtot) for more details, including a proof that mtot = rtot / ntot.
        if Element or Specie, return fluid.m, converted from [amu] to self.units unit system.
        '''
        f = self.fluid
        if f is SINGLE_FLUID:
            m_amu = super().get_m()
        else:
            m_amu = f.m * self.u('amu')
        return xr.DataArray(m_amu, attrs=self.units_meta())

    @known_var(load_across_dims=['fluid'])  # [TODO] deps
    def get_r(self):
        '''mass density.
        if SINGLE_FLUID, r directly from Bifrost;
        if Element, r inferred from SINGLE_FLUID r and abundances;
        if Species, r = n * m.
        '''
        # [TODO][EFF] improve efficiency by allowing to group species, e.g. via Partition();
        #    self('n') * self('m') will get a good speedup if grouped instead of load_across_dims.
        f = self.fluid
        if f is SINGLE_FLUID:
            return super().get_r()
        elif isinstance(f, Element):
            return self('r_elem')
        elif isinstance(f, Specie):
            return self('n') * self('m')
        raise LoadingNotImplementedError(f'{type(self).__name__}.get_r() for fluid of type {type(f)}')


    # # # N_MODE DISPATCH / CODE ARCHITECTURE # # #
    cls_behavior_attrs.register('n_mode', 'ne_mode')

    N_MODE_OPTIONS = {
        'best': '''use best mode available, based on fluid:
            electron --> 'table'
            Specie --> 'saha'.''',
        'elem': '''n for fluid's Element, from abundances and SINGLE_FLUID r.
            (crash if fluid.get_element() fails)''',
        'saha': '''from n_elem & saha ionization equation, assuming n=0 for twice+ ionized species.
            (crash if not Specie)''',
        'table': '''infer from EOS table, using SINGLE_FLUID r and e.
            (crash if not electron)''',
        'QN': '''sum of qi ni across self.fluids; getting 'ne' for saha via 'best' method.
            (crash if not electron)''',
        'QN_table': '''sum of qi ni across self.fluids; getting 'ne' for saha via 'table' method.
            (crash if not electron)''',
    }

    n_mode = simple_property('_n_mode', default='best', validate_from='N_MODE_OPTIONS',
        doc='''str. mode for getting Specie densities. (ignored if fluid is SINGLE_FLUID or an Element)
        see N_MODE_OPTIONS for details about available options.
        Note that you can always calculate n using a specific formula with the appropriate var,
            regardless of n_mode. E.g. n_saha will always load value from saha.
        Note: if ne_mode is not None, override n_mode with ne_mode when getting n for electrons.''')

    NE_MODE_OPTIONS = {
        None: '''use n_mode for electrons instead of ne_mode.''',
        'best': '''equivalent to table. Subclass might override.''',
        'table': '''infer from EOS table, using SINGLE_FLUID r and e.''',
        'QN': '''sum of qi ni across self.fluids; getting 'ne' for saha via 'best' method.''',
        'QN_table': '''sum of qi ni across self.fluids; getting 'ne' for saha via 'table' method.''',
    }
    
    ne_mode = simple_property('_ne_mode', default=None, validate_from='NE_MODE_OPTIONS',
        doc='''None or str. mode for getting electron number density. See NE_MODE_OPTIONS for details.''')

    ne_mode_explicit = alias('ne_mode', doc='''explicit ne_mode: ne_mode if not None, else n_mode.''')
    @ne_mode_explicit.getter
    def ne_mode_explicit(self):
        '''return ne_mode if set, else n_mode for electrons.'''
        ne_mode = self.ne_mode
        return self.n_mode if ne_mode is None else ne_mode

    # # # GENERIC NUMBER DENSITY # # #
    @known_var(load_across_dims=['fluid'])
    def get_ntype(self):
        '''ntype of self.fluid. Result depends on fluid as well as self.n_mode (and ne_mode if electron).
        See self.N_MODE_OPTIONS and self.NE_MODE_OPTIONS for options.
            'SINGLE_FLUID' <--> n for SINGLE_FLUID
            'elem' <--> n for Element
            'saha' <--> n from saha equation. (not available for electrons)
            'table' <--> n from EOS table. (only available for electrons)
            'QN_table' <--> n from sum of qi ni across self.fluids, with ne from table.
            'nan' <--> nan or crash, depending on self.typevar_crash_if_nan.
        '''
        result = 'nan'  # <-- nan unless set to something else below
        f = self.fluid
        if f is SINGLE_FLUID:
            result = 'SINGLE_FLUID'
        elif isinstance(f, Element):
            result = 'elem'
        elif isinstance(f, Specie):
            electron = f.is_electron()
            mode = self.ne_mode_explicit if electron else self.n_mode
            if mode == 'elem' and f.element is not None:
                result = 'elem'
            elif (not electron) and ((mode == 'best') or (mode == 'saha')):
                result = 'saha'
            elif electron:
                if (mode == 'table') or (mode == 'best'):
                    result = 'table'
                elif (mode == 'QN_table') or (mode == 'QN'):
                    result = 'QN_table'
        if result == 'nan':
            self._handle_typevar_nan(errmsg=f"ntype, when fluid={self.fluid!r}, n_mode={self.n_mode!r}.")
        return xr.DataArray(result)

    # some (but not all) of the vars associated with ntypes.
    #   the types not included here are those with a more complicated dependency,
    #   e.g. when ntype=='QN_table' we need to do self('ne_QN', ne_mode='table').
    NTYPE_TO_VAR = {  # used in self.get_n. Subclass might copy this dict and add or adjust types.
        'elem': 'n_elem',
        'saha': 'n_saha',
        'table': 'ne_fromtable',
        'nan': 'nan',
    }
    # non-simple deps based on ntype. Subclass might copy this dict and add or adjust types.
    #   "simple" dep if it is already described by NTYPE_TO_VAR.
    _NTYPE_TO_NONSIMPLE_DEPS = {
        'SINGLE_FLUID': ['SF_r', 'SF_m'],
        'QN_table': ['ne_QN', 'ne_fromtable'],
    }
    # all deps based on ntype. combination of NTYPE_TO_VAR and _NTYPE_TO_NONSIMPLE_DEPS.
    #   subclass might add new ntypes by adjusting those,
    #   or adjust the _NTYPE_TO_DEPS property to add an even-more-complicated dependency if needed.
    _NTYPE_TO_DEPS = property(lambda self: {**self.NTYPE_TO_VAR, **self._NTYPE_TO_NONSIMPLE_DEPS},
        doc='''all deps based on ntype. combination of NTYPE_TO_VAR and _NTYPE_TO_NONSIMPLE_DEPS.''')

    @known_var(partition_across_dim=('fluid', 'ntype'), partition_deps='_NTYPE_TO_DEPS')
    def get_n(self, *, ntype):
        '''number density. Formula depends on fluid:
        if SINGLE_FLUID, n = (r / m), from SINGLE_FLUID r & m.
            default m is the abundance-weighted average particle mass; see help(self.get_m) for details.
        if Element, n = (r / m), where
            r is inferred from abundances combined with SINGLE_FLUID r, and
            m is element particle mass (fluid.m)
        if Specie, n depends on ntype, determined from self.n_mode (and self.ne_mode, if electron);
            see help(self.get_ntype) for details.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if ntype in self.NTYPE_TO_VAR:
            var = self.NTYPE_TO_VAR[ntype]
            return self(var)
        elif ntype == 'SINGLE_FLUID':
            if self.current_n_fluid() > 1:
                raise LoadingNotImplementedError('[TODO] get_n with multiple SINGLE_FLUID...')
            with self.using(fluid=SINGLE_FLUID):
                return super().get_n()
        elif ntype == 'QN_table':
            return self('ne_QN', ne_mode='table')
        raise LoadingNotImplementedError(f'{type(self).__name__}.get_n() when ntype={ntype!r}.')


    # # # NTYPE: ELEM # # #

    @known_var(load_across_dims=['fluid'], aliases=['r_elem_per_rtot'])
    def get_rfrac_elem(self):
        '''mass density of element(s) for self.fluid, divided by total mass density.'''
        f = self.fluid
        if f is SINGLE_FLUID:
            return xr.DataArray(1)
        elif isinstance(f, (Element, Specie)):
            return xr.DataArray(f.get_element().r_per_nH() / self.elements.rtot_per_nH())
        else:
            raise NotImplementedError(f'fluid of type {type(f)} not yet supported for get_rfrac_elem')

    @known_var(load_across_dims=['fluid'], aliases=['n_elem_per_ntot'])
    def get_nfrac_elem(self):
        '''number density of element(s) for self.fluid, divided by total number density.'''
        f = self.fluid
        if f is SINGLE_FLUID:
            return xr.DataArray(1)
        elif isinstance(f, (Element, Specie)):
            return xr.DataArray(f.get_element().n_per_nH() / self.elements.ntot_per_nH())
        else:
            raise NotImplementedError(f'fluid of type {type(f)} not yet supported for get_nfrac_elem')

    @known_var(deps=['rfrac_elem', 'SF_r'])
    def get_r_elem(self):
        '''mass density of element(s) for self.fluid. r_elem = rfrac_elem * SF_r.'''
        return self('rfrac_elem') * self('SF_r')

    @known_var(deps=['nfrac_elem', 'SF_n'])
    def get_n_elem(self):
        '''number density of element(s) for self.fluid. n_elem = nfrac_elem * SF_n.'''
        return self('nfrac_elem') * self('SF_n')


    # # # NTYPE: SAHA # # #
    # (n_saha defined in MhdMultifluidIonizationLoader)


    # # # NTYPE: ELECTRONS # # #
    @known_var(deps=['ntype'], ignores_dims=['fluid'])
    def get_ne_type(self):
        '''ne_type. Result depends on self.ne_mode.
        Possibilities include 'table', 'QN_table'. See help(self.get_ntype) for details.
        '''
        electron = self.fluids.get_electron()
        return self('ntype', fluid=electron)

    _NE_TYPE_TO_DEPS = {
        'table': ['ne_fromtable'],
        'QN_table': ['ne_QN', 'ne_fromtable'],
    }

    @known_var(value_deps=[('ne_type', '_NE_TYPE_TO_DEPS')])
    def get_ne(self):
        '''electron number density. Result depends on self.ne_mode.
        See self.NE_MODE_OPTIONS for details.
        '''
        kind = self('ne_type').item()
        if kind == 'table':
            result = self('ne_fromtable')
        elif kind == 'QN_table':
            result = self('ne_QN', ne_mode='table')
        elif kind == 'nan':
            return self._assign_electron_fluid_coord_if_unambiguous(self('nan'))
        else:
            errmsg = f'{type(self).__name__}.get_ne() when ne_mode={self.ne_mode_explicit!r}'
            raise LoadingNotImplementedError(errmsg)
        return result

    def _assign_electron_fluid_coord_if_unambiguous(self, array):
        '''return self.assign_fluid_coord(array, electron fluid).
        if self doesn't have exactly 1 electron fluid, don't assign coord.
        '''
        try:
            electron = self.fluids.get_electron()
        except FluidValueError:
            return array
        # else
        return self.assign_fluid_coord(array, electron, overwrite=True)

    @known_var(deps=['n', 'q'], ignores_dims=['fluid'])
    def get_ne_QN(self):
        '''electron number density, assuming quasineutrality.
        result is sum_i qi ni / |qe|, with sum across all ions i in self.fluids.
        (Comes from assuming sum_s qs ns = 0, with sum across all species s in self.fluids.)
        '''
        ions = self.fluids.ions()
        if 'QN' in self.ne_mode_explicit:
            errmsg = (f"cannot get 'ne_QN' when ne_mode (={self.ne_mode_explicit!r}) still implies QN;\n"
                      "need a non-QN way to get ne for saha. See self.NE_MODE_OPTIONS for options.")
            raise FormulaMissingError(errmsg)
        ni = self('n', fluid=ions)  # <-- internally, ne for saha determined by self.ne_mode.
        Zi = self('q', fluid=ions) / self.u('qe')  # Zi = qi / |qe|
        result = Zi * ni
        result = xarray_promote_dim(result, 'fluid').sum('fluid')
        return self._assign_electron_fluid_coord_if_unambiguous(result)

    @known_var(deps=['SF_e', 'SF_r'], ignores_dims=['fluid'])
    def get_ne_fromtable(self):
        '''electron number density, from plugging r and e into eos tables (see self.tabin).'''
        result = super().get_ne_fromtable()  # see MhdEosLoader
        return self._assign_electron_fluid_coord_if_unambiguous(result)


    # # # --- SETTING VALUES; KNOWN SETTERS --- # # #
    # used when using set_var.

    @known_setter
    def set_n(self, value, **kw):
        '''set n to this value. n = number density.'''
        fluids = self.fluid_list()
        if all(f is SINGLE_FLUID for f in fluids):
            super().set_n(value, **kw)
        relevant = ['snap', 'fluid']
        if not all((f is SINGLE_FLUID) or isinstance(f, Element) for f in fluids):
            relevant.append('n_mode')
            if not self.n_mode == 'elem':  # [TODO] any other cases where n doesn't depend on ne_mode?
                relevant.append('ne_mode')
        return self.set_var_internal('n', value, relevant, **kw, ukey='number_density')
