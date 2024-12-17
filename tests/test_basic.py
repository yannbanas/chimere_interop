from chimere.types import JSONData, PythonDictData, PandasDataFrameData, CSVData, XMLData
from chimere.core import convert
import pytest

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
        convert(json_obj, XMLData)

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
    # On va demander une conversion impossible, par ex: JSONData -> PandasDataFrameData directement
    # Sans passer par Dict. Ici, c'est possible si on n'avait pas l'adaptateur correspondant.
    # Pour le test, imaginons qu'on supprime l'adaptateur Dict->DF, ce test prouverait l'échec.
    # Dans ce cas, on va juste tenter une conversion farfelue, par ex: CSV -> PythonDictData (non défini).
    csv_obj = CSVData("col1,col2\nval1,val2")
    with pytest.raises(ValueError, match="Aucun chemin de conversion trouvé"):
        convert(csv_obj, PythonDictData)