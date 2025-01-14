"""
File Purpose: loading single-fluid Muram quantities related to Equation Of State (EOS).
"""
import os

from ...defaults import DEFAULTS
from ...errors import (
    LoadingNotImplementedError,
    InputError,
    SnapValueError,
)
from ...mhd import MhdEosLoader
from ...tools import (
    simple_property,
    UNSET,
)

''' --------------------- MuramEosLoader--------------------- '''

class MuramEosLoader(MhdEosLoader):
    '''single-fluid Bifrost quantities related to Equation of State (EOS): ne, T, P.

    The implementation here assumes tables available at table=self.tabin[var],
        for var='ne', 'T', or 'P', and each having a table.interp(r=r, e=e) method,
        which gives value of var in 'raw' units.
    '''

    # non-NEQ functionality is inherited from MhdEosLoader.
    # 'aux' functionality is implemented here: read directly from aux files.


    # # # EOS MODE DISPATCH # # #

    _VALID_EOS_MODES = ('ideal', 'table', 'aux')

    eos_mode = simple_property('_eos_mode', setdefaultvia='_default_eos_mode', validate_from='_VALID_EOS_MODES',
            doc='''mode for "Equation of State" related variables (ne, T, P).
            'ideal' --> treat as ideal gas. P = n kB T = (gamma - 1) e, and can't get ne.
            'table' --> plug r and e into tables (see self.tabin) to get ne, T, P.
            'aux' --> read directly from aux files for eosP, eosT, and eosne.''')

    def _all_eos_aux_files_exist(self):
        '''returns whether eos aux files (eosP, eosT, and eosne) exist for all snaps in self.'''
        try:
            loadable = self.directly_loadable_vars()
        except SnapValueError:
            return False  # [TODO] this is overly restrictive...
        else:
            return all(var in loadable for var in ('eosT', 'eosP', 'eosne'))

    def _default_eos_mode(self):
        '''default for how to handle "Equation of State" related variables (ne, T, P).
        (provides default value for self.eos_mode.)

        result will be 'aux' if files for 'eosT', 'eosP', and 'eosne' exist for each snap,
        else 'table' if 'tabparams.in' file exists,
        else 'ideal'.
        '''
        if self._all_eos_aux_files_exist():
            return 'aux'
        elif os.path.isfile(os.path.join(self.dirname, 'tabparams.in')):
            return 'table'
        else:
            return 'ideal'

    _EOS_MODE_TO_NE_DEPS = {**MhdEosLoader._EOS_MODE_TO_NE_DEPS, 'aux': 'ne_aux'}
    @known_var(attr_deps=[('eos_mode', '_EOS_MODE_TO_NE_DEPS')])
    def get_ne(self):
        '''electron number density. Depends on self.eos_mode; see help(type(self).eos_mode).
        'ideal' --> cannot get ne. Crash with FormulaMissingError.
        'table' --> ne from plugging r and e into EOS lookup tables (see self.tabin).
        'aux' --> ne from 'eosne' file.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if self.eos_mode == 'aux':
            return self('ne_aux')
        else:
            return super().get_ne()

    _EOS_MODE_TO_T_DEPS = {**MhdEosLoader._EOS_MODE_TO_T_DEPS, 'aux': 'T_aux'}
    @known_var(attr_deps=[('eos_mode', '_EOS_MODE_TO_T_DEPS')])
    def get_T(self):
        '''temperature. Depends on self.eos_mode; see help(type(self).eos_mode).
        'ideal' --> T from ideal gas law: P_ideal = n kB T_ideal --> T_ideal = P_ideal / (n kB).
        'table' --> T from plugging r and e into EOS lookup tables (see self.tabin).
        'aux' --> T from 'eosT' file.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if self.eos_mode == 'aux':
            return self('T_aux')
        else:
            return super().get_T()

    _EOS_MODE_TO_P_DEPS = {**MhdEosLoader._EOS_MODE_TO_P_DEPS, 'aux': 'P_aux'}
    @known_var(attr_deps=[('eos_mode', '_EOS_MODE_TO_P_DEPS')])
    def get_P(self):
        '''pressure. Depends on self.eos_mode; see help(type(self).eos_mode).
        'ideal' --> P from ideal gas law: P = (gamma - 1) e.
        'table' --> P from plugging r and e into EOS lookup tables (see self.tabin).
        'aux' --> P from 'eosP' file.
        '''
        __tracebackhide__ = DEFAULTS.TRACEBACKHIDE
        if self.eos_mode == 'aux':
            return self('P_aux')
        else:
            return super().get_P()


    # # # EOS == NEQ (NON-EQUILIBRIUM) # # #

    @known_var(dims=['snap'])
    def get_ne_aux(self):
        '''electron number density, from 'eosne' file.'''
        ufactor = self.u('n', convert_from='cgs')
        return self.load_maindims_var_across_dims('eosne', u=ufactor, dims=['snap'])

    @known_var(dims=['snap'])
    def get_T_aux(self):
        '''temperature, from 'eosT' file.'''
        # note: multifluid T_aux assumes same T for all fluids.
        return self.load_maindims_var_across_dims('eosT', u='K', dims=['snap'])

    @known_var(dims=['snap'])
    def get_P_aux(self):
        '''pressure, from 'eosP' file.'''
        ufactor = self.u('pressure', convert_from='cgs')
        return self.load_maindims_var_across_dims('eosP', u=ufactor, dims=['snap'])
