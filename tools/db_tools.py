"""Database data source tools — SQLAlchemy-based, supports SQLite + MySQL."""

import pandas as pd
from hello_agents import BaseTool
from session import session
from sqlalchemy import create_engine, inspect, text


def _create_engine(conn_str: str):
    return create_engine(conn_str, echo=False)


class SQLQueryTool(BaseTool):
    name = "query_database"
    description = "Execute SQL query on a database and load results as DataFrame. Provide connection_string (sqlite:///path or mysql+pymysql://user:pass@host/db) and query. Returns summary."

    def run(self, connection_string: str, query: str) -> str:
        try:
            engine = _create_engine(connection_string)
            with engine.connect() as conn:
                df = pd.read_sql_query(text(query), conn)
            session.current_df = df
            session.file_path = f"db://{connection_string.split('@')[-1] if '@' in connection_string else connection_string}"
            return f"Query returned {df.shape[0]} rows x {df.shape[1]} columns.\nColumns: {list(df.columns)}\n\nFirst 5 rows:\n{df.head().to_string()}"
        except Exception as e:
            return f"Database query error: {e}"


class ListTablesTool(BaseTool):
    name = "list_tables"
    description = "List all tables in a database. Provide connection_string. Returns table names and their row counts."

    def run(self, connection_string: str) -> str:
        try:
            engine = _create_engine(connection_string)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if not tables:
                return "No tables found in the database."
            lines = [f"Tables in database ({len(tables)}):"]
            for t in tables:
                try:
                    with engine.connect() as conn:
                        count = conn.execute(text(f"SELECT COUNT(*) FROM [{t}]")).scalar()
                    lines.append(f"  - {t}: {count} rows")
                except Exception:
                    lines.append(f"  - {t}: (unable to count)")
            return "\n".join(lines)
        except Exception as e:
            return f"Database connection error: {e}"
