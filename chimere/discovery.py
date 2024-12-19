# chimere/discovery.py
from __future__ import annotations

import ctypes
import logging
import re
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Any, Type, Optional, Set, List, Tuple

logger = logging.getLogger(__name__)

class CTypeCategory(Enum):
    INTEGER = auto()
    FLOAT = auto()
    CHAR = auto()
    POINTER = auto()
    ARRAY = auto()
    STRUCT = auto()
    UNION = auto()
    ENUM = auto()
    VOID = auto()
    BOOL = auto()
    FUNCTION = auto()

@dataclass
class TypeInfo:
    c_type: str
    python_type: Type
    ctypes_type: Type[ctypes._SimpleCData]
    category: CTypeCategory
    size: int
    signed: bool = True
    
class TypeMapper:
    # Mapping complet des types C standards
    C_TYPE_MAP = {
        # Entiers
        'char': TypeInfo('char', str, ctypes.c_char, CTypeCategory.CHAR, 1),
        'signed char': TypeInfo('signed char', int, ctypes.c_byte, CTypeCategory.INTEGER, 1),
        'unsigned char': TypeInfo('unsigned char', int, ctypes.c_ubyte, CTypeCategory.INTEGER, 1, False),
        'short': TypeInfo('short', int, ctypes.c_short, CTypeCategory.INTEGER, 2),
        'unsigned short': TypeInfo('unsigned short', int, ctypes.c_ushort, CTypeCategory.INTEGER, 2, False),
        'int': TypeInfo('int', int, ctypes.c_int, CTypeCategory.INTEGER, 4),
        'unsigned int': TypeInfo('unsigned int', int, ctypes.c_uint, CTypeCategory.INTEGER, 4, False),
        'long': TypeInfo('long', int, ctypes.c_long, CTypeCategory.INTEGER, 4),
        'unsigned long': TypeInfo('unsigned long', int, ctypes.c_ulong, CTypeCategory.INTEGER, 4, False),
        'long long': TypeInfo('long long', int, ctypes.c_longlong, CTypeCategory.INTEGER, 8),
        'unsigned long long': TypeInfo('unsigned long long', int, ctypes.c_ulonglong, CTypeCategory.INTEGER, 8, False),
        'size_t': TypeInfo('size_t', int, ctypes.c_size_t, CTypeCategory.INTEGER, 8, False),
        'ssize_t': TypeInfo('ssize_t', int, ctypes.c_ssize_t, CTypeCategory.INTEGER, 8),
        'intptr_t': TypeInfo('intptr_t', int, ctypes.c_void_p, CTypeCategory.INTEGER, 8),
        'uintptr_t': TypeInfo('uintptr_t', int, ctypes.c_void_p, CTypeCategory.INTEGER, 8, False),
        
        # Flottants
        'float': TypeInfo('float', float, ctypes.c_float, CTypeCategory.FLOAT, 4),
        'double': TypeInfo('double', float, ctypes.c_double, CTypeCategory.FLOAT, 8),
        'long double': TypeInfo('long double', float, ctypes.c_longdouble, CTypeCategory.FLOAT, 16),
        
        # Caractères et chaînes
        'char*': TypeInfo('char*', str, ctypes.c_char_p, CTypeCategory.POINTER, 8),
        'const char*': TypeInfo('const char*', str, ctypes.c_char_p, CTypeCategory.POINTER, 8),
        'wchar_t': TypeInfo('wchar_t', str, ctypes.c_wchar, CTypeCategory.CHAR, 2),
        'wchar_t*': TypeInfo('wchar_t*', str, ctypes.c_wchar_p, CTypeCategory.POINTER, 8),
        
        # Booléens
        'bool': TypeInfo('bool', bool, ctypes.c_bool, CTypeCategory.BOOL, 1),
        '_Bool': TypeInfo('_Bool', bool, ctypes.c_bool, CTypeCategory.BOOL, 1),
        
        # Pointeurs et void
        'void': TypeInfo('void', type(None), None, CTypeCategory.VOID, 0),
        'void*': TypeInfo('void*', object, ctypes.c_void_p, CTypeCategory.POINTER, 8),
        'const void*': TypeInfo('const void*', object, ctypes.c_void_p, CTypeCategory.POINTER, 8),
        
        # Types Windows spécifiques
        'BYTE': TypeInfo('BYTE', int, ctypes.c_byte, CTypeCategory.INTEGER, 1),
        'WORD': TypeInfo('WORD', int, ctypes.c_ushort, CTypeCategory.INTEGER, 2, False),
        'DWORD': TypeInfo('DWORD', int, ctypes.c_ulong, CTypeCategory.INTEGER, 4, False),
        'HANDLE': TypeInfo('HANDLE', int, ctypes.c_void_p, CTypeCategory.POINTER, 8),
        'LPSTR': TypeInfo('LPSTR', str, ctypes.c_char_p, CTypeCategory.POINTER, 8),
        'LPCSTR': TypeInfo('LPCSTR', str, ctypes.c_char_p, CTypeCategory.POINTER, 8),
        'LPWSTR': TypeInfo('LPWSTR', str, ctypes.c_wchar_p, CTypeCategory.POINTER, 8),
        'LPCWSTR': TypeInfo('LPCWSTR', str, ctypes.c_wchar_p, CTypeCategory.POINTER, 8),
        
        # Types POSIX spécifiques
        'pid_t': TypeInfo('pid_t', int, ctypes.c_int, CTypeCategory.INTEGER, 4),
        'uid_t': TypeInfo('uid_t', int, ctypes.c_uint, CTypeCategory.INTEGER, 4, False),
        'gid_t': TypeInfo('gid_t', int, ctypes.c_uint, CTypeCategory.INTEGER, 4, False),
        'off_t': TypeInfo('off_t', int, ctypes.c_longlong, CTypeCategory.INTEGER, 8),
        
        # Types réseaux
        'socklen_t': TypeInfo('socklen_t', int, ctypes.c_uint, CTypeCategory.INTEGER, 4, False),
        'in_addr_t': TypeInfo('in_addr_t', int, ctypes.c_uint, CTypeCategory.INTEGER, 4, False),
        'in_port_t': TypeInfo('in_port_t', int, ctypes.c_ushort, CTypeCategory.INTEGER, 2, False),
    }

    @classmethod
    def get_type_info(cls, c_type: str) -> TypeInfo:
        """Récupère les informations de type pour un type C."""
        # Normalise le type
        c_type = c_type.strip()
        c_type = re.sub(r'\s+', ' ', c_type)
        
        # Vérifie le cache
        if c_type in cls.C_TYPE_MAP:
            return cls.C_TYPE_MAP[c_type]
            
        # Analyse les types composés
        if '*' in c_type:
            base_type = c_type.replace('*', '').strip()
            if 'const' in base_type:
                base_type = base_type.replace('const', '').strip()
            if base_type in cls.C_TYPE_MAP:
                return TypeInfo(
                    c_type=c_type,
                    python_type=object,
                    ctypes_type=ctypes.POINTER(cls.C_TYPE_MAP[base_type].ctypes_type),
                    category=CTypeCategory.POINTER,
                    size=8
                )
        
        # Type par défaut si non trouvé
        logger.warning(f"Type inconnu: {c_type}, utilisation du type par défaut void*")
        return cls.C_TYPE_MAP['void*']

