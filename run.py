#!/usr/bin/env python3
"""Intelligent Data Analyst - Multi-Agent Data Analysis System

Usage:
    python run.py -f data/sales.csv -t "Analyze sales trends by region and product"
    python run.py -f data/survey.xlsx -t "Find correlations between age, income, and satisfaction"
    python run.py -f data/metrics.csv
"""

import argparse
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import OUTPUT_DIR
from session import session
from agents.orchestrator import DataAnalystOrchestrator
from utils.file_utils import validate_file_path, ensure_output_dir


def main():
    parser = argparse.ArgumentParser(
        description="Intelligent Data Analyst - Multi-Agent Data Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py -f data/sales.csv -t "Analyze monthly revenue trends and top products"
  python run.py -f data/survey.xlsx -t "Find correlations and create distribution charts"
  python run.py -f data/metrics.csv
        """,
    )
    parser.add_argument(
        "-f", "--file", required=True,
        help="Path to input data file (CSV or Excel)"
    )
    parser.add_argument(
        "-t", "--task",
        help="Analysis task description (if omitted, enters interactive mode)"
    )
    parser.add_argument(
        "--format", choices=["md", "html", "both"], default="both",
        help="Report output format (default: both)"
    )
    parser.add_argument(
        "--chart-format", choices=["png", "html"], default="png",
        help="Chart output format (default: png)"
    )

    args = parser.parse_args()

    # Validate input
    try:
        file_path = validate_file_path(args.file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    ensure_output_dir()
    session.reset()

    # Build task
    if args.task:
        task = args.task
    else:
        print(f"\nData file: {file_path}")
        task = input("What analysis would you like to perform? ").strip()
        if not task:
            print("Error: No analysis task provided.", file=sys.stderr)
            sys.exit(1)

    chart_fmt = args.chart_format
    report_fmt = "Markdown and HTML" if args.format == "both" else args.format.upper()

    full_task = (
        f"Analyze the data file at '{file_path}'. "
        f"Step 1: use collect_and_inspect_data with file_path='{file_path}' to load it. "
        f"Step 2: use analyze_data to perform this analysis: {task}. "
        f"Step 3: use create_visualizations to create charts in {chart_fmt} format for: {task}. "
        f"Step 4: use generate_report to produce a {report_fmt} report with all findings. "
    )

    print(f"\n{'='*60}")
    print(f"Starting Intelligent Data Analyst...")
    print(f"  File:   {file_path}")
    print(f"  Task:   {task}")
    print(f"  Charts: {chart_fmt}")
    print(f"  Report: {report_fmt}")
    print(f"{'='*60}\n")

    try:
        orchestrator = DataAnalystOrchestrator()
        result = orchestrator.run(full_task)
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print(result)
        print(f"\nOutput files:")
        for p in session.chart_paths:
            print(f"  Chart:  {p}")
        for p in session.report_paths:
            print(f"  Report: {p}")
    except Exception as e:
        print(f"\nError during analysis: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
