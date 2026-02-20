from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str) -> str:
    """Load a prompt template by filename (without extension). Supports .md and .txt."""
    for ext in (".md", ".txt"):
        path = _PROMPTS_DIR / f"{name}{ext}"
        if path.exists():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Prompt '{name}' not found in {_PROMPTS_DIR}")