class LibraryIntrospector:
    def __init__(self, lib_path: Path):
        self.lib_path = lib_path
        self.lib = ctypes.CDLL(str(lib_path))
        self._type_mapper = TypeMapper()
        self._cached_structures: Dict[str, Any] = {}
        
    def analyze_library(self) -> Dict[str, Dict[str, Any]]:
        """Analyse complète de la bibliothèque."""
        structures = {}
        
        # Découvre les fonctions exportées
        exported_symbols = self._get_exported_symbols()
        
        for symbol in exported_symbols:
            if self._is_structure_related(symbol):
                struct_name = self._extract_structure_name(symbol)
                if struct_name not in structures:
                    structures[struct_name] = self._analyze_structure(struct_name)
                    
        return structures
    
    def _get_exported_symbols(self) -> Set[str]:
        """Récupère tous les symboles exportés de la bibliothèque."""
        try:
            # Utilise platform-specific tools pour lister les symboles
            # nm, drmemory, depends.exe, etc.
            pass
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des symboles: {e}")
            return set()

    def _is_structure_related(self, symbol: str) -> bool:
        """Détermine si un symbole est lié à une structure."""
        pattern = r'^(create|free|get|set)_[a-zA-Z0-9_]+$'
        return bool(re.match(pattern, symbol))

    def _analyze_structure(self, struct_name: str) -> Dict[str, Any]:
        """Analyse une structure particulière."""
        if struct_name in self._cached_structures:
            return self._cached_structures[struct_name]
            
        struct_info = {
            'fields': {},
            'methods': {},
            'size': 0,
            'alignment': 0
        }
        
        try:
            # Analyse le header ou les symboles de debug
            field_info = self._extract_field_info(struct_name)
            for field_name, c_type in field_info.items():
                type_info = self._type_mapper.get_type_info(c_type)
                struct_info['fields'][field_name] = {
                    'type': type_info,
                    'offset': 0,  # Calculé plus tard
                }
                
            # Trouve les méthodes associées
            struct_info['methods'] = self._find_structure_methods(struct_name)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de {struct_name}: {e}")
            
        self._cached_structures[struct_name] = struct_info
        return struct_info

    def _find_structure_methods(self, struct_name: str) -> Dict[str, Any]:
        """Trouve toutes les méthodes associées à une structure."""
        methods = {}
        prefixes = ['create', 'free', 'get', 'set']
        
        for prefix in prefixes:
            method_name = f"{prefix}_{struct_name}"
            if hasattr(self.lib, method_name):
                methods[prefix] = {
                    'name': method_name,
                    'function': getattr(self.lib, method_name)
                }
                
        return methods