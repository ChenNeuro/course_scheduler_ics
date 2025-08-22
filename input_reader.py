# input_reader.py
import pandas as pd

def read_schedule_xls(filepath: str):
    """
    从 Excel 文件读取课程表（xls/xlsx），返回 DataFrame
    假设列是星期几，行是第几节
    """
    df = pd.read_excel(filepath, header=0, index_col=0)
    return df