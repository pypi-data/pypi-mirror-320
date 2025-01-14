"""
File Purpose: electric field in Bifrost
"""
import numpy as np

from ...defaults import DEFAULTS
from ...dimensions import SINGLE_FLUID
from ...errors import FormulaMissingError
from ...quantities import QuantityLoader
from ...tools import UNSET


''' --------------------- BifrostEfieldLoader --------------------- '''

class BifrostEfieldLoader(QuantityLoader):
    '''quantities related to electric field in Bifrost'''
    @known_var(dims=['snap'])
    def get_qjoule(self):
        '''joule heating (?). eta * |J|**2. Directly from Bifrost aux.
        qjoule in aux is stored in raw units.
            for more aux units see: https://ita-solar.github.io/Bifrost/aux_variables/
        '''
        if 'qjoule' not in self.directly_loadable_vars():
            raise FormulaMissingError('qjoule when not saved to aux')
        ufactor = self.u('energy_density time-1', convert_from='raw')
        return self.load_maindims_var_across_dims('qjoule', u=ufactor, dims=['snap'])

    @known_var(deps=['qjoule', 'mod2_J'])
    def get_eta(self):
        '''eta (scalar), such that E = -u x B + eta J + ....'''
        return self('qjoule') / self('mod2_J')

    @known_var(dims=['snap'])
    def get_eta_hall(self):
        '''eta_hall (scalar), such that E = -u x B + eta_hall J x Bhat + ....
        eta_hall in aux is stored in raw(?) units ([TODO]-check!).
        '''
        if 'eta_hall' not in self.directly_loadable_vars():
            raise FormulaMissingError('eta_hall when not saved to aux')
        ufactor = self.u('e_field current_density-1', convert_from='raw')
        return self.load_maindims_var_across_dims('eta_hall', u=ufactor, dims=['snap'])

    @known_var(dims=['snap'])
    def get_eta_amb(self):
        '''eta_amb (scalar), such that E = -u x B - eta_amb (J x Bhat) x Bhat + ....
        eta_amb in aux is stored in raw(?) units ([TODO]-check!).
        '''
        if 'eta_amb' not in self.directly_loadable_vars():
            raise FormulaMissingError('eta_amb when not saved to aux')
        ufactor = self.u('e_field current_density-1', convert_from='raw')
        return self.load_maindims_var_across_dims('eta_amb', u=ufactor, dims=['snap'])

    @known_var(deps=['(SF_u)_cross_B'], aliases=['E_motional'])
    def get_E_uxB(self, *, _B=None):
        '''E_uxB = -u x B, the motional electric field. E = E_uxB + ...
        [EFF] for efficiency, can provide B if already known.
            CAUTION: if providing B, any missing components assumed to be 0.
        '''
        result = -self('(SF_u)_cross_B', _B=_B)
        # don't include fluid=SINGLE_FLUID in result.
        result = result.drop_vars('fluid')  # [TODO] handle 'fluid not in result coords' case?
        return result

    @known_var(deps=['eta', 'J'])
    def get_E_etaJ(self, *, _J=None):
        '''E_etaJ = eta * J. Goes into E = E_uxB + E_etaJ + ...
        [EFF] for efficiency, can provide J if already known.
        '''
        J = self('J') if _J is None else _J
        return self('eta') * J

    @known_var(deps=['eta_hall', 'J_cross_B'])
    def get_E_hall(self, *, _J=None, _B=None, _JxB=None, _mod_B=None):
        '''E_hall = eta_hall * J x B / |B|. Goes into E = E_uxB + E_hall + ...
        [EFF] for efficiency, can provide J, B, JxB, and/or _mod_B if already known.
            CAUTION: if providing vector, any missing components assumed to be 0.
        '''
        eta_hall = self('eta_hall')
        JxB = self('J_cross_B', _J=_J, _B=_B) if _JxB is None else _JxB
        mod_B = self('mod_B', _B=_B) if _mod_B is None else _mod_B
        return eta_hall * JxB / mod_B

    @known_var(deps=['eta_amb', 'J', 'B'])
    def get_E_amb(self, *, _J=None, _B=None, _JxB=None, _mod_B=None):
        '''E_amb = -eta_amb (J x B) x B / |B|**2. Goes into E = E_uxB + E_amb + ...
        [EFF] for efficiency, can provide J, B, JxB, and/or _mod_B if already known.
            CAUTION: if providing vector, any missing components assumed to be 0.
        '''
        eta_amb = self('eta_amb')
        JxB = self('J_cross_B', _J=_J, _B=_B) if _JxB is None else _JxB
        JxBxB = self('(J_cross_B)_cross_B', _val0=_JxB, _B=_B)
        mod_B = self('mod_B', _B=_B) if _mod_B is None else _mod_B
        return -eta_amb * JxBxB / mod_B**2

    @known_var(deps=['E_etaJ', 'E_hall', 'E_amb'])
    def get_E_u0(self, *, _J=None, _B=None, _JxB=None, _mod_B=None):
        '''E without motional electric field contribution. E_u0 = E_etaJ + E_hall + E_amb.
        [EFF] for efficiency, can provide J, B, JxB, and/or _mod_B if already known.
            CAUTION: if providing vector, any missing components assumed to be 0.
        '''
        with self.using(component=None):  # all 3 vector components here
            J = self('J') if _J is None else _J
            B = self('B') if _B is None else _B
            JxB = self('J_cross_B', _J=_J, _B=_B) if _JxB is None else _JxB
            mod_B = self('mod_B', _B=_B) if _mod_B is None else _mod_B
        E_etaJ = self('E_etaJ', _J=J)
        E_hall = self('E_hall', _J=J, _B=B, _JxB=JxB, _mod_B=mod_B)
        E_amb  = self('E_amb',  _J=J, _B=B, _JxB=JxB, _mod_B=mod_B)
        return E_etaJ + E_hall + E_amb

    @known_var(deps=['E_uxB', 'E_u0'])
    def get_E(self):
        '''electric field from Bifrost. E = E_uxB + E_u0.'''
        with self.using(component=None):  # all 3 vector components here
            B = self('B')
        E_uxB = self('E_uxB', _B=B)
        E_u0  = self('E_u0',  _B=B)
        return E_uxB + E_u0

    @known_var(attr_deps=[('E_un0_type', '_E_UN0_TYPE_TO_DEPS')])
    def get_E_un0(self):
        '''electric field in u_n=0 frame.
        Result depends on self.E_un0_mode; see help(type(self).E_un0_mode) for details.
        Note: using E_un0_mode=None (the default) and self.assume_un='u',
            is equivalent to using E_un0_mode = 'un=u', which will just give self('E_u0').
        Else, E_un0 = E + u_n x B, if can get u_n (crash if can't get u_n).
        '''
        if self.E_un0_type == 'E+unxB':  # slightly more helpful error than super(); u_neutral will probably crash.
            try:
                un = self('u_neutral', component=None)  # check if can get u_n... probably cant...
            except NotImplementedError:
                errmsg = 'E_un0, when E_un0_mode=None, u_neutral unknown, and self.assume_un != "u".'
                raise FormulaMissingError(errmsg)
            else:
                result = self('E')
                if np.any(un != 0):
                    result = result + self('u_neutral_cross_B', _u_neutral=un)
        else:
            result = super().get_E_un0()
        return result

    @property
    def E_un0_type(self):
        '''string telling method that will be used to get E_un0. Based on self.E_un0_mode and assume_un.
        possible results:
            'nan' <--> will crash. (e.g. this occurs if E_un0_mode = 'E0_perpmodB_min')
            'E+unxB' <--> self('E') + self('u_neutral_cross_B')
            'E_u0' <--> self('E_u0')
            'E+uxB' <--> self('E') + self('u_cross_B')
            'E' <--> self('E')
            'E0_perpB' <--> self('E0_un0_perpB')
        '''
        if self.E_un0_mode is None and self.assume_un == 'u':
            return 'E_u0'
        else:
            return super().E_un0_type
