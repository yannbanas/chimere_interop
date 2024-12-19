# chimere/dynamic_types.py
"""Module de génération dynamique des types."""
import ctypes
from typing import Type, Dict, Any
from .metadata import StructureMetadata

class DynamicStructureFactory:
    """Fabrique de structures dynamiques."""
    _cache: Dict[str, Type[ctypes.Structure]] = {}
    
    @classmethod
    def create_structure(cls, metadata: StructureMetadata) -> Type[ctypes.Structure]:
        """Crée ou récupère une structure ctypes dynamique."""
        if metadata.name not in cls._cache:
            cls._cache[metadata.name] = cls._create_new_structure(metadata)
        return cls._cache[metadata.name]
    
    @staticmethod
    def _create_new_structure(metadata: StructureMetadata) -> Type[ctypes.Structure]:
        """Crée une nouvelle structure ctypes."""
        return type(
            f"Dynamic{metadata.name}",
            (ctypes.Structure,),
            {
                "_fields_": [(f.name, f.ctype) for f in metadata.fields.values()],
                "__doc__": metadata.description or f"Structure dynamique pour {metadata.name}"
            }
        )

class DynamicStructData:
    def __init__(self, ptr: Any, metadata: StructureMetadata) -> None:
        self.ptr = ptr
        self.metadata = metadata
        self._lib = ctypes.CDLL(str(metadata.dll_path))
        
    def __del__(self) -> None:
        if hasattr(self, 'ptr') and self.ptr:
            free_name = self.metadata.function_prefix.replace('create_', 'free_')
            free_func = getattr(self._lib, free_name)
            free_func(self.ptr)