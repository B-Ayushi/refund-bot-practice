"""Entry point for the autonomous code improvement agent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from autonomous_code_agent import CodeImprovementWorkflow


root_agent = CodeImprovementWorkflow()