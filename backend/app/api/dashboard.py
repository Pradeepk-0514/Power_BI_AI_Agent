from fastapi import APIRouter, HTTPException

from app.schemas.dashboard import (
    DashboardRequest,
    DashboardPlanResponse
)

from app.agents.dashboard_agent import (
    DashboardPlanningAgent
)

from app.services.dataset_service import (
    dataset_service
)

from app.agents.kpi_agent import (
    KPIGenerationAgent
)

from app.agents.visualization_agent import (
    VisualizationRecommendationAgent
)

from app.agents.chart_agent import (
    ChartConfigurationAgent
)

from app.agents.insight_agent import (
    InsightGenerationAgent
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


dashboard_agent = DashboardPlanningAgent()
visualization_agent = VisualizationRecommendationAgent()
chart_agent = ChartConfigurationAgent()
insight_agent = InsightGenerationAgent()


@router.post(
    "/plan",
    response_model=DashboardPlanResponse
)
def generate_dashboard_plan(
    request: DashboardRequest
):

    # ---------------------------------------------
    # 1. Get dataset
    # ---------------------------------------------

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

    # ---------------------------------------------
    # 2. Generate dashboard plan
    # ---------------------------------------------

    # These inputs will eventually come from
    # Modules 3.1, 3.2 and 4.2.

    kpis = []

    visualizations = []

    insights = []

    result = dashboard_agent.generate_plan(
        profile=profile,
        kpis=kpis,
        visualizations=visualizations,
        insights=insights,
        prompt=request.prompt
    )

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "dashboard_title": result[
            "dashboard_title"
        ],
        "description": result[
            "description"
        ],
        "pages": result[
            "pages"
        ]
    }