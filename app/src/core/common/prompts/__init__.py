from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str, base_dir: Path | None = None) -> str:
    """Load a prompt template by filename (without extension). Supports .md and .txt.
    If base_dir is given, look there; otherwise use common/prompts (shared templates).
    """
    root = base_dir if base_dir is not None else _PROMPTS_DIR
    for ext in (".md", ".txt"):
        path = root / f"{name}{ext}"
        if path.exists():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Prompt '{name}' not found in {root}")
