# chimere/metadata.py
"""Module gérant les métadonnées des structures."""
from dataclasses import dataclass
from typing import Dict, Any, Type, Optional, List
import ctypes
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class FieldMetadata:
    """Métadonnées d'un champ de structure."""
    name: str
    type: Type
    ctype: Type[ctypes._SimpleCData]
    nullable: bool = False
    description: Optional[str] = None

@dataclass(frozen=True)
class StructureMetadata:
    name: str
    fields: Dict[str, FieldMetadata]
    dll_path: Path
    function_prefix: str  # Ajout du nouveau champ
    description: Optional[str] = None
    version: str = "1.0.0"

class MetadataRegistry:
    """Registre global des métadonnées de structures."""
    _structures: Dict[str, StructureMetadata] = {}
    
    @classmethod
    def register_from_json(cls, json_path: Path) -> None:
        """Charge les métadonnées depuis un fichier JSON."""
        try:
            with open(json_path) as f:
                specs = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Erreur lors du chargement de {json_path}: {e}")
            raise
            
        for struct_name, spec in specs.items():
            cls._register_structure(struct_name, spec)
    
    @classmethod
    def _register_structure(cls, name: str, spec: Dict[str, Any]) -> None:
        try:
            fields = {
                field_name: FieldMetadata(
                    name=field_name,
                    type=eval(field_spec["type"]),
                    ctype=getattr(ctypes, field_spec["ctype"]),
                    nullable=field_spec.get("nullable", False),
                    description=field_spec.get("description")
                )
                for field_name, field_spec in spec["fields"].items()
            }
            
            cls._structures[name] = StructureMetadata(
                name=name,
                fields=fields,
                dll_path=Path(spec["dll_path"]),
                function_prefix=spec["function_prefix"],
                description=spec.get("description"),
                version=spec.get("version", "1.0.0")
            )
        except (KeyError, AttributeError) as e:
            raise ValueError(f"Spécification invalide pour {name}: {e}")

    @classmethod
    def get_structure(cls, name: str) -> StructureMetadata:
        """Récupère les métadonnées d'une structure."""
        if name not in cls._structures:
            raise KeyError(f"Structure inconnue: {name}")
        return cls._structures[name]