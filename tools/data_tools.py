import os
import pandas as pd
from hello_agents import BaseTool
from session import session


class LoadCSVTool(BaseTool):
    name = "load_csv"
    description = "Load a CSV file into the DataFrame. Provide file_path to the CSV file. Returns data summary."

    def run(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            return f"Error: File not found at '{file_path}'."
        try:
            df = pd.read_csv(file_path)
            session.current_df = df
            session.file_path = file_path
            return self._summarize(df)
        except Exception as e:
            return f"Error loading CSV: {e}"

    def _summarize(self, df: pd.DataFrame) -> str:
        lines = [
            f"Loaded: {session.file_path}",
            f"Shape: {df.shape[0]} rows x {df.shape[1]} columns",
            f"Columns: {list(df.columns)}",
            f"Dtypes:\n{df.dtypes.to_string()}",
            f"Missing values:\n{df.isnull().sum().to_string()}",
            f"First 5 rows:\n{df.head().to_string()}",
        ]
        return "\n".join(lines)


class LoadExcelTool(BaseTool):
    name = "load_excel"
    description = "Load an Excel file (.xlsx/.xls) into the DataFrame. Provide file_path and optional sheet_name (default 0). Returns summary."

    def run(self, file_path: str, sheet_name: str = "0") -> str:
        if not os.path.exists(file_path):
            return f"Error: File not found at '{file_path}'."
        try:
            sheet = 0 if sheet_name == "0" else sheet_name
            df = pd.read_excel(file_path, sheet_name=sheet)
            session.current_df = df
            session.file_path = file_path
            lines = [
                f"Loaded: {session.file_path}",
                f"Shape: {df.shape[0]} rows x {df.shape[1]} columns",
                f"Columns: {list(df.columns)}",
                f"Dtypes:\n{df.dtypes.to_string()}",
                f"Missing values:\n{df.isnull().sum().to_string()}",
                f"First 5 rows:\n{df.head().to_string()}",
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"Error loading Excel: {e}"


class GetDataInfoTool(BaseTool):
    name = "get_data_info"
    description = "Return detailed info about the currently loaded DataFrame: shape, columns, dtypes, missing counts, memory usage, and basic statistics for numeric columns."

    def run(self) -> str:
        df = session.current_df
        if df is None:
            return "Error: No data loaded. Use load_csv or load_excel first."
        lines = [
            f"File: {session.file_path}",
            f"Shape: {df.shape[0]} rows x {df.shape[1]} columns",
            f"Columns: {list(df.columns)}",
            f"Dtypes:\n{df.dtypes.to_string()}",
            f"Missing:\n{df.isnull().sum().to_string()}",
            f"Memory: {df.memory_usage(deep=True).sum() / 1024:.1f} KB",
            f"Numeric summary:\n{df.describe().to_string()}",
        ]
        return "\n".join(lines)
