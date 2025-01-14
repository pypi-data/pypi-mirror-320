"""
Package Purpose: optional add-ons for PlasmaCalculators

[TODO] custom gettable vars (defined outside of PlasmaCalcs)?
[TODO] "load all addons" function; don't load until function called.
        this way, user could edit DEFAULTS before loading addons.
"""
# load all addon modules (allowing them to register_addon_loader if appropriate)
from . import tfbi

# create AddonLoader object with all loaded addon loaders
from . import addon_tools

class AddonLoader(*addon_tools.ADDON_LOADERS):
    '''loader for all (successfully) imported addons.'''
    pass
