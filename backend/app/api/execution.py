from fastapi import APIRouter, HTTPException

from app.services.dataset_service import dataset_service
from app.schemas.execution import (
    ExecutionRequest,
    ExecutionResponse
)
from app.agents.execution_agent import DataExecutionAgent
from app.agents.prompt_agent import PromptUnderstandingAgent
from app.agents.analysis_plan_agent import AnalysisPlanAgent


router = APIRouter(
    prefix="/api/analysis",
    tags=["Analysis Execution"]
)

execution_agent = DataExecutionAgent()


@router.post(
    "/execute",
    response_model=ExecutionResponse
)
def execute_analysis(
    request: ExecutionRequest
):

    dataset = dataset_service.get_dataset(
        request.dataset_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    profile = dataset.get("profile")

    if profile is None:
        raise HTTPException(
            status_code=400,
            detail="Dataset has not been analyzed yet"
        )

    # Module 2.1
    prompt_agent = PromptUnderstandingAgent(
        profile
    )

    prompt_result = prompt_agent.understand(
        request.prompt
    )

    # Module 2.2
    plan_agent = AnalysisPlanAgent()

    plan_result = plan_agent.generate_plan(
        prompt_result
    )

    analysis_plan = plan_result.get(
        "analysis_plan",
        []
    )

    # Module 4.1
    try:

        results = execution_agent.execute(
            dataset["file_path"],
            analysis_plan
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Analysis execution failed: {str(exc)}"
        )

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "intent": plan_result.get(
            "intent",
            "business_analysis"
        ),
        "results": results
    }