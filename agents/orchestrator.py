from typing import Callable, Optional
from hello_agents import HelloAgentsLLM, ToolRegistry, SimpleAgent
from config import get_llm
from prompts.orchestrator_prompt import ORCHESTRATOR_PROMPT
from agents.delegator_tools import (
    DataCollectionDelegator,
    AnalysisDelegator,
    VisualizationDelegator,
    ReportDelegator,
)
from agents.specialist_agents import (
    create_data_collection_agent,
    create_analysis_agent,
    create_visualization_agent,
    create_report_agent,
)


class DataAnalystOrchestrator:
    """Hub of the multi-agent data analysis system with progress callbacks."""

    def __init__(self, on_progress: Optional[Callable[[str, int], None]] = None):
        """
        Args:
            on_progress: Optional callback(stage_name, percent) for GUI progress.
        """
        self.llm = get_llm()
        self.on_progress = on_progress

        # Build delegator tool registry
        self.delegator_registry = ToolRegistry()
        self.delegator_registry.register_tools([
            DataCollectionDelegator(),
            AnalysisDelegator(),
            VisualizationDelegator(),
            ReportDelegator(),
        ])

        self.data_agent = None
        self.analysis_agent = None
        self.viz_agent = None
        self.report_agent = None

    def run(self, task: str) -> str:
        """Execute full analysis pipeline with progress reporting."""
        return self._pipeline(task)

    def _emit(self, stage: str, pct: int):
        if self.on_progress:
            self.on_progress(stage, pct)

    def _pipeline(self, task: str) -> str:
        """Direct pipeline: Plan -> Data -> Analysis -> Viz -> Report."""

        # Lazy init specialists
        if self.data_agent is None:
            self.data_agent = create_data_collection_agent()
            self.analysis_agent = create_analysis_agent()
            self.viz_agent = create_visualization_agent()
            self.report_agent = create_report_agent()

        # ── Step 0: Plan (quick, 1 LLM call) ──
        self._emit("Planning...", 5)
        import re
        file_match = re.search(r"['\"]?([^'\"]+\.(?:csv|xlsx|xls))['\"]?", task)

        # ── Step 1: Data Loading ──
        self._emit("Loading data...", 10)
        if file_match:
            data_task = f"Load and thoroughly inspect the data file at: {file_match.group(1)}"
        else:
            data_task = f"Load and inspect the data file. Task: {task}"
        data_result = self.data_agent.run(data_task)

        # ── Step 2: Statistical Analysis ──
        self._emit("Analyzing statistics...", 30)
        analysis_result = self.analysis_agent.run(
            f"Perform comprehensive statistical analysis: {task}"
        )

        # ── Step 3: Visualization ──
        self._emit("Creating charts...", 55)
        viz_result = self.viz_agent.run(
            f"Create 4-6 relevant charts for this analysis in png format. Task: {task}"
        )

        # ── Step 4: Report Generation ──
        self._emit("Generating reports...", 80)
        report_result = self.report_agent.run(
            f"Generate both Markdown and HTML reports with all findings.\n\n"
            f"Data Summary:\n{data_result}\n\n"
            f"Analysis Findings:\n{analysis_result}\n\n"
            f"Visualization Results:\n{viz_result}\n\n"
            f"Original Task: {task}"
        )

        self._emit("Complete", 95)

        return (
            f"## Analysis Complete\n\n"
            f"### Data Overview\n{data_result[:500]}...\n\n"
            f"### Statistical Analysis\n{analysis_result[:500]}...\n\n"
            f"### Visualizations\n{viz_result[:500]}...\n\n"
            f"### Reports\n{report_result}"
        )
