"""Data models for generated code and workflow results."""

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True, slots=True)
class CodeArtifact:
    requirement: str
    code: str
    language: str = "python"


@dataclass(frozen=True, slots=True)
class ReviewResult:
    quality_score: int
    feedback: str = ""
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WorkflowResult:
    artifact: CodeArtifact
    reviews: tuple[ReviewResult, ...]
    iterations: int
    quality_score: int