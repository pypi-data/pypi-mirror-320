"""
File Purpose: basic test for muram hookup in PlasmaCalcs.
These tests require the Header.NNN file(s), but not any simulation output data.
"""
import os
import pytest

import numpy as np

import PlasmaCalcs as pc

HERE = os.path.dirname(__file__)
RUNDIR = os.path.join(HERE, 'test_muram_nodata')


''' --------------------- basics --------------------- '''

def get_muram_calculator(**kw_init):
    '''make a muram calculator'''
    with pc.InDir(RUNDIR):
        mc = pc.MuramCalculator(**kw_init)
    return mc

def get_muram_multifluid_calculator(**kw_init):
    '''make a muram multifluid calculator'''
    with pc.InDir(RUNDIR):
        mm = pc.MuramMultifluidCalculator(**kw_init)
    return mm

def test_make_muram_calculator():
    '''ensure can make MuramCalculator and MuramMultifluidCalculator objects.'''
    mc = get_muram_calculator()
    mm = get_muram_multifluid_calculator()


''' --------------------- misc --------------------- '''

def test_muram_params():
    '''test some stuff about muram params'''
    mc = get_muram_calculator()
    mm = get_muram_multifluid_calculator()
    EXPECTED = {   # hard-coded some expected values
        'order': np.array([1, 2, 0]),
        'N0': 1152,
        'N1': 512,
        'N2': 256,
        'Nx': 512,
        'Ny': 256,
        'Nz': 1152,
        'dx': 19200000.0,
        'dy': 19200000.0,
        'dz': 6400000.0,
        't': 49926.96,
        'snap_s': '557956',
    }
    for param, value in EXPECTED.items():
        assert np.all(mc.params[param] == value)
        assert np.all(mm.params[param] == value)

def test_muram_mixture():
    '''test some stuff about muram elements and species.'''
    mc = get_muram_calculator()
    mm = get_muram_multifluid_calculator()
    # check elements:
    ELEMENTS = ['H', 'He', 'C', 'N', 'O',
                'Ne', 'Na', 'Mg', 'Al', 'Si',
                'S', 'K', 'Ca', 'Cr', 'Fe', 'Ni']
    assert len(mc.elements) == len(ELEMENTS)
    assert len(mm.elements) == len(ELEMENTS)
    assert all(e == el for e, el in zip(mc.elements, ELEMENTS))
    assert all(e == el for e, el in zip(mm.elements, ELEMENTS))
    # check mass:
    assert mc('m') == mc.elements.mtot() * mc.u('amu')
    assert mm('SF_m') == mm.elements.mtot() * mm.u('amu') == mc('m')
    assert mm('SINGLE_FLUID_m') == mm('m', fluid=pc.SINGLE_FLUID) == mm('SF_m')
    # check species details:
    assert len(mm.fluid) == len(mm.fluids) # fluid=None by default
    assert len(mm.fluids.ions()) == len(mm.elements)  # once-ionized ion of each element
    assert all(f.q==1 for f in mm.fluids.ions())
    assert len(mm.fluids) == len(mm.elements) + 2  # 2= 1 electron, 1 neutral
    assert mm.fluid[0] == mm.fluids.get_electron()
    # check can get mass of species:
    mions = mm('m', fluid=mm.fluids.ions())
    assert mions.identical(mm('m', fluid=pc.SET_IONS))
    assert np.all(mions == [el.m * mm.u('amu') for el in mm.elements])
    mall = mm('m')
    assert mall.isel(fluid=0) == mm.u('me')
    # check can get charge of species:
    qall = mm('q')
    assert qall.isel(fluid=0) == -mm.u('qe')
    assert qall.isel(fluid=1) == 0  # fluid[1] is neutral in this case.
    #    ^ [TODO] maybe don't need to impose this; it's okay if muram changes this fact...
    assert np.all(qall.isel(fluid=slice(2, None)) == mm.u('qe'))
