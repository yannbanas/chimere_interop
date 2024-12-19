import json
import pytest
from pathlib import Path
from chimere.metadata import MetadataRegistry
from chimere.adapters import DictToStructAdapter
from chimere.exceptions import ValidationError

@pytest.fixture
def library_configs():
    return {
        "GoStruct": {
            "dll_path": "D:/Experimentation/chimere_interop/src_sample_intero/python_go_lib/go_struct.dll",
            "function_prefix": "create_go_struct",
            "fields": {"name": {"type": "str", "ctype": "c_char_p"},
                      "age": {"type": "int", "ctype": "c_int"}},
            "description": "Go structure"
        },
        "CppStruct": {
            "dll_path": "D:/Experimentation/chimere_interop/dll/python_cpp_lib.dll",
            "function_prefix": "create_struct",
            "fields": {"name": {"type": "str", "ctype": "c_char_p"},
                      "age": {"type": "int", "ctype": "c_int"}},
            "description": "C++ structure"
        },
        "RustStruct": {
            "dll_path": "D:/Experimentation/chimere_interop/src_sample_intero/python_rust_lib/target/release/python_rust_lib.dll",
            "function_prefix": "create_rust_struct",
            "fields": {"name": {"type": "str", "ctype": "c_char_p"},
                      "age": {"type": "int", "ctype": "c_int"}},
            "description": "Rust structure"
        }
    }

@pytest.fixture
def setup_registry(tmp_path, library_configs):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(library_configs))
    MetadataRegistry.register_from_json(config_path)

@pytest.mark.parametrize("struct_name", ["GoStruct", "CppStruct", "RustStruct"])
def test_create_struct(setup_registry, struct_name):
    adapter = DictToStructAdapter(struct_name)
    data = {"name": "Test", "age": 25}
    result = adapter.convert(data)
    assert result.ptr.contents.name.decode() == "Test"
    assert result.ptr.contents.age == 25

@pytest.mark.parametrize("struct_name", ["GoStruct", "CppStruct", "RustStruct"])
def test_struct_invalid_type(setup_registry, struct_name):
    adapter = DictToStructAdapter(struct_name)
    with pytest.raises(ValidationError):
        adapter.convert({"name": 123, "age": "invalid"})

@pytest.mark.parametrize("struct_name", ["GoStruct", "CppStruct", "RustStruct"])
def test_struct_missing_field(setup_registry, struct_name):
    adapter = DictToStructAdapter(struct_name)
    with pytest.raises(ValidationError):
        adapter.convert({"name": "Test"})

@pytest.mark.parametrize("struct_name", ["GoStruct", "CppStruct", "RustStruct"])
def test_struct_memory_cleanup(setup_registry, struct_name):
    adapter = DictToStructAdapter(struct_name)
    result = adapter.convert({"name": "Test", "age": 25})
    del result

@pytest.mark.parametrize("struct_name", ["GoStruct", "CppStruct", "RustStruct"])
def test_struct_unicode(setup_registry, struct_name):
    adapter = DictToStructAdapter(struct_name)
    data = {"name": "éèà", "age": 25}
    result = adapter.convert(data)
    assert result.ptr.contents.name.decode() == "éèà"

# Tests spécifiques
@pytest.mark.parametrize("struct_name", ["GoStruct", "CppStruct", "RustStruct"])
def test_struct_null_handling(setup_registry, struct_name):
    adapter = DictToStructAdapter(struct_name)
    # Le test devrait passer directement avec ValidationError
    with pytest.raises(ValidationError, match="Le champ name ne peut pas être null"):
        adapter.convert({"name": None, "age": 25})

@pytest.mark.parametrize("struct_name", ["GoStruct", "CppStruct", "RustStruct"])
def test_struct_large_values(setup_registry, struct_name):
    adapter = DictToStructAdapter(struct_name)
    data = {"name": "x" * 1000, "age": 2**30}
    result = adapter.convert(data)
    assert len(result.ptr.contents.name.decode()) == 1000

@pytest.mark.parametrize("struct_name", ["GoStruct", "CppStruct", "RustStruct"])
def test_struct_special_chars(setup_registry, struct_name):
    adapter = DictToStructAdapter(struct_name)
    data = {"name": "Test\0\n\r\t", "age": 25}
    result = adapter.convert(data)
    assert result.ptr.contents.name.decode().replace('\0', '') == "Test\n\r\t"