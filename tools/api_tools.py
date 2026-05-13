"""API / URL data source tools — fetch JSON or CSV from web endpoints."""

import json
import pandas as pd
import httpx
from hello_agents import BaseTool
from session import session


class FetchAPITool(BaseTool):
    name = "fetch_api_data"
    description = "Fetch JSON data from a REST API and load into DataFrame. Provide url. Optional: method (GET/POST), headers_json for custom headers."

    def run(self, url: str, method: str = "GET", headers_json: str = "{}") -> str:
        try:
            headers = json.loads(headers_json) if headers_json else {}
            client = httpx.Client(proxy=None, trust_env=False, timeout=30)
            if method.upper() == "POST":
                resp = client.post(url, headers=headers)
            else:
                resp = client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

            # Normalize JSON to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # Try common nesting patterns
                for key in ["data", "results", "items", "records", "rows"]:
                    if key in data and isinstance(data[key], list):
                        df = pd.DataFrame(data[key])
                        break
                else:
                    df = pd.DataFrame([data])
            else:
                return f"Unexpected API response type: {type(data)}"

            session.current_df = df
            session.file_path = url
            return f"API returned {df.shape[0]} rows x {df.shape[1]} columns.\nColumns: {list(df.columns)}\n\nFirst 5 rows:\n{df.head().to_string()}"
        except Exception as e:
            return f"API fetch error: {e}"


class LoadURLCSVTool(BaseTool):
    name = "load_url_csv"
    description = "Download and load a CSV file from a URL. Provide url. Returns data summary."

    def run(self, url: str) -> str:
        try:
            client = httpx.Client(proxy=None, trust_env=False, timeout=60)
            resp = client.get(url)
            resp.raise_for_status()
            import io
            df = pd.read_csv(io.StringIO(resp.text))
            session.current_df = df
            session.file_path = url
            return f"CSV from URL loaded: {df.shape[0]} rows x {df.shape[1]} columns.\nColumns: {list(df.columns)}\n\nFirst 5 rows:\n{df.head().to_string()}"
        except Exception as e:
            return f"URL CSV load error: {e}"
