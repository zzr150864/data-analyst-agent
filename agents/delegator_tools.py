from hello_agents import BaseTool
from agents.specialist_agents import (
    create_data_collection_agent,
    create_analysis_agent,
    create_visualization_agent,
    create_report_agent,
)


class DataCollectionDelegator(BaseTool):
    name = "collect_and_inspect_data"
    description = "Load and inspect a data file (CSV/Excel). Provide the file_path to the data file. Returns data summary, schema info, and quality report."

    def run(self, file_path: str) -> str:
        agent = create_data_collection_agent()
        result = agent.run(f"Load and thoroughly inspect the data file at: {file_path}")
        return result


class AnalysisDelegator(BaseTool):
    name = "analyze_data"
    description = "Perform statistical analysis on the loaded data. Provide instructions describing what analysis to perform (e.g., 'compute descriptive statistics, correlations, and trends'). Returns analysis findings."

    def run(self, instructions: str) -> str:
        agent = create_analysis_agent()
        result = agent.run(instructions)
        return result


class VisualizationDelegator(BaseTool):
    name = "create_visualizations"
    description = "Create charts and visualizations for the data. Provide instructions specifying which charts to create and what to visualize. Returns paths to saved chart files and descriptions."

    def run(self, instructions: str) -> str:
        agent = create_visualization_agent()
        result = agent.run(instructions)
        return result


class ReportDelegator(BaseTool):
    name = "generate_report"
    description = "Generate the final analysis report in Markdown and HTML formats. Provide the report title and all analysis findings, chart descriptions, and conclusions. Returns paths to saved report files."

    def run(self, instructions: str) -> str:
        agent = create_report_agent()
        result = agent.run(instructions)
        return result
