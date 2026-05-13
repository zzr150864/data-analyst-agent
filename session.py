import pandas as pd
from typing import List, Optional


class SessionState:
    def __init__(self):
        self.current_df: Optional[pd.DataFrame] = None
        self.file_path: str = ""
        self.chart_paths: List[str] = []
        self.report_paths: List[str] = []

    def reset(self):
        self.current_df = None
        self.file_path = ""
        self.chart_paths.clear()
        self.report_paths.clear()


session = SessionState()
