import importlib
import inspect
import pkgutil
from typing import List

def get_all_classes_from_package(package_name: str) -> List[str]:
    """
    Recursively finds all classes defined in a package and its subpackages.
    Returns their fully qualified names for use in __all__ declarations.
    
    Args:
        package_name: Name of the package to search
        
    Returns:
        List of fully qualified class names as strings
        
    Example:
        __all__ = get_all_classes_from_package(__name__)
    """
    class_names = []
    
    # Import the root package
    package = importlib.import_module(package_name)
    
    # Recursively traverse modules and submodules in the package
    for _, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        # Import the module or submodule
        module = importlib.import_module(module_name)
        
        # Get all classes defined in this module
        for name, cls in inspect.getmembers(module, inspect.isclass):
            # Only include classes that were defined in this module
            if cls.__module__ == module_name:
                # Add the fully qualified class name
                class_names.append(f"{module_name}.{name}")
    
    return class_names