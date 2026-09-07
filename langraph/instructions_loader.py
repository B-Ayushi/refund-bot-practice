from pathlib import Path


INSTRUCTIONS_DIR = Path(__file__).resolve().parent / "instructions"


def load_instruction(name):
    return (INSTRUCTIONS_DIR / f"{name}.md").read_text(encoding="utf-8")
