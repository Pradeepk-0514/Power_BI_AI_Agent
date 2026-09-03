from fastapi import APIRouter, HTTPException

from app.services.dataset_service import dataset_service

from app.schemas.insight import (
    InsightRequest,
    InsightResponse
)

from app.agents.prompt_agent import (
    PromptUnderstandingAgent
)

from app.agents.analysis_plan_agent import (
    AnalysisPlanAgent
)

from app.agents.execution_agent import (
    DataExecutionAgent
)

from app.agents.insight_agent import (
    InsightGenerationAgent
)


router = APIRouter(
    prefix="/api/insight",
    tags=["Insight Generation"]
)


execution_agent = DataExecutionAgent()
insight_agent = InsightGenerationAgent()


@router.post(
    "/generate",
    response_model=InsightResponse
)
def generate_insights(
    request: InsightRequest
):

    # -----------------------------------------
    # Get dataset
    # -----------------------------------------

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

    # -----------------------------------------
    # Module 2.1
    # Prompt Understanding
    # -----------------------------------------

    prompt_agent = PromptUnderstandingAgent(
        profile
    )

    prompt_result = prompt_agent.understand(
        request.prompt
    )

    # -----------------------------------------
    # Module 2.2
    # Analysis Plan
    # -----------------------------------------

    plan_agent = AnalysisPlanAgent()

    plan_result = plan_agent.generate_plan(
        prompt_result
    )

    analysis_plan = plan_result.get(
        "analysis_plan",
        []
    )

    # -----------------------------------------
    # Module 4.1
    # Execute Analysis
    # -----------------------------------------

    try:

        execution_results = execution_agent.execute(
            dataset["file_path"],
            analysis_plan
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Analysis execution failed: {str(exc)}"
        )

    # -----------------------------------------
    # Module 4.2
    # Generate Insights
    # -----------------------------------------

    try:

        insights = insight_agent.generate(
            execution_results
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Insight generation failed: {str(exc)}"
        )

    # -----------------------------------------
    # Response
    # -----------------------------------------

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "intent": plan_result.get(
            "intent",
            "business_analysis"
        ),
        "insights": insights
    }