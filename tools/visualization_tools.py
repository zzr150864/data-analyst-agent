import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from hello_agents import BaseTool
from session import session
from utils.file_utils import ensure_output_dir, output_path


def _get_df():
    df = session.current_df
    if df is None:
        raise ValueError("No data loaded.")
    return df


class BarChartTool(BaseTool):
    name = "bar_chart"
    description = "Create a bar chart (x_column vs y_column). Saves to outputs/. Choose format='png' or format='html'."

    def run(self, x_column: str, y_column: str, title: str = "", format: str = "png") -> str:
        df = _get_df()
        ensure_output_dir()
        fname = f"bar_{x_column}_vs_{y_column}".replace(" ", "_")
        chart_title = title or f"{y_column} by {x_column}"
        if format == "html":
            import plotly.express as px
            fig = px.bar(df, x=x_column, y=y_column, title=chart_title)
            path = output_path(f"{fname}.html")
            fig.write_html(path)
        else:
            fig, ax = plt.subplots()
            ax.bar(df[x_column].astype(str), df[y_column])
            ax.set_title(chart_title)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            plt.xticks(rotation=45)
            path = output_path(f"{fname}.png")
            fig.savefig(path, bbox_inches="tight", dpi=100)
            plt.close(fig)
        session.chart_paths.append(path)
        return f"Chart saved: {path}"


class LineChartTool(BaseTool):
    name = "line_chart"
    description = "Create a line chart (x_column vs y_column). Saves to outputs/. Choose format='png' or format='html'."

    def run(self, x_column: str, y_column: str, title: str = "", format: str = "png") -> str:
        df = _get_df()
        ensure_output_dir()
        fname = f"line_{x_column}_vs_{y_column}".replace(" ", "_")
        chart_title = title or f"{y_column} over {x_column}"
        if format == "html":
            import plotly.express as px
            fig = px.line(df, x=x_column, y=y_column, title=chart_title)
            path = output_path(f"{fname}.html")
            fig.write_html(path)
        else:
            fig, ax = plt.subplots()
            ax.plot(df[x_column], df[y_column], marker="o", linewidth=2)
            ax.set_title(chart_title)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            plt.xticks(rotation=45)
            path = output_path(f"{fname}.png")
            fig.savefig(path, bbox_inches="tight", dpi=100)
            plt.close(fig)
        session.chart_paths.append(path)
        return f"Chart saved: {path}"


class ScatterPlotTool(BaseTool):
    name = "scatter_plot"
    description = "Create a scatter plot (x_column vs y_column). Saves to outputs/. Choose format='png' or format='html'."

    def run(self, x_column: str, y_column: str, title: str = "", format: str = "png") -> str:
        df = _get_df()
        ensure_output_dir()
        fname = f"scatter_{x_column}_vs_{y_column}".replace(" ", "_")
        chart_title = title or f"{y_column} vs {x_column}"
        if format == "html":
            import plotly.express as px
            fig = px.scatter(df, x=x_column, y=y_column, title=chart_title)
            path = output_path(f"{fname}.html")
            fig.write_html(path)
        else:
            fig, ax = plt.subplots()
            ax.scatter(df[x_column], df[y_column], alpha=0.6)
            ax.set_title(chart_title)
            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            path = output_path(f"{fname}.png")
            fig.savefig(path, bbox_inches="tight", dpi=100)
            plt.close(fig)
        session.chart_paths.append(path)
        return f"Chart saved: {path}"


class HeatmapTool(BaseTool):
    name = "heatmap"
    description = "Create a correlation heatmap for all numeric columns. Provide title. Saves to outputs/. Choose format='png' or format='html'."

    def run(self, title: str = "Correlation Heatmap", format: str = "png") -> str:
        df = _get_df()
        numeric = df.select_dtypes(include=[np.number])
        if numeric.shape[1] < 2:
            return "Need at least 2 numeric columns for heatmap."
        ensure_output_dir()
        corr = numeric.corr()
        if format == "html":
            import plotly.express as px
            fig = px.imshow(corr, text_auto=".2f", title=title, color_continuous_scale="RdBu_r")
            path = output_path("heatmap.html")
            fig.write_html(path)
        else:
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
            plt.colorbar(im)
            ax.set_xticks(range(len(corr.columns)))
            ax.set_xticklabels(corr.columns, rotation=45, ha="right")
            ax.set_yticks(range(len(corr.columns)))
            ax.set_yticklabels(corr.columns)
            for i in range(len(corr.columns)):
                for j in range(len(corr.columns)):
                    ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
            ax.set_title(title)
            path = output_path("heatmap.png")
            fig.savefig(path, bbox_inches="tight", dpi=100)
            plt.close(fig)
        session.chart_paths.append(path)
        return f"Heatmap saved: {path}"


