"""
File Purpose: calculating plasma heating, e.g. equilibrium T from E & collisions
"""

from .plasma_parameters import PlasmaParametersLoader


class PlasmaHeatingLoader(PlasmaParametersLoader):
    '''plasma heating. See help(self.get_Eheat) for more details.'''
    @known_var(deps=['m_n', 'skappa', 'mod_B', 'u_n'])
    def get_Eheat_perp_coeff(self, *, _Eheat_par_coeff=None):
        '''Eheat_perp = Eheat_perp_coeff * |E_perp|^2. for E heating perp to B. Units of Kelvin.
        see help(self.get_Eheat) for more details.

        [EFF] for efficiency, can provide _Eheat_par_coeff if known.
        '''
        Eheat_par_coeff = self('Eheat_par_coeff') if _Eheat_par_coeff is None else _Eheat_par_coeff
        return Eheat_par_coeff / (1 + self('skappa')**2)

    @known_var(deps=['m_n', 'skappa', 'mod_B', 'u_n'])
    def get_Eheat_par_coeff(self):
        '''Eheat_par = Eheat_par_coeff * |E_par|^2. for E heating parallel to B. Units of Kelvin.
        see help(self.get_Eheat) for more details.
        '''
        return (self('m_n') / (3 * self.u('kB'))) * (self('skappa')**2 / self('mod2_B'))

    @known_var(deps=['Eheat_perp_coeff', 'E_perpmag_B'])
    def get_Eheat_perp(self, *, _E_un0=None, _B=None, _Eheat_par_coeff=None):
        '''Eheat_perp = Eheat_perp_coeff * |E_perp|^2. heating perp to B. Units of Kelvin.
        see help(self.get_Eheat) for more details.

        [EFF] for efficiency, can provide _E_un0, _B and/or _Eheat_par_coeff if known.
            caution: if providing _E_un0 or _B, will assume any missing components are 0.
        '''
        perp_coeff = self('Eheat_perp_coeff', _Eheat_par_coeff=_Eheat_par_coeff)
        return perp_coeff * self('E_un0_perpmag_B', _E_un0=_E_un0, _B=_B)**2

    @known_var(deps=['Eheat_par_coeff', 'E_parmag_B'])
    def get_Eheat_par(self, *, _E_un0=None, _B=None, _Eheat_par_coeff=None):
        '''Eheat_par = Eheat_par_coeff * |E_par|^2. heating parallel to B. Units of Kelvin.
        see help(self.get_Eheat) for more details.

        [EFF] for efficiency, can provide _E_un0, _B and/or _Eheat_par_coeff if known.
            caution: if providing _E_un0 or _B, will assume any missing components are 0.
        '''
        par_coeff = self('Eheat_par_coeff') if _Eheat_par_coeff is None else _Eheat_par_coeff
        return par_coeff * self('E_un0_parmag_B', _E_un0=_E_un0, _B=_B)**2

    @known_var(deps=['Eheat_perp', 'Eheat_par'])
    def get_Eheat(self):
        '''Eheat = Eheat_perp + Eheat_par. total heating from electric field. Units of Kelvin.
        
        From assuming u_n=0 and derivatives=0 in heating & momentum equations, which yields:
            T_s = T_n + Eheat_perp + Eheat_par, where
                Eheat_perp = Eheat_perp_coeff * |E_perp|^2,
                Eheat_par  = Eheat_par_coeff * |E_par|^2,
                E_perp = E(in u_n=0 frame) perp to B,
                E_par  = E(in u_n=0 frame) parallel to B,
                Eheat_perp_coeff = (m_n / (3 kB)) (kappa_s^2 / B^2) * (1 / (1 + kappa_s^2)),
                Eheat_par_coeff  = (m_n / (3 kB)) (kappa_s^2 / B^2).
        '''
        with self.using(component=None):  # all 3 vector components
            E_un0 = self('E_un0')
            B = self('B')
            Eheat_par_coeff = self('Eheat_par_coeff')
        Eheat_perp = self('Eheat_perp', _E_un0=E_un0, _B=B, _Eheat_par_coeff=Eheat_par_coeff)
        Eheat_par = self('Eheat_par', _E_un0=E_un0, _B=B, _Eheat_par_coeff=Eheat_par_coeff)
        return Eheat_perp + Eheat_par


    # # # PLASMA PARAMETERS AFFECTED BY HEATING # # #

    @known_var(deps=['Eheat', 'T_n'])
    def get_T_from_Eheat(self):
        '''T_from_Eheat = T_n + Eheat. Units of Kelvin.
        see help(self.get_Eheat) for more details.
        '''
        return self('T_n') + self('Eheat')

    @known_var(deps=['Eheat_perp', 'T_n'])
    def get_T_from_Eheat_perp(self):
        '''T_from_Eheat_perp = T_n + Eheat_perp. Units of Kelvin.
        see help(self.get_Eheat) for more details.
        '''
        return self('T_n') + self('Eheat_perp')

    @known_var(deps=['eqperp_ldebye2'])
    def get_eqperp_ldebye(self):
        '''Debye length (of self.fluid), using T_from_Eheat_perp instead of T.
        eqperp_ldebye = sqrt(epsilon0 kB T_from_Eheat_perp / (n q^2))
        '''
        return self('eqperp_ldebye2')**0.5

    @known_var(deps=['T_from_Eheat_perp', 'n', 'abs_q'])
    def get_eqperp_ldebye2(self):
        '''squared Debye length (of self.fluid), using Eheat_perp instead of T.
        eqperp_ldebye2 = epsilon0 kB T_from_Eheat_perp / (n q^2)
        '''
        T = self('T_from_Eheat_perp')
        return self.u('eps0') * self.u('kB') * T / (self('n') * self('abs_q')**2)

    @known_var(deps=['T_from_Eheat_perp', 'm'])
    def get_eqperp_vtherm(self):
        '''thermal velocity, using T_from_Eheat_perp instead of T.
        eqperp_vtherm = sqrt(kB T_from_Eheat_perp / m)
        '''
        T = self('T_from_Eheat_perp')
        return (T * (self.u('kB') / self('m')))**0.5

    @known_var(deps=['eqperp_vtherm', 'nusn'], aliases=['eqperp_lmfp'])
    def get_eqperp_mean_free_path(self):
        '''collisional mean free path, using eqperp_vtherm instead of vtherm.
        eqperp_lmfp = eqperp_vtherm / nusn
        '''
        return self('eqperp_vtherm') / self('nusn')
