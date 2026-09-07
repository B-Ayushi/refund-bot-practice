from autonomous_code_agent import (
    CodeImprovementWorkflow,
    CodeRefactorerAgent,
    CodeReviewerAgent,
    CodeWriterAgent,
)


def test_agents_are_concrete_adk_llm_agents() -> None:
    writer = CodeWriterAgent()
    reviewer = CodeReviewerAgent()
    refactorer = CodeRefactorerAgent()

    assert writer.name == "code_writer"
    assert reviewer.name == "code_reviewer"
    assert refactorer.name == "code_refactorer"
    assert writer.output_key == "generated_code"
    assert reviewer.output_key == "review_result"
    assert refactorer.output_key == "generated_code"


def test_workflow_has_writer_loop_and_quality_gate() -> None:
    workflow = CodeImprovementWorkflow(max_iterations=3)

    assert workflow.name == "autonomous_code_improvement"
    assert workflow.sub_agents[0].name == "generation_and_quality"
    assert workflow.sub_agents[0].sub_agents[1].name == "code_quality_loop"
