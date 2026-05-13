from pathlib import Path
from config import OUTPUT_DIR

VALID_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def validate_file_path(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower() not in VALID_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{path.suffix}'. "
            f"Supported: {', '.join(VALID_EXTENSIONS)}"
        )
    return str(path.resolve())


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def output_path(filename: str) -> str:
    return str(OUTPUT_DIR / filename)
