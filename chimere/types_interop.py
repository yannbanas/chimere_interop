from .discovery import LibraryIntrospector, TypeMapper
from pathlib import Path

# Chargement automatique des structures
def load_libraries():
    libraries = {
        'cpp': Path("D:/Experimentation/chimere_interop/dll/python_cpp_lib.dll"),
        'rust': Path("D:/Experimentation/chimere_interop/src_sample_intero/python_rust_lib/target/release/python_rust_lib.dll"),
        'go': Path("D:/Experimentation/chimere_interop/src_sample_intero/python_go_lib/go_struct.dll")
    }
    
    structs = {}
    for name, path in libraries.items():
        introspector = LibraryIntrospector(path)
        structs[name] = introspector.analyze_library()
    
    return structs