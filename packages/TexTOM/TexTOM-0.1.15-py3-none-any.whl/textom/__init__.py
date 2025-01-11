# textom/__init__.py
import pkgutil
import importlib
from pathlib import Path
from .version import __version__

__all__ = []
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    if module_name == 'textom':  # Restrict to the textom module
        module = importlib.import_module(f"{__name__}.{module_name}")
        for name in dir(module):
            if not name.startswith("_"):  # Skip private attributes
                globals()[name] = getattr(module, name)
                __all__.append(name)

# Optional: Set package metadata
# __version__ = "0.1.10"
__author__ = "Moritz Frewein"
__email__ = "textom@fresnel.fr"

# import configparser
# # Define the path to the setup.cfg file
# setup_cfg_path = Path(__file__).parent.parent / "setup.cfg"

# # Read the version from setup.cfg
# config = configparser.ConfigParser()
# config.read(setup_cfg_path)
# __version__ = config["metadata"]["version"]