from abc import ABC, abstractmethod
import pandas as pd

class BaseRepresentation(ABC):
    """Classe de base abstraite pour toutes les représentations de données."""
    pass

class JSONData(BaseRepresentation):
    def __init__(self, content: str):
        """
        content: string contenant un JSON, ex: '{"key": "value"}'
        """
        self.content = content

class CSVData(BaseRepresentation):
    def __init__(self, content: str):
        """
        content: string CSV, ex: "col1,col2\nval1,val2"
        """
        self.content = content

class PythonDictData(BaseRepresentation):
    def __init__(self, data: dict):
        """
        data: un dictionnaire Python, ex: {"name": "Alice", "age": 30}
        """
        self.data = data

class PandasDataFrameData(BaseRepresentation):
    def __init__(self, df: pd.DataFrame):
        """
        df: un objet pandas DataFrame
        """
        self.df = df

class XMLData(BaseRepresentation):
    def __init__(self, content: str):
        self.content = content

