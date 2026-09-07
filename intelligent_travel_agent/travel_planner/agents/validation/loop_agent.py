from travel_planner.workflows.validation_workflow import ValidationOutcome, ValidationWorkflow

class ValidationLoopAgent:
    """Compatibility facade; termination remains owned by ValidationWorkflow."""
    def __init__(self, workflow: ValidationWorkflow | None = None) -> None:
        self.workflow = workflow or ValidationWorkflow()

    async def run(self, request: object) -> ValidationOutcome:
        return await self.workflow.run(request)  # type: ignore[arg-type]
