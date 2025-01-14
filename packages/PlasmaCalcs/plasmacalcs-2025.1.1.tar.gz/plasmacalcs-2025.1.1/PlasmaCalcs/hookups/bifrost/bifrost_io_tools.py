"""
File Purpose: misc. tools for reading directly from bifrost files
"""
import os
import re

import numpy as np

from ...errors import (
    FileAmbiguityError,
    FileContentsError,
    FileContentsConflictError,
)
from ...tools import (
    read_idl_params_file,
    alias_child, alias_key_of, weakref_property_simple,
)


''' --------------------- bifrost snapname_NNN.idl files --------------------- '''

def read_bifrost_snap_idl(filename, *, eval=True, strip_strs=True):
    '''Parse Bifrost snapname_NNN.idl file into a dictionary.

    filename: string
        file to read from.
    eval: bool, default True
        whether to attempt to evaluate the values,
        using ast.literal_eval (safer but less flexible than eval).
        False --> values will remain as strings.
        True --> try to evaluate values but use strings if evaluation fails.
            Also convert '.true.' and '.false.' to True and False, case-insensitively.
    strip_strs: bool, default True
        whether to strip whitespace from all string values in result, after eval.

    File formatting notes:
        - semicolons (;) are used for comments. (idl format)
        - ignore blank lines & lines that don't assign a variable (missing '=')
        - ignores all leading & trailing whitespace in vars & values.
        - might use '.true.' and '.false.' for booleans.
    '''
    result = read_idl_params_file(filename, eval=eval)
    if eval:
        # handle .true. and .false. conversions below. Other evals have already been handled^
        for key, value in result.items():
            if isinstance(value, str):
                lowered = value.lower()
                if lowered == '.true.':
                    result[key] = True
                elif lowered == '.false.':
                    result[key] = False
        # strip whitespace from string values in result
        if strip_strs:
            for key, value in result.items():
                if isinstance(value, str):
                    result[key] = value.strip()
    return result

def bifrost_snap_idl_files(snapname, *, dir=os.curdir, abspath=False):
    '''return list of all bifrost snapname_NNN.idl files in directory.
    Sorts by snap number.

    snapname: str. match snapname_NNN.idl. (NNN can be any integer, doesn't need to be 3 digits.)
    abspath: bool. whether to return absolute paths or just the file basenames within directory.
    '''
    pattern = rf'{snapname}_([0-9]+)[.]idl'
    result = []
    for f in os.listdir(dir):
        match = re.fullmatch(pattern, f)
        if match is not None:
            snap_number = int(match.group(1))
            result.append((snap_number, f))
    result.sort()
    result = [f for (n, f) in result]
    if abspath:
        absdir = os.path.abspath(dir)
        result = [os.path.join(absdir, f) for f in result]
    return result

def bifrost_infer_snapname_here(dir=os.curdir):
    '''infer snapname based on files in directory, if possible.
    For files like snapname_NNN.idl, if all have same snapname, return it.
    If no such files, raise FileNotFoundError; if multiple implied snapnames, raise FileAmbiguityError.
    NNN can be any integer, doesn't need to be 3 digits.
    '''
    pattern = re.compile(r'(.+)_[0-9]+[.]idl')
    snapname = None
    for f in os.listdir(dir):
        match = pattern.fullmatch(f)
        if match is not None:
            if snapname is None:
                snapname = match.group(1)
            elif snapname != match.group(1):
                raise FileAmbiguityError(f'found different snapnames: {snapname!r}, {match.group(1)!r}')
    if snapname is None:
        raise FileNotFoundError(f'no files like "snapname_NNN.idl" found in directory: {dir!r}')
    return snapname


''' --------------------- bifrost mesh files --------------------- '''

def read_bifrost_meshfile(meshfile):
    '''returns dict of mesh coords from a Bifrost mesh file.

    Mesh file format looks like:
        x size (int)
        x coords
        x "down" coords
        dx values when taking "up derivative"
        dx values when taking "down derivative"
        then similar for y and z.

    The "down" and "up" refer to interpolation / staggering.

    result will have keys:
        x_size: int, number of points in x
        x: x coords list (as numpy array)
        x_down: x "down" coords
        dxup: dx when taking "up derivative"
        dxdn: dx when taking "down derivative"
    '''
    meshfile = os.path.abspath(meshfile)  # <-- makes error messages more verbose, if crash later.
    with open(meshfile, 'r') as f:
        lines = f.readlines()
    if len(lines) != 5 * len(('x', 'y', 'z')):
        raise FileContentsError(f'expected 5 lines per axis, got nlines={len(lines)}')
    result = {}
    x_to_lines = {'x': lines[:5], 'y': lines[5:10], 'z': lines[10:15]}
    for x, xlines in x_to_lines.items():
        result[f'{x}_size'] = int(xlines[0])
        result[x]           = np.array([float(s) for s in xlines[1].split()])
        result[f'{x}_down'] = np.array([float(s) for s in xlines[2].split()])
        result[f'{x}_ddup'] = np.array([float(s) for s in xlines[3].split()])
        result[f'{x}_dddn'] = np.array([float(s) for s in xlines[4].split()])
        # sanity checks:
        for key in [x, f'{x}_down', f'{x}_ddup', f'{x}_dddn']:
            if len(result[key]) != result[f'{x}_size']:
                raise FileContentsConflictError(f'length of {key!r} does not match {x}_size')
    return result


