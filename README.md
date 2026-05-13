# Intelligent Data Analyst — 智能数据分析师

基于多智能体架构的 AI 数据分析系统。自动加载数据、统计分析、生成可视化图表、撰写 Markdown/HTML/PDF 报告。支持桌面 GUI 和命令行两种使用方式。

## 架构

采用 **Hub-and-Spoke（中心-辐条）模式**，1 个编排器协调 4 个专员 Agent：

```
用户输入 → DataAnalystOrchestrator → DataAgent → AnalysisAgent → VisualizationAgent → ReportAgent
```

| Agent | 职责 | 工具数 |
|-------|------|--------|
| DataCollectionAgent | 加载 CSV/Excel/SQL/API 数据，探查结构 | 7 |
| AnalysisAgent | 描述统计、相关性、趋势检测、分组聚合 | 4 |
| VisualizationAgent | 生成 10 种图表 (PNG/HTML) | 10 |
| ReportAgent | 撰写 Markdown/HTML/PDF 报告 | 3 |

## 功能特性

- 10 种图表：柱状图、折线图、散点图、热力图、直方图、箱线图、饼图、雷达图、面积图、堆叠柱状图
- 7 种数据源：CSV、Excel、SQLite、MySQL、REST API、URL CSV、数据库查询
- 3 种报告格式：Markdown、HTML（带 CSS 样式）、PDF（嵌入图表）
- 桌面 GUI（tkinter）：文件选择、实时进度、图表缩略图预览
- 命令行 CLI：适合脚本和自动化
- PyInstaller 打包为独立 `.exe`（无需安装 Python）

## 快速开始

### 1. 安装依赖

```bash
pip install httpx pandas matplotlib openpyxl python-dotenv numpy
# 可选：pip install plotly（HTML 交互图表）、scikit-learn（趋势检测）
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env 填入 LLM API Key（支持 OpenAI 兼容 API，默认 DeepSeek）
```

### 3. 运行

**桌面 GUI**：
```bash
python gui_app.py
```

**命令行**：
```bash
python run.py -f data/sales.csv -t "分析各区域销售趋势、利润最高的产品类别、促销效果对比"
```

### 4. 打包为 .exe（可选）

```bash
pip install pyinstaller
python build_exe.py
# 输出: dist/DataAnalyst.exe
```

将 `.env` 文件放在 `.exe` 同目录即可运行。

## 项目结构

```
data-analyst-agent/
├── hello_agents/           # 自建 Agent 框架核心
│   └── core.py             # HelloAgentsLLM, BaseTool, ToolRegistry, Agent 类
├── agents/                 # 多智能体编排
│   ├── orchestrator.py     # DataAnalystOrchestrator
│   ├── specialist_agents.py # 4 个专员 Agent 工厂
│   └── delegator_tools.py   # Agent → Tool 包装器
├── tools/                  # 24 个分析工具
│   ├── data_tools.py       # 文件数据源
│   ├── db_tools.py         # 数据库数据源
│   ├── api_tools.py        # API/URL 数据源
│   ├── analysis_tools.py   # 统计分析
│   ├── visualization_tools.py  # 10 种图表
│   └── report_tools.py     # Markdown/HTML/PDF 报告
├── prompts/                # Agent 系统提示词
├── gui/                    # 桌面 GUI 组件
├── gui_app.py              # GUI 入口
├── run.py                  # CLI 入口
├── build_exe.py            # PyInstaller 打包脚本
├── data/sales.csv          # 样本数据
└── outputs/                # 输出目录
```

## 工具速查

| 工具 | 类型 | 说明 |
|------|------|------|
| `load_csv` / `load_excel` | 数据源 | 加载本地文件 |
| `load_url_csv` / `fetch_api_data` | 数据源 | URL/API 获取数据 |
| `query_database` / `list_tables` | 数据源 | SQL 查询（SQLite/MySQL） |
| `get_data_info` | 数据源 | 数据探查摘要 |
| `descriptive_stats` | 分析 | 描述统计 + 偏度 + 峰度 |
| `correlation_analysis` | 分析 | 相关性矩阵 + TOP5 |
| `trend_detection` | 分析 | 线性回归趋势检测 |
| `groupby_analysis` | 分析 | 分组聚合 |
| `bar_chart` / `stacked_bar` | 图表 | 柱状图 / 堆叠柱状图 |
| `line_chart` / `area_chart` | 图表 | 折线图 / 面积图 |
| `scatter_plot` / `heatmap` | 图表 | 散点图 / 热力图 |
| `histogram` / `box_plot` | 图表 | 直方图 / 箱线图 |
| `pie_chart` / `radar_chart` | 图表 | 饼图 / 雷达图 |
| `generate_markdown_report` | 报告 | Markdown 报告 |
| `generate_html_report` | 报告 | HTML 报告（带样式） |
| `generate_pdf_report` | 报告 | PDF 报告（python-docx） |

## 技术栈

- Python 3.8+
- 自建轻量 Agent 框架（hello_agents，兼容 hello-agents 设计）
- httpx（OpenAI 兼容 API 调用）、matplotlib + plotly（可视化）、pandas + numpy（数据处理）
- tkinter + ttk（桌面 GUI）、PyInstaller（打包）
- SQLAlchemy + PyMySQL（数据库）、python-docx + docx2pdf（PDF）

## License

MIT
