import numpy as np
import pandas as pd
from hello_agents import BaseTool
from session import session


class DescriptiveStatsTool(BaseTool):
    name = "descriptive_stats"
    description = "Compute descriptive statistics for specified numeric columns (comma-separated) or all numeric columns if empty. Returns mean, std, min, max, quartiles, skewness, kurtosis."

    def run(self, columns: str = "") -> str:
        df = session.current_df
        if df is None:
            return "Error: No data loaded."
        cols = [c.strip() for c in columns.split(",") if c.strip()] if columns else None
        numeric = df.select_dtypes(include=[np.number])
        if cols:
            numeric = numeric[[c for c in cols if c in numeric.columns]]
        if numeric.empty:
            return "No numeric columns found in the data."
        stats = numeric.describe().to_string()
        skew = numeric.skew().to_frame("skewness").to_string()
        kurt = numeric.kurtosis().to_frame("kurtosis").to_string()
        return f"Descriptive Statistics:\n{stats}\n\nSkewness:\n{skew}\n\nKurtosis:\n{kurt}"


class CorrelationAnalysisTool(BaseTool):
    name = "correlation_analysis"
    description = "Compute pairwise correlation matrix for numeric columns. Provide method: 'pearson', 'spearman', or 'kendall'. Returns full matrix and top 5 strongest correlations."

    def run(self, method: str = "pearson") -> str:
        df = session.current_df
        if df is None:
            return "Error: No data loaded."
        numeric = df.select_dtypes(include=[np.number])
        if numeric.shape[1] < 2:
            return "Need at least 2 numeric columns for correlation analysis."
        corr = numeric.corr(method=method)
        pairs = []
        for i in range(len(corr.columns)):
            for j in range(i + 1, len(corr.columns)):
                pairs.append((corr.columns[i], corr.columns[j], corr.iloc[i, j]))
        pairs.sort(key=lambda x: abs(x[2]), reverse=True)
        top5_str = "\n".join(f"  {a} <-> {b}: {v:.4f}" for a, b, v in pairs[:5])
        return f"Correlation Matrix ({method}):\n{corr.to_string()}\n\nTop 5 Correlations:\n{top5_str}"


class TrendDetectionTool(BaseTool):
    name = "trend_detection"
    description = "Detect linear trends in a numeric column using linear regression. Provide value_column name. Returns slope, intercept, R-squared, and trend direction."

    def run(self, value_column: str, date_column: str = "") -> str:
        df = session.current_df
        if df is None:
            return "Error: No data loaded."
        if value_column not in df.columns:
            return f"Column '{value_column}' not found. Available: {list(df.columns)}"
        data = df.dropna(subset=[value_column])
        y = data[value_column].values.astype(np.float64)
        if date_column and date_column in df.columns:
            x_raw = pd.to_numeric(pd.to_datetime(data[date_column])).values.astype(np.float64)
        else:
            x_raw = np.arange(len(y), dtype=np.float64)

        # Linear regression with numpy: y = slope * x + intercept
        X = np.column_stack([x_raw, np.ones_like(x_raw)])
        coeffs, residuals, rank, sv = np.linalg.lstsq(X, y, rcond=None)
        slope, intercept = coeffs[0], coeffs[1]

        # R-squared
        y_pred = slope * x_raw + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0

        direction = "upward" if slope > 0 else "downward"
        return (
            f"Trend for '{value_column}': "
            f"slope={slope:.4f}, intercept={intercept:.2f}, "
            f"R^2={r2:.4f}, direction={direction}"
        )


class GroupByAnalysisTool(BaseTool):
    name = "groupby_analysis"
    description = "Group data by a categorical column and compute aggregate (mean, sum, count, min, max) for a numeric column."

    def run(self, group_column: str, agg_column: str, agg_func: str = "mean") -> str:
        df = session.current_df
        if df is None:
            return "Error: No data loaded."
        if group_column not in df.columns:
            return f"Group column '{group_column}' not found. Available: {list(df.columns)}"
        if agg_column not in df.columns:
            return f"Aggregate column '{agg_column}' not found. Available: {list(df.columns)}"
        result = df.groupby(group_column)[agg_column].agg(agg_func)
        return f"GroupBy '{group_column}' -> {agg_func}({agg_column}):\n{result.to_string()}"