class HistogramTool(BaseTool):
    name = "histogram"
    description = "Create a histogram for a numeric column. Provide column name. Saves to outputs/. Choose format='png' or format='html'."

    def run(self, column: str, bins: int = 20, title: str = "", format: str = "png") -> str:
        df = _get_df()
        if column not in df.columns:
            return f"Column '{column}' not found. Available: {list(df.columns)}"
        ensure_output_dir()
        fname = f"hist_{column}".replace(" ", "_")
        chart_title = title or f"Distribution of {column}"
        data = df[column].dropna()
        if format == "html":
            import plotly.express as px
            fig = px.histogram(df, x=column, nbins=bins, title=chart_title)
            path = output_path(f"{fname}.html")
            fig.write_html(path)
        else:
            fig, ax = plt.subplots()
            ax.hist(data, bins=bins, edgecolor="white", alpha=0.8)
            ax.set_title(chart_title)
            ax.set_xlabel(column)
            ax.set_ylabel("Frequency")
            path = output_path(f"{fname}.png")
            fig.savefig(path, bbox_inches="tight", dpi=100)
            plt.close(fig)
        session.chart_paths.append(path)
        return f"Histogram saved: {path}"


class BoxPlotTool(BaseTool):
    name = "box_plot"
    description = "Create a box plot for a numeric column, optionally grouped by a category column. Saves to outputs/. Choose format='png' or format='html'."

    def run(self, value_column: str, group_column: str = "", title: str = "", format: str = "png") -> str:
        df = _get_df()
        ensure_output_dir()
        fname = f"box_{value_column}".replace(" ", "_")
        chart_title = title or f"Box Plot of {value_column}"
        if format == "html":
            import plotly.express as px
            if group_column and group_column in df.columns:
                fig = px.box(df, x=group_column, y=value_column, title=chart_title)
            else:
                fig = px.box(df, y=value_column, title=chart_title)
            path = output_path(f"{fname}.html")
            fig.write_html(path)
        else:
            fig, ax = plt.subplots()
            if group_column and group_column in df.columns:
                groups = df.groupby(group_column)[value_column].apply(list)
                ax.boxplot(
                    [np.array([v for v in g if pd.notna(v)]) for g in groups],
                    labels=list(groups.index)
                )
                ax.set_xlabel(group_column)
            else:
                data = df[value_column].dropna()
                ax.boxplot(data.values, labels=[value_column])
            ax.set_title(chart_title)
            ax.set_ylabel(value_column)
            path = output_path(f"{fname}.png")
            fig.savefig(path, bbox_inches="tight", dpi=100)
            plt.close(fig)
        session.chart_paths.append(path)
        return f"Box plot saved: {path}"


class PieChartTool(BaseTool):
    name = "pie_chart"
    description = "Create a pie chart showing proportion of values by category. Required: value_column, label_column. Saves to outputs/. Choose format='png' or format='html'."

    def run(self, value_column: str, label_column: str, title: str = "", format: str = "png") -> str:
        df = _get_df()
        ensure_output_dir()
        fname = f"pie_{label_column}".replace(" ", "_")
        chart_title = title or f"{value_column} by {label_column}"

        grouped = df.groupby(label_column)[value_column].sum()
        if format == "html":
            import plotly.express as px
            fig = px.pie(df, values=value_column, names=label_column, title=chart_title)
            path = output_path(f"{fname}.html")
            fig.write_html(path)
        else:
            fig, ax = plt.subplots()
            wedges, texts, autotexts = ax.pie(
                grouped.values, labels=grouped.index, autopct="%1.1f%%",
                startangle=90, pctdistance=0.75
            )
            for at in autotexts:
                at.set_fontsize(8)
            ax.set_title(chart_title)
            path = output_path(f"{fname}.png")
            fig.savefig(path, bbox_inches="tight", dpi=100)
            plt.close(fig)
        session.chart_paths.append(path)
        return f"Pie chart saved: {path}"


