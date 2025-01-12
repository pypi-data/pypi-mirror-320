
# Import everything from the Pybind11 extension
from .flatnav import *  

# Expose DataType directly in the flatnav namespace
from .flatnav.data_type import DataType

# Expose the __version__ and __doc__ attributes directly in the flatnav namespace
from .flatnav import __version__
from .flatnav import __doc__

# Ensure the index submodule is accessible under flatnav.index
from .flatnav import index
