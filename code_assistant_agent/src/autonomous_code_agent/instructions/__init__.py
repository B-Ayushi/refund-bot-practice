"""Load instruction templates packaged with the agents."""

from importlib.resources import files


def load_instruction(filename: str) -> str:
    """Return an instruction template from this package."""
    return files(__package__).joinpath(filename).read_text(encoding="utf-8")