''' --------------------- BifrostVarPathsManager --------------------- '''

class BifrostVarPathsManager():
    '''manages filepaths (as abspaths) and readable vars for a BifrostSnap.
    self.kind2path = {kind: path}
    self.kind2vars = {kind: [list of readable vars]}
    self.var2kind = {var: kind}
    self.var2path = {var: path}
    self.path2kind = {path: kind}
    self.path2vars = {path: [list of readable vars]}
    self.var2index = {var: index of var in its path's list of vars}
    
    self.kinds: tuple of kinds with any vars in self.
    self.vars: tuple of all vars in self.
    self.paths: tuple of all paths with any vars in self.

    kinds are: 'snap', 'aux', 'hion', 'helium', 'ooe'.
    if kind has no vars, do not include it in results.

    snap: BifrostSnap
    bcalc: BifrostCalculator
    '''
    KINDS = ('snap', 'aux', 'hion', 'helium', 'ooe')

    def __init__(self, snap, bcalc):
        self.snap = snap
        self.bcalc = bcalc
        self.init_all()

    snap = weakref_property_simple('_snap')  # weakref --> snap caching paths manager would be fine.
    bcalc = weakref_property_simple('_bcalc')  # weakref --> bcalc caching paths manager would be fine.
    params = alias_child('snap', 'params')
    snapname = alias_key_of('params', 'snapname')
    NNN = property(lambda self: self.snap.file_s(self.bcalc),
            doc='''(str) the NNN part of the snapname_NNN.idl filename.''')
    snapdir = alias_child('bcalc', 'snapdir')

    def snappath(self, filename):
        '''returns os.path.join(self.snapdir, filename)'''
        return os.path.join(self.snapdir, filename)

    def init_all(self):
        '''init all KINDS in self.'''
        self.kind2path = dict()
        self.kind2vars = dict()
        self.var2kind = dict()
        self.var2path = dict()
        self.path2kind = dict()
        self.path2vars = dict()
        self.var2index = dict()
        self.init_snap_kind()
        self.init_aux_kind()
        self.init_hion_kind()
        self.init_helium_kind()
        self.init_ooe_kind()
        self.kinds = tuple(self.kind2vars.keys())
        self.vars = tuple(self.var2kind.keys())
        self.paths = tuple(self.path2vars.keys())

    def _init_kind_vars_path(self, kind, vars, path):
        '''updates self with corresponding kind, vars, and path.'''
        self.kind2vars[kind] = vars
        self.kind2path[kind] = path
        for var in vars:
            if var in self.var2kind:  # var not unique... crash!
                errmsg = f'{type(self).__name__} with multiple vars with same name: {var!r}'
                raise LoadingNotImplementedError(errmsg)
            self.var2kind[var] = kind
            self.var2path[var] = path
        self.path2kind[path] = kind
        self.path2vars[path] = vars
        self.var2index.update({var: i for i, var in enumerate(vars)})

    def init_snap_kind(self):
        '''vars stored in snapname_NNN.snap file.'''
        path = self.snappath(f'{self.snapname}_{self.NNN}.snap')
        if self.params.get('do_mhd', False):
            vars = ('r', 'px', 'py', 'pz', 'e', 'bx', 'by', 'bz')
        else:
            vars = ('r', 'px', 'py', 'pz', 'e')
        self._init_kind_vars_path('snap', vars, path)

    def init_aux_kind(self):
        '''vars stored in snapname_NNN.aux file.'''
        path = self.snappath(f'{self.snapname}_{self.NNN}.aux')
        vars = tuple(self.params.get('aux', '').split())
        if len(vars) > 0:
            self._init_kind_vars_path('aux', vars, path)

    def init_hion_kind(self):
        '''vars stored in snapname.hion_NNN.snap file.'''
        path = self.snappath(f'{self.snapname}.hion_{self.NNN}.snap')
        if self.params.get('do_hion', 0) > 0:
            vars = ('hionne', 'hiontg', 'n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'nh2')
            self._init_kind_vars_path('hion', vars, path)

    def init_helium_kind(self):
        '''vars stored in snapname.helium_NNN.snap file.'''
        path = self.snappath(f'{self.snapname}.helium_{self.NNN}.snap')
        if self.params.get('do_helium', 0) > 0:
            vars = ('nhe1', 'nhe2', 'nhe3')
            self._init_kind_vars_path('helium', vars, path)

    def init_ooe_kind(self):
        '''out of equilibrium vars.'''
        if self.params.get('do_out_of_eq', 0) > 0:
            pass
            #raise NotImplementedError('loading ooe vars. Got do_out_of_eq > 0')

    # # # DISPLAY # # #
    def __repr__(self):
        return f'{type(self).__name__}(vars={self.vars})'

    def help(self):
        '''print docstring of self...'''
        print(type(self).__doc__)
