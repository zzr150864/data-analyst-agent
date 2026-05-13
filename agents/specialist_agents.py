from hello_agents import HelloAgentsLLM, SimpleAgent, ToolRegistry
from config import get_llm
from prompts.data_prompt import DATA_COLLECTION_PROMPT
from prompts.analysis_prompt import ANALYSIS_PROMPT
from prompts.visualization_prompt import VISUALIZATION_PROMPT
from prompts.report_prompt import REPORT_PROMPT
from tools.data_tools import LoadCSVTool, LoadExcelTool, GetDataInfoTool
from tools.db_tools import SQLQueryTool, ListTablesTool
from tools.api_tools import FetchAPITool, LoadURLCSVTool
from tools.analysis_tools import (
    DescriptiveStatsTool,
    CorrelationAnalysisTool,
    TrendDetectionTool,
    GroupByAnalysisTool,
)
from tools.visualization_tools import (
    BarChartTool,
    LineChartTool,
    ScatterPlotTool,
    HeatmapTool,
    HistogramTool,
    BoxPlotTool,
    PieChartTool,
    RadarChartTool,
    AreaChartTool,
    StackedBarTool,
)
from tools.report_tools import (
    GenerateMarkdownReportTool,
    GenerateHTMLReportTool,
    GeneratePDFReportTool,
)


def create_data_collection_agent() -> SimpleAgent:
    registry = ToolRegistry()
    registry.register_tools([
        LoadCSVTool(),
        LoadExcelTool(),
        GetDataInfoTool(),
        SQLQueryTool(),
        ListTablesTool(),
        FetchAPITool(),
        LoadURLCSVTool(),
    ])
    return SimpleAgent(
        name="DataCollector",
        llm=get_llm(),
        system_prompt=DATA_COLLECTION_PROMPT,
        tool_registry=registry,
        max_steps=8,
    )


def create_analysis_agent() -> SimpleAgent:
    registry = ToolRegistry()
    registry.register_tools([
        DescriptiveStatsTool(),
        CorrelationAnalysisTool(),
        TrendDetectionTool(),
        GroupByAnalysisTool(),
    ])
    return SimpleAgent(
        name="StatisticalAnalyst",
        llm=get_llm(),
        system_prompt=ANALYSIS_PROMPT,
        tool_registry=registry,
        max_steps=5,
    )


def create_visualization_agent() -> SimpleAgent:
    registry = ToolRegistry()
    registry.register_tools([
        BarChartTool(),
        LineChartTool(),
        ScatterPlotTool(),
        HeatmapTool(),
        HistogramTool(),
        BoxPlotTool(),
        PieChartTool(),
        RadarChartTool(),
        AreaChartTool(),
        StackedBarTool(),
    ])
    return SimpleAgent(
        name="VisualizationExpert",
        llm=get_llm(),
        system_prompt=VISUALIZATION_PROMPT,
        tool_registry=registry,
        max_steps=10,
    )


def create_report_agent() -> SimpleAgent:
    registry = ToolRegistry()
    registry.register_tools([
        GenerateMarkdownReportTool(),
        GenerateHTMLReportTool(),
        GeneratePDFReportTool(),
    ])
    return SimpleAgent(
        name="ReportWriter",
        llm=get_llm(),
        system_prompt=REPORT_PROMPT,
        tool_registry=registry,
        max_steps=6,
    )
