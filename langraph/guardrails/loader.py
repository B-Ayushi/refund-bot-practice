from pathlib import Path


GUARDRAILS_DIR = Path(__file__).resolve().parent


def load_guardrail(folder, name):
    return (GUARDRAILS_DIR / folder / f"{name}.md").read_text(encoding="utf-8")
