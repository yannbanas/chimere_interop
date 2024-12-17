from chimere.types import JSONData, PythonDictData, PandasDataFrameData, CSVData, XMLData, ParquetData, ERRORData
from chimere.core import convert
import pytest
import pandas as pd

# ---- Tests de base ----

def test_json_to_dict():
    json_obj = JSONData('{"name": "Alice", "age": 30}')
    dict_obj = convert(json_obj, PythonDictData)
    assert isinstance(dict_obj, PythonDictData)
    assert dict_obj.data == {"name": "Alice", "age": 30}

#definir un type dans type ne pas creer adapter pour un cas impossible pour verifier que le test echoue
def test_no_adapter_found():
    from chimere.types import CSVData
    json_obj = JSONData('{"key": "value"}')
    with pytest.raises(ValueError):
        convert(json_obj, ERRORData)

# ---- Tests ajoutés pour Phase 2 ---- 

def test_chain_conversion_json_to_csv():
    # Chemin: JSONData -> PythonDictData -> PandasDataFrameData -> CSVData
    json_obj = JSONData('{"name": "Bob", "age": 25}')
    csv_obj = convert(json_obj, CSVData)
    assert isinstance(csv_obj, CSVData)
    # On vérifie que le CSV obtenu contient bien les colonnes et la valeur
    assert "name" in csv_obj.content
    assert "age" in csv_obj.content
    assert "Bob" in csv_obj.content
    assert "25" in csv_obj.content

def test_no_direct_or_indirect_path():
    # Au lieu de CSV -> PythonDictData, on va tenter CSV -> ERRORData
    # Ce type n'a aucun adaptateur, donc aucun chemin n'est possible.
    from chimere.types import ERRORData
    csv_obj = CSVData("col1,col2\nval1,val2")
    with pytest.raises(ValueError, match="Aucun chemin de conversion trouvé"):
        convert(csv_obj, ERRORData)


# ---- Tests ajoutés pour Phase 3 ----

def test_xml_to_json_via_dict():
    # Chemin: XMLData -> PythonDictData -> JSONData
    xml_content = "<root>Hello</root>"
    xml_obj = XMLData(xml_content)
    json_obj = convert(xml_obj, JSONData)
    assert isinstance(json_obj, JSONData)
    # On vérifie le contenu JSON, qui devrait provenir du dict {root: "Hello"}
    import json
    data = json.loads(json_obj.content)
    assert data == {"root": "Hello"}

def test_invalid_xml():
    # On fournit un XML invalide pour vérifier que la validation échoue
    xml_content = "<root><unclosedTag>"
    xml_obj = XMLData(xml_content)
    with pytest.raises(ValueError, match="XML invalide"):
        convert(xml_obj, JSONData)  # Doit échouer avant conversion

def test_dataframe_to_parquet():
    # On teste la conversion PandasDataFrameData -> ParquetData
    df = pd.DataFrame({"name": ["Charlie"], "age": [40]})
    df_obj = PandasDataFrameData(df)
    pq_obj = convert(df_obj, ParquetData)
    assert isinstance(pq_obj, ParquetData)
    # On pourrait vérifier le contenu du parquet en le relisant :
    df_back = pd.read_parquet(pq_obj.path)
    assert df_back.equals(df)

def test_invalid_json_validation():
    # On fournit un JSON invalide à l'adaptateur JSON -> Dict
    invalid_json = JSONData("{invalid_json}")
    with pytest.raises(ValueError, match="JSON invalide"):
        convert(invalid_json, PythonDictData)
