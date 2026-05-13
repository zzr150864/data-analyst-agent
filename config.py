import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from hello_agents import HelloAgentsLLM

# When bundled as .exe, base dir = exe location; otherwise = project dir
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent

ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)

LLM_API_KEY = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "deepseek-chat")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "120"))

OUTPUT_DIR = BASE_DIR / "outputs"
CHART_DEFAULT_FORMAT = os.getenv("CHART_FORMAT", "png")
CHART_DPI = int(os.getenv("CHART_DPI", "100"))

_llm_instance = None

def get_llm() -> HelloAgentsLLM:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = HelloAgentsLLM(
            model=LLM_MODEL_ID,
            apiKey=LLM_API_KEY,
            baseUrl=LLM_BASE_URL,
            timeout=LLM_TIMEOUT,
        )
    return _llm_instance
