import importlib
import pkgutil
from types import ModuleType
from typing import Dict

def import_moduls(paquete: str) -> Dict[str, ModuleType]:
    """
    Recursively imports all modules from a package and its subpackages.

    This function traverses through a package and all its subpackages,
    importing each module it finds. It maintains a dictionary of all
    imported modules keyed by their full package path.

    Args:
        paquete (str): Base package name (e.g., 'routes')

    Returns:
        Dict[str, ModuleType]: Dictionary with full module names as keys
                              and their imported objects as values

    Example:
        modules = import_moduls('routes')
        # Result: {'routes.auth': <module 'routes.auth'>,
        #          'routes.api.users': <module 'routes.api.users'>, ...}
    """
    modulos = {}
    paquete_obj = importlib.import_module(paquete)

    def _importar_recursivo(paquete_obj, paquete_raiz):
        """
        Recursive helper function for module importing.

        Args:
            paquete_obj: Package object to import from
            paquete_raiz: Root package name for building full module paths
        """
        if hasattr(paquete_obj, "__path__"):  # Ensures it's a package
            for finder, nombre_modulo, es_paquete in pkgutil.iter_modules(paquete_obj.__path__):
                nombre_completo = f"{paquete_raiz}.{nombre_modulo}"
                modulos[nombre_completo] = importlib.import_module(nombre_completo)
                if es_paquete:
                    _importar_recursivo(
                        importlib.import_module(nombre_completo),
                        nombre_completo
                    )

    _importar_recursivo(paquete_obj, paquete)
    return modulos