import json
import pandas as pd
import csv
import io
from .registry import register_adapter
from .types import PythonDictData, PandasDataFrameData, CSVData, JSONData


@register_adapter(JSONData, PythonDictData)
class JSONToDictAdapter:
    def convert(self, json_obj: JSONData) -> PythonDictData:
        data = json.loads(json_obj.content)
        return PythonDictData(data)
    
@register_adapter(PythonDictData, PandasDataFrameData)
class DictToDataFrameAdapter:
    def convert(self, dict_obj: PythonDictData) -> PandasDataFrameData:
        df = pd.DataFrame([dict_obj.data])
        return PandasDataFrameData(df)

@register_adapter(PandasDataFrameData, CSVData)
class DataFrameToCSVAdapter:
    def convert(self, df_obj: PandasDataFrameData) -> CSVData:
        output = io.StringIO()
        df_obj.df.to_csv(output, index=False)
        return CSVData(output.getvalue())
