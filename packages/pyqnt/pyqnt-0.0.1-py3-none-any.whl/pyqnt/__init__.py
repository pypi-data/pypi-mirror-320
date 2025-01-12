"""PyQnt: A Python library for quantitative finance.

This module provides tools for fetching historical data and portfolio management.
"""

import inspect
from .data import *
from .quant import *

# Dynamically generate __all__ based on functions and classes in submodules
__all__ = [
    name for name, obj in locals().items()
    if not name.startswith("_") and (inspect.isfunction(obj) or inspect.isclass(obj))
]

# Version of the package
__version__ = "0.0.1"