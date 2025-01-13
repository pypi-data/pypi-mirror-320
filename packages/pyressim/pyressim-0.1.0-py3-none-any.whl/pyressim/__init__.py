import os
import importlib

# Get all Python files in the current directory (excluding __init__.py)
module_files = [f[:-3] for f in os.listdir(os.path.dirname(__file__)) if f.endswith(".py") and f != "__init__.py"]

# Dynamically import all modules
for module in module_files:
    module_obj = importlib.import_module(f".{module}", package=__name__)
    globals().update({name: getattr(module_obj, name) for name in dir(module_obj) if not name.startswith("_")})