"""
File Purpose: The main calculator class for multifluid analysis from single-fluid mhd,
for hookups to inherit from.
"""

from .mhd_multifluid_bases import MhdMultifluidBasesLoader
from .mhd_multifluid_densities import MhdMultifluidDensityLoader
from .mhd_multifluid_ionization import MhdMultifluidIonizationLoader
from ..elements import ElementList
from ..mhd_calculator import MhdCalculator
from ...plasma_calculator import MultifluidPlasmaCalculator

class MhdMultifluidCalculator(MhdMultifluidDensityLoader, MhdMultifluidIonizationLoader,
                              MhdMultifluidBasesLoader, MultifluidPlasmaCalculator,
                              MhdCalculator):
    '''class for multi-fluid analysis of single-fluid MHD outputs.

    set self.fluid=SINGLE_FLUID to get single-fluid values,
        otherwise will get inferred multifluid values.

    Not intended for direct instantiation. Instead, see options in the "hookups" subpackage,
        or write your own hookup for a different type of input, following the examples there.
    '''
    # parent class ordering notes:
    # - MhdMultifluidIonizationLoader must go before MhdMultifluidBasesLoader,
    #     because MhdMultifluidBasesLoader parent BasesLoader defines get_ionfrac too;
    #     this affects known_var results... (maybe it's a bug in known_var code?)
    #     with this ordering, KNOWN_VARS['ionfrac'].cls_where_defined is MhdMultifluidIonizationLoader;
    #     without this ordering, it is BasesLoader instead, which gives wrong deps.

    # # # ELEMENTS # # #
    element_list_cls = ElementList

    @property
    def elements(self):
        '''ElementList of unique elements found in any of self.fluids.
        To alter self.elements, adjust self.fluids; will infer new self.elements automatically.
        '''
        return self.element_list_cls.unique_from_element_havers(self.fluids, istart=0)

    # # # COLLISIONS # # #
    # aliases to check during set_collisions_crosstab_defaults
    #    (which gets called the first time self.collisions_cross_mapping is accessed).
    # override from super() to avoid 'H' and 'He' aliases to avoid ambiguity with Element fluids.
    _COLLISIONS_CROSSTAB_DEFAULT_FLUIDS_ALIASES = \
        MultifluidPlasmaCalculator._COLLISIONS_CROSSTAB_DEFAULT_FLUIDS_ALIASES.copy()
    _COLLISIONS_CROSSTAB_DEFAULT_FLUIDS_ALIASES.update({
        'H_I'   : ['H_I',    'H I'],  # excludes 'H', since 'H' might be an Element.
        'He_I'  : ['He_I',   'He I'], # excludes 'He', since 'He' might be an Element.
        })

    # note: lots of other functionality inherited from parents.
