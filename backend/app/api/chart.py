from fastapi import APIRouter, HTTPException

from app.schemas.chart import (
    ChartConfigurationRequest,
    ChartConfigurationResponse
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

from app.agents.chart_agent import (
    ChartConfigurationAgent
)

from app.services.dataset_service import (
    dataset_service
)


router = APIRouter(
    prefix="/api/chart",
    tags=["Chart Configuration"]
)


visualization_agent = (
    VisualizationRecommendationAgent()
)

chart_agent = ChartConfigurationAgent()


@router.post(
    "/configure",
    response_model=ChartConfigurationResponse
)
def configure_charts(
    request: ChartConfigurationRequest
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

    # ---------------------------------------------
    # Module 3.3
    # Chart Configuration
    # ---------------------------------------------

    charts = chart_agent.generate(
        profile,
        visualizations
    )

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "charts": charts
    }