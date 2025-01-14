"""
File Purpose: loading single-fluid Bifrost quantities related to Equation Of State (EOS).
"""
import numpy as np

from ...defaults import DEFAULTS
from ...errors import (
    LoadingNotImplementedError,
    InputError,
)
from ...mhd import MhdEosLoader
from ...tools import (
    simple_property,
    UNSET,
)

''' --------------------- BifrostEosLoader--------------------- '''

class BifrostEosLoader(MhdEosLoader):
    '''single-fluid Bifrost quantities related to Equation of State (EOS): ne, T, P.

    The implementation here assumes tables available at table=self.tabin[var],
        for var='ne', 'T', or 'P', and each having a table.interp(r=r, e=e) method,
        which gives value of var in 'raw' units.
    '''

    # non-NEQ functionality is inherited from MhdEosLoader.
    # NEQ ("nonequilibrium") functionality is implemented here.


    # # # EOS MODE DISPATCH # # #

    _VALID_EOS_MODES = ('ideal', 'table', 'neq')

    eos_mode = simple_property('_eos_mode', setdefaultvia='eos_mode_sim', validate_from='_VALID_EOS_MODES',
            doc='''mode for "Equation of State" related variables (ne, T, P).
            'ideal' --> treat as ideal gas. P = n kB T = (gamma - 1) e, and can't get ne.
            'table' --> plug r and e into tables (see self.tabin) to get ne, T, P.
            'neq' --> non-equilibrium ionization for H (possibly also for He too):
                       ne and T from hionne and hiontg (from aux). P from table, r, and e.''')

    def eos_mode_sim(self):
        '''how simulation handled "Equation of State" related variables (ne, T, P).
        (provides default value for self.eos_mode.)

        'ideal' --> treated as ideal gas: P = n kB T = (gamma - 1) e.
            ne not available.
        'table' --> plugged into EOS lookup tables (see self.tabin)
            plug r and e into tables to get ne, T, P.
        'neq' --> non-equilibrium ionization for H (possibly also for He too):
            ne and T from hionne and hiontg (from aux). P from table, r, and e.
        '''
        if 'tabinputfile' not in self.params:
            return 'ideal'
        elif self.params.get('do_hion', False):
            return 'neq'
        else:
            return 'table'

    _EOS_MODE_TO_NE_DEPS = {**MhdEosLoader._EOS_MODE_TO_NE_DEPS, 'neq': 'ne_neq'}
    @known_var(attr_deps=[('eos_mode', '_EOS_MODE_TO_NE_DEPS')])
    def get_ne(self):
        '''electron number density. Depends on self.eos_mode; see help(type(self).eos_mode).
        'ideal' --> cannot get ne. Crash with FormulaMissingError.
        'table' --> ne from plugging r and e into EOS lookup tables (see self.tabin).
        'neq' --> ne from 'hionne' from aux.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if self.eos_mode == 'neq':
            return self('ne_neq')
        else:
            return super().get_ne()

    _EOS_MODE_TO_T_DEPS = {**MhdEosLoader._EOS_MODE_TO_T_DEPS, 'neq': 'T_neq'}
    @known_var(attr_deps=[('eos_mode', '_EOS_MODE_TO_T_DEPS')])
    def get_T(self):
        '''temperature. Depends on self.eos_mode; see help(type(self).eos_mode).
        'ideal' --> T from ideal gas law: P_ideal = n kB T_ideal --> T_ideal = P_ideal / (n kB).
        'table' --> T from plugging r and e into EOS lookup tables (see self.tabin).
        'neq' --> T from 'hiontg' from aux.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if self.eos_mode == 'neq':
            return self('T_neq')
        else:
            return super().get_T()

    _EOS_MODE_TO_P_DEPS = {**MhdEosLoader._EOS_MODE_TO_P_DEPS, 'neq': 'P_fromtable'}
    @known_var(attr_deps=[('eos_mode', '_EOS_MODE_TO_P_DEPS')])
    def get_P(self):
        '''pressure. Depends on self.eos_mode; see help(type(self).eos_mode).
        'ideal' --> P from ideal gas law: P = (gamma - 1) e.
        'table' --> P from plugging r and e into EOS lookup tables (see self.tabin).
        'neq' --> P from table, r, and e. (Even in neq mode, P still comes from table.)
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if self.eos_mode == 'neq':
            return self('P_fromtable')
        else:
            return super().get_P()


    # # # EOS == NEQ (NON-EQUILIBRIUM) # # #

    @known_var(dims=['snap'])
    def get_ne_neq(self):
        '''electron number density, from 'hionne' in aux.
        hionne in aux is stored in cgs units.
        '''
        ufactor = self.u('n', convert_from='cgs')
        return self.load_maindims_var_across_dims('hionne', u=ufactor, dims=['snap'])

    @known_var(dims=['snap'])
    def get_T_neq(self):
        '''temperature, from 'hiontg' in aux.
        hiontg in aux is stored in [K] units.
        '''
        # note: multifluid T_neq assumes same T for all fluids.
        return self.load_maindims_var_across_dims('hiontg', u='K', dims=['snap'])
