"""
File Purpose: calculating plasma parameters, e.g. plasma beta, plasma frequency
"""

from .quantity_loader import QuantityLoader
from ..tools import xarray_sum

class PlasmaParametersLoader(QuantityLoader):
    '''plasma parameters, e.g. plasma beta, plasma frequency'''
    # # # PLASMA BETA # # #
    @known_var(deps=['P', 'mod_B'])
    def get_beta(self):
        '''plasma beta. beta = (pressure / magnetic pressure) = (P / (B^2 / (2 mu0)))'''
        return self('P') / (self('mod_B')**2 / (2 * self.u('mu0')))

    # # # GYROFREQUENCY # # #
    @known_var(deps=['q', 'mod_B', 'm'])
    def get_sgyrof(self):
        '''signed gyrofrequency. sgyrof == q |B| / m == charge * |B| / mass. Negative when charge < 0.'''
        return self('mod_B') * (self('q') / self('m'))
        # ^note: grouped (q/m) for efficiency (both are probably constant across maindims)
        #    and because both might be small numbers --> helps avoid getting close to float32 limits.

    @known_var(deps=['abs_sgyrof'], aliases=['cyclof', 'omega_c'])
    def get_gyrof(self):
        '''(unsigned) gyrofrequency. gyrof == |sgyrof| == |q| |B| / m == |charge| * |B| / mass.'''
        return self('abs_sgyrof')

    # # # MAGNETIZATION PARAMETER (KAPPA) # # #
    @known_var(deps=['nusn', 'sgyrof'])
    def get_skappa(self):
        '''signed kappa (magnetization parameter). skappa = sgyrof / nusn. Negative when charge < 0.
        skappa = gyrofrequency / collision frequency of self.fluid with neutrals.
        gyrofrequency == q * |B| / (mass * nusn). 
        ''' 
        return self('sgyrof') / self('nusn')

    @known_var(deps=['abs_skappa'])
    def get_kappa(self):
        '''(unsigned) kappa (magnetization parameter). kappa = |skappa| == |gyrof| / nusn.
        kappa = |gyrofrequency| / collision frequency of self.fluid with neutrals.
        '''
        return self('abs_skappa')

    # # # PLAMSA FREQUENCY # # #
    @known_var(deps=['n', 'abs_q', 'm'])
    def get_wplasma(self):
        '''"plasma frequency" for self.fluid. wplasma = sqrt(n q^2 / (m epsilon0))
        This is analogous to the "true" plasma frequency of Langmuir oscillations,
            which is calculated using the same formula but applied to electrons.
        wplasma is equivalent to wplasmae when self.fluid is electrons.
        '''
        return self('n')**0.5 * self('abs_q') / (self('m') * self.u('eps0'))**0.5

    @known_var(deps=['wplasma'], aliases=['wpe', 'omega_pe'], ignores_dims=['fluid'])
    def get_wplasmae(self):
        '''electron plasma frequency; Langmuir oscillations. wpe = sqrt(ne qe^2 / (me epsilon0))'''
        electron = self.fluid.get_electron()  # gets one and only electron fluid, or crashes if that's impossible.
        return self('wplasma', fluid=electron)

    # # # DEBYE LENGTH # # #
    @known_var(deps=['ldebye2'])
    def get_ldebye(self):
        '''Debye length (of self.fluid). ldebye = sqrt(epsilon0 kB T / (n q^2))'''
        return self('ldebye2')**0.5

    @known_var(deps=['Tjoule', 'n', 'abs_q'])
    def get_ldebye2(self):
        '''squared Debye length (of self.fluid). ldebye2 = epsilon0 kB T / (n q^2)'''
        return self.u('eps0') * self('Tjoule') / (self('n') * self('abs_q')**2)
        
    @known_var(deps=['ldebye2'], reduces_dims=['fluid'])
    def get_ldebye_subset(self):
        '''"total" Debye length; ldebye_subset = sqrt(epsilon0 kB / sum_fluids(n q^2 / T))
        sum is taken over the fluids in self.fluid.
        Equivalent: sqrt( 1 / sum_fluids(1/ldebye^2) )
        '''
        return xarray_sum(1/self('ldebye2'), dim='fluid')**-0.5

    @known_var(deps=['ldebye_subset'], ignores_dims=['fluid'])
    def get_ldebye_total(self):
        '''total Debye length for all fluids; ldebye_total = sqrt(epsilon0 kB / sum_fluids(n q^2 / T))
        sum is taken over all the fluids in self.fluids.
        Equivalent: sqrt( 1 / sum_fluids(1/ldebye^2) )
        '''
        return self('ldebye_subset', fluid=None)  # fluid=None --> use all fluids.

    # # # MEAN FREE PATH # # #
    @known_var(deps=['vtherm', 'nusn'], aliases=['lmfp'])
    def get_mean_free_path(self):
        '''collisional mean free path. lmfp = vtherm / nusn = thermal velocity / collision frequency.'''
        return self('vtherm') / self('nusn')

    # # # THERMAL VELOCITY # # #
    @known_var(deps=['Tjoule', 'm'], aliases=['vth', 'vthermal'])
    def get_vtherm(self):
        '''thermal velocity. vtherm = sqrt(kB T / m)'''
        return (self('Tjoule') / self('m'))**0.5

    @known_setter
    def set_vtherm(self, value, **kw):
        '''set thermal velocity, by setting T.
        vtherm = sqrt(kB T / m) --> set T to (m vtherm^2 / kB).
        '''
        T = self('m').values * value**2 / self.u('kB')
        self.set('T', T, **kw)

    # # # SOUND SPEED # # #
    @known_var(deps=['csound2'], aliases=['cs'])
    def get_csound(self):
        '''sound speed. csound = sqrt(gamma * P / r)'''
        return self('csound2')**0.5

    @known_var(deps=['gamma', 'P', 'r'], aliases=['cs2'])
    def get_csound2(self):
        '''sound speed squared. csound2 = gamma P / r.'''
        return self('gamma') * self('P') / self('r')

    # # # ALFVEN SPEED # # #
    @known_var(deps=['va2'], aliases=['va'])
    def get_valfven(self):
        '''Alfven speed. valfven = |B| / sqrt(mu0 * r)'''
        return self('va2')**0.5

    @known_var(deps=['mod2_B', 'r'], aliases=['va2'])
    def get_valfven2(self):
        '''Alfven speed squared. valfven2 = |B|^2 / (mu0 * r)'''
        return self('mod2_B') / (self.u('mu0') * self('r'))

    # # # ROSENBERG CRITERION # # #
    @known_var
    def get_rosenberg_qn(self):
        '''Rosenberg criterion for quasineutrality. rosenberg_qn = (nusn / wplasma)^2.
        quasineutrality is "reasonable" iff rosenberg_qn << 1.
        (Intuitively: quasineutrality reasonable iff 'collisions much slower than plasma oscillations')
        '''
        return self('nusn/wplasma')**2
