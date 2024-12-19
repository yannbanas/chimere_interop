import json
import pandas as pd
import csv
import io
import xml.etree.ElementTree as ET
import tempfile
import ctypes
from typing import Any, Dict
from .registry import register_adapter
from .types import (
    PythonDictData, PandasDataFrameData, CSVData, JSONData, XMLData, ParquetData
)
from .metadata import MetadataRegistry
from .dynamic_types import DynamicStructureFactory, DynamicStructData
from .exceptions import ValidationError, ConversionError

# Dynamic adapters
class DynamicAdapter:
    """Adaptateur dynamique de base."""
    def __init__(self, target_structure: str) -> None:
        self.metadata = MetadataRegistry.get_structure(target_structure)
        self.struct_type = DynamicStructureFactory.create_structure(self.metadata)
        self._lib = ctypes.CDLL(str(self.metadata.dll_path))
        
    def validate(self, data: Dict[str, Any]) -> None:
        """Valide les données d'entrée."""
        required = {
            name: meta for name, meta in self.metadata.fields.items() 
            if not meta.nullable
        }
        missing = set(required) - set(data)
        if missing:
            raise ValidationError(f"Champs requis manquants: {missing}")
        
        for name, value in data.items():
            field = self.metadata.fields.get(name)
            if not field:
                raise ValidationError(f"Champ inconnu: {name}")
            if value is not None and not isinstance(value, field.type):
                raise ValidationError(
                    f"Type invalide pour {name}: attendu {field.type}, reçu {type(value)}"
                )

class DictToStructAdapter(DynamicAdapter):
    def convert(self, data: Dict[str, Any]) -> DynamicStructData:
        self.validate(data)
        try:
            create_func = getattr(self._lib, self.metadata.function_prefix)
            args = []
            for field in self.metadata.fields.values():
                value = data.get(field.name)
                if value is None:
                    if not field.nullable:
                        raise ValidationError(f"Le champ {field.name} ne peut pas être null")
                    value = self._get_null_value(field.ctype)
                elif isinstance(value, str):
                    value = value.encode('utf-8', errors='ignore')
                    if '\0' in value.decode():  # Gérer NULL bytes
                        value = value.decode().replace('\0', '').encode('utf-8')
                args.append(value)
            
            create_func.argtypes = [f.ctype for f in self.metadata.fields.values()]
            create_func.restype = ctypes.POINTER(self.struct_type)
            
            ptr = create_func(*args)
            return DynamicStructData(ptr, self.metadata)
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ConversionError(f"Erreur de conversion: {e}")
    
    def _get_null_value(self, ctype):
        if ctype == ctypes.c_char_p:
            return None
        return 0
           
# Classic adapters
@register_adapter(PythonDictData, DynamicStructData, cost=5, fidelity='high')
class DictToDynamicStructAdapter:
    def __init__(self, lib_name: str, struct_name: str):
        self.lib_name = lib_name
        self.struct_name = struct_name
        self.metadata = MetadataRegistry.get_structure(f"{lib_name}_{struct_name}")
        
    def convert(self, dict_obj: PythonDictData) -> DynamicStructData:
        adapter = DictToStructAdapter(f"{self.lib_name}_{self.struct_name}")
        return adapter.convert(dict_obj.data)

@register_adapter(JSONData, PythonDictData, cost=2, fidelity='high')
class JSONToDictAdapter:
    def validate_input(self, json_obj: JSONData):
        # Vérifier que c'est du JSON valide
        try:
            json.loads(json_obj.content)
        except json.JSONDecodeError:
            raise ValueError("JSON invalide")

    def convert(self, json_obj: JSONData) -> PythonDictData:
        data = json.loads(json_obj.content)
        return PythonDictData(data)


@register_adapter(PythonDictData, JSONData, cost=1, fidelity='high')
class DictToJSONAdapter:
    def convert(self, dict_obj: PythonDictData) -> JSONData:
        return JSONData(json.dumps(dict_obj.data))


@register_adapter(PythonDictData, PandasDataFrameData, cost=2, fidelity='high')
class DictToDataFrameAdapter:
    def convert(self, dict_obj: PythonDictData) -> PandasDataFrameData:
        df = pd.DataFrame([dict_obj.data])
        return PandasDataFrameData(df)


