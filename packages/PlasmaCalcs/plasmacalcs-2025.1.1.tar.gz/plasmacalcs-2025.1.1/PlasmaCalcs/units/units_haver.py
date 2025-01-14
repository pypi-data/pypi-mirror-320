"""
File Purpose: UnitsHaver
"""
import xarray as xr

from .units_manager import UnitsManager
from ..dimensions import BehaviorHaver
from ..tools import alias_child

class UnitsHaver(BehaviorHaver):
    '''has some unit-related methods. self.u manages the actual units.

    u: None or UnitsManager
        manages the units.
        if not None, set self.u = u
    units: None or str
        the current default unit system for outputs. E.g. 'si' or 'raw'.
        if not None, set self.units = units.

    self.units aliases to self.u.units.
        i.e., setting self.units sets self.u.units; getting self.units gets self.u.units.
    '''
    def __init__(self, u=None, units=None, **kw_super):
        if u is not None: self.u = u
        if units is not None: self.units = units
        super().__init__(**kw_super)

    @property
    def u(self):
        '''the current units manager for self.
        if not yet initialized, getting self.u will create (and store) a new UnitsManager().
        '''
        try:
            return self._u
        except AttributeError:
            self._u = UnitsManager()
            return self._u
    @u.setter
    def u(self, value):
        self._u = value

    cls_behavior_attrs.register('units')
    units = alias_child('u', 'units',
            doc='''the current unit system for self. E.g., 'si'. (this is an alias to self.u.units)''')

    def record_units(self, array):
        '''return array.assign_attrs(self.units_meta()).
        if array is not an xarray.DataArray, convert it first.
        '''
        if not isinstance(array, xr.DataArray):
            array = xr.DataArray(array)
        return array.assign_attrs(self.units_meta())

    def units_meta(self):
        '''return dict(units=self.units).'''
        return dict(units=self.units)


class CoordsUnitsHaver(UnitsHaver):
    '''UnitsHaver which allows to set separate units systems for coordinates and data.
    Expects coordinate-units-getting-calls to supply alt='coords' to self.u,
        otherwise will default to coords units being the same as self units.
    '''
    cls_behavior_attrs.register('coords_units')
    @property
    def coords_units(self):
        '''the current unit system for coordinates. E.g., 'si'.
        by default, will always equal self.units.
        However, setting value will set self.u.alts['coords'] = value.
        '''
        u = self.u
        return u.alts.get('coords', u.units)
    @coords_units.setter
    def coords_units(self, value):
        self.u.alts['coords'] = value
    @coords_units.deleter
    def coords_units(self):
        self.u.alts.pop('coords', None)  # None -> it's okay if coords_units didn't exist yet

    def units_meta(self):
        '''return dict(units=self.units). Also include coords_units if different.'''
        result = super().units_meta()
        if self.coords_units != self.units:
            result['coords_units'] = self.coords_units
        return result
