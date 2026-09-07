"""Public API for the autonomous code improvement workflow."""

from .agents.refactorer import CodeRefactorerAgent
from .agents.reviewer import CodeReviewerAgent
from .agents.writer import CodeWriterAgent
from .models.artifacts import CodeArtifact, ReviewResult, WorkflowResult
from .workflow.improvement_workflow import CodeImprovementWorkflow

root_agent = CodeImprovementWorkflow()

__all__ = [
    "CodeArtifact",
    "CodeImprovementWorkflow",
    "CodeRefactorerAgent",
    "CodeReviewerAgent",
    "CodeWriterAgent",
    "ReviewResult",
    "WorkflowResult",
    "root_agent",
]