@register_adapter(PandasDataFrameData, PythonDictData, cost=2, fidelity='high')
class DataFrameToDictAdapter:
    def convert(self, df_obj: PandasDataFrameData) -> PythonDictData:
        # Conversion d'un DataFrame en Dict (on prend la première ligne par exemple)
        # Pour un DF plus complexe, on pourrait convertir en liste de dicts.
        # Ici, on simplifie au maximum.
        if len(df_obj.df) == 1:
            data_dict = df_obj.df.iloc[0].to_dict()
        else:
            # Si plus d'une ligne, on choisit d'en faire une liste de dicts
            data_dict = df_obj.df.to_dict(orient='records')
        return PythonDictData(data_dict)


@register_adapter(PandasDataFrameData, CSVData, cost=2, fidelity='medium')
class DataFrameToCSVAdapter:
    def convert(self, df_obj: PandasDataFrameData) -> CSVData:
        output = io.StringIO()
        df_obj.df.to_csv(output, index=False)
        return CSVData(output.getvalue())


@register_adapter(CSVData, PandasDataFrameData, cost=2, fidelity='medium')
class CSVToDataFrameAdapter:
    def convert(self, csv_obj: CSVData) -> PandasDataFrameData:
        input_io = io.StringIO(csv_obj.content)
        df = pd.read_csv(input_io)
        return PandasDataFrameData(df)


@register_adapter(XMLData, PythonDictData, cost=3, fidelity='medium')
class XMLToDictAdapter:
    def validate_input(self, xml_obj: XMLData):
        try:
            ET.fromstring(xml_obj.content)
        except ET.ParseError:
            raise ValueError("XML invalide")

    def convert(self, xml_obj: XMLData) -> PythonDictData:
        # Conversion simplifiée XML->Dict (juste un exemple)
        root = ET.fromstring(xml_obj.content)
        return PythonDictData({root.tag: root.text})


@register_adapter(PythonDictData, XMLData, cost=3, fidelity='medium')
class DictToXMLAdapter:
    def convert(self, dict_obj: PythonDictData) -> XMLData:
        # On prend un cas simplifié : si dict_obj.data est un dict simple clé:valeur
        # On crée un seul élément XML. Pour un dict plus complexe, il faudrait une logique plus élaborée.
        if isinstance(dict_obj.data, dict) and len(dict_obj.data) == 1:
            key = list(dict_obj.data.keys())[0]
            value = dict_obj.data[key]
            xml_str = f"<{key}>{value}</{key}>"
        else:
            # Conversion simplifiée pour un dict complexe
            # On génère un root et des sous-éléments
            root = ET.Element("root")
            for k, v in dict_obj.data.items():
                elem = ET.SubElement(root, k)
                elem.text = str(v)
            xml_str = ET.tostring(root, encoding='unicode')
        return XMLData(xml_str)


@register_adapter(PandasDataFrameData, ParquetData, cost=4, fidelity='high')
class DataFrameToParquetAdapter:
    def convert(self, df_obj: PandasDataFrameData) -> ParquetData:
        # Sauver le DataFrame en parquet dans un fichier temporaire
        temp = tempfile.NamedTemporaryFile(suffix=".parquet", delete=False)
        df_obj.df.to_parquet(temp.name)
        return ParquetData(temp.name)


@register_adapter(ParquetData, PandasDataFrameData, cost=4, fidelity='high')
class ParquetToDataFrameAdapter:
    def convert(self, pq_obj: ParquetData) -> PandasDataFrameData:
        df = pd.read_parquet(pq_obj.path)
        return PandasDataFrameData(df)
    
@register_adapter(PythonDictData, DynamicStructData, cost=5, fidelity='medium')
class DictToForeignStructAdapter:
    def __init__(self, target_type: str):
        self.target_type = target_type
        
    def convert(self, dict_obj: PythonDictData) -> DynamicStructData:
        adapter = DictToStructAdapter(self.target_type)
        return adapter.convert(dict_obj.data)

@register_adapter(DynamicStructData, JSONData, cost=5, fidelity='medium')
class ForeignStructToJSONAdapter:
    def convert(self, struct_obj: DynamicStructData) -> JSONData:
        contents = struct_obj.ptr.contents
        data = {}
        for field_name, field_meta in struct_obj.metadata.fields.items():
            value = getattr(contents, field_name)
            if isinstance(value, bytes):
                value = value.decode('utf-8')
            data[field_name] = value
        return JSONData(json.dumps(data))