class RadarChartTool(BaseTool):
    name = "radar_chart"
    description = "Create a radar/spider chart for multi-dimension comparison. Provide one or more value_columns (comma-separated) and a group_column for categories. Saves to outputs/."

    def run(self, value_columns: str, group_column: str, title: str = "", format: str = "png") -> str:
        df = _get_df()
        ensure_output_dir()
        fname = f"radar_{group_column}".replace(" ", "_")
        chart_title = title or f"Radar Chart by {group_column}"

        cols = [c.strip() for c in value_columns.split(",") if c.strip()]
        cols = [c for c in cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
        if len(cols) < 3:
            return "Radar chart needs at least 3 valid numeric columns."

        categories = df[group_column].unique()
        if len(categories) > 8:
            categories = categories[:8]

        N = len(cols)
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        angles += angles[:1]

        if format == "html":
            import plotly.express as px
            fig = px.line_polar(df, r=cols[0], theta=group_column, line_close=True, title=chart_title)
            path = output_path(f"{fname}.html")
            fig.write_html(path)
        else:
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            for cat in categories:
                subset = df[df[group_column] == cat]
                values = [subset[c].mean() for c in cols]
                # Normalize to 0-1 range
                vmax = df[cols].max().max()
                vmin = df[cols].min().min()
                if vmax > vmin:
                    values = [(v - vmin) / (vmax - vmin) for v in values]
                values += values[:1]
                ax.fill(angles, values, alpha=0.15)
                ax.plot(angles, values, "o-", linewidth=2, label=str(cat))
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(cols, fontsize=8)
            ax.set_title(chart_title, pad=20)
            ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
            path = output_path(f"{fname}.png")
            fig.savefig(path, bbox_inches="tight", dpi=100)
            plt.close(fig)
        session.chart_paths.append(path)
        return f"Radar chart saved: {path}"


class AreaChartTool(BaseTool):
    name = "area_chart"
    description = "Create a stacked area chart for cumulative trend visualization. Provide x_column and one or more y_columns (comma-separated). Saves to outputs/."

    def run(self, x_column: str, y_columns: str, title: str = "", format: str = "png", stacked: bool = True) -> str:
        df = _get_df()
        ensure_output_dir()
        fname = f"area_{x_column}".replace(" ", "_")
        chart_title = title or f"Area Chart over {x_column}"

        y_cols = [c.strip() for c in y_columns.split(",") if c.strip()]
        y_cols = [c for c in y_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
        if not y_cols:
            return "No valid numeric y_columns found."

        x_data = df[x_column].astype(str) if not pd.api.types.is_numeric_dtype(df[x_column]) else df[x_column]

        if format == "html":
            import plotly.express as px
            fig = px.area(df, x=x_column, y=y_cols, title=chart_title)
            path = output_path(f"{fname}.html")
            fig.write_html(path)
        else:
            fig, ax = plt.subplots()
            if stacked:
                ax.stackplot(x_data, *[df[c] for c in y_cols], labels=y_cols, alpha=0.7)
            else:
                for c in y_cols:
                    ax.fill_between(range(len(df)), df[c], alpha=0.3, label=c)
            ax.set_title(chart_title)
            ax.set_xlabel(x_column)
            ax.legend(loc="upper left")
            plt.xticks(rotation=45)
            path = output_path(f"{fname}.png")
            fig.savefig(path, bbox_inches="tight", dpi=100)
            plt.close(fig)
        session.chart_paths.append(path)
        return f"Area chart saved: {path}"


class StackedBarTool(BaseTool):
    name = "stacked_bar"
    description = "Create a stacked bar chart comparing multiple numeric columns grouped by a category. Provide x_column and y_columns (comma-separated). Saves to outputs/."

    def run(self, x_column: str, y_columns: str, title: str = "", format: str = "png") -> str:
        df = _get_df()
        ensure_output_dir()
        fname = f"stackedbar_{x_column}".replace(" ", "_")
        chart_title = title or f"Stacked Bar by {x_column}"

        y_cols = [c.strip() for c in y_columns.split(",") if c.strip()]
        y_cols = [c for c in y_cols if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
        if len(y_cols) < 2:
            return "Stacked bar chart needs at least 2 valid numeric columns."

        x_labels = df[x_column].astype(str).values
        x_idx = np.arange(len(x_labels))
        width = 0.6

        if format == "html":
            import plotly.express as px
            fig = px.bar(df, x=x_column, y=y_cols, title=chart_title, barmode="stack")
            path = output_path(f"{fname}.html")
            fig.write_html(path)
        else:
            fig, ax = plt.subplots()
            bottom = np.zeros(len(df))
            for c in y_cols:
                ax.bar(x_idx, df[c].values, width, bottom=bottom, label=c, alpha=0.85)
                bottom += df[c].values
            ax.set_title(chart_title)
            ax.set_xlabel(x_column)
            ax.set_xticks(x_idx)
            ax.set_xticklabels(x_labels, rotation=45, ha="right")
            ax.legend()
            path = output_path(f"{fname}.png")
            fig.savefig(path, bbox_inches="tight", dpi=100)
            plt.close(fig)
        session.chart_paths.append(path)
        return f"Stacked bar chart saved: {path}"
