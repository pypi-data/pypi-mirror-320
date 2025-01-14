# gtus/__init__.py
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# You can also import your classes or functions here
from .core import GTUS, AsyncGTUS  # Import your classes for easy access

__version__ = "0.1.0"

__all__ = ["GTUS"]  