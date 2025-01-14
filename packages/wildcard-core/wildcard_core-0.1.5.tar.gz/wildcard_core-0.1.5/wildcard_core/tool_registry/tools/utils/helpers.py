import importlib
import inspect
import pkgutil
import base64
from typing import List
from wildcard_core.tool_registry.tools.base import BaseAction
import re

def load_actions_from_package(package_name: str) -> List[BaseAction]:
    """Recursively loads and instantiates all Action subclasses from a specified package."""
    actions = []
    
    # Import the root package
    package = importlib.import_module(package_name)
    
    # Recursively traverse modules and submodules in the package
    for _, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        # Import the module or submodule
        module = importlib.import_module(module_name)
        
        # Inspect each class in the module to find Action subclasses
        for _, cls in inspect.getmembers(module, inspect.isclass):
            # Check if the class is a subclass of Action but not Action itself
            if issubclass(cls, BaseAction) and cls is not BaseAction:
                # Instantiate the action and add it to the list
                actions.append(cls())
    
    return actions

def is_base64_urlsafe(s: str) -> bool:
    x = re.search("^([A-Za-z0-9+/]{4})*([A-Za-z0-9+/]{3}=|[A-Za-z0-9+/]{2}==)?$", s)
    if x:
        return True
    else: 
        return False
