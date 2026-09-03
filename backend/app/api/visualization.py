from fastapi import APIRouter, HTTPException

from app.schemas.visualization import (
    VisualizationGenerationRequest,
    VisualizationGenerationResponse
)

from app.agents.prompt_agent import (
    PromptUnderstandingAgent
)

from app.agents.analysis_plan_agent import (
    AnalysisPlanAgent
)

from app.agents.visualization_agent import (
    VisualizationRecommendationAgent
)

from app.services.dataset_service import (
    dataset_service
)


router = APIRouter(
    prefix="/api/visualization",
    tags=["Visualization"]
)


visualization_agent = (
    VisualizationRecommendationAgent()
)


@router.post(
    "/recommend",
    response_model=VisualizationGenerationResponse
)
def recommend_visualizations(
    request: VisualizationGenerationRequest
):

    # ---------------------------------------------
    # Get dataset
    # ---------------------------------------------

    dataset = dataset_service.get_dataset(
        request.dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # ---------------------------------------------
    # Get dataset profile
    # ---------------------------------------------

    profile = dataset.get("profile")

    if profile is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "Dataset has not been analyzed yet"
            )
        )

    # ---------------------------------------------
    # Module 2.1
    # Prompt Understanding
    # ---------------------------------------------

    prompt_agent = PromptUnderstandingAgent(
        profile
    )

    prompt_result = prompt_agent.understand(
        request.prompt
    )

    # ---------------------------------------------
    # Module 2.2
    # Analysis Plan
    # ---------------------------------------------

    plan_agent = AnalysisPlanAgent()

    plan_result = plan_agent.generate_plan(
        prompt_result
    )

    analysis_plan = plan_result.get(
        "analysis_plan",
        []
    )

    # ---------------------------------------------
    # Module 3.2
    # Visualization Recommendation
    # ---------------------------------------------

    visualizations = (
        visualization_agent.generate(
            profile,
            analysis_plan
        )
    )

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "visualizations": visualizations
    }