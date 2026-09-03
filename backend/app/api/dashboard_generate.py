from fastapi import APIRouter, HTTPException

from app.schemas.dashboard_generation import (
    DashboardGenerationRequest,
    DashboardGenerationResponse
)

from app.services.dataset_service import dataset_service

from app.agents.prompt_agent import (
    PromptUnderstandingAgent
)

from app.agents.analysis_plan_agent import (
    AnalysisPlanAgent
)

from app.agents.visualization_agent import (
    VisualizationRecommendationAgent
)

from app.agents.chart_configuration_agent import (
    ChartConfigurationAgent
)

from app.agents.dashboard_generation_agent import (
    DashboardGenerationAgent
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard Generation"]
)


@router.post(
    "/generate",
    response_model=DashboardGenerationResponse
)
def generate_dashboard(
    request: DashboardGenerationRequest
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
    # 2. Understand prompt
    # ---------------------------------------------

    prompt_agent = PromptUnderstandingAgent(
        profile
    )

    prompt_result = prompt_agent.understand(
        request.prompt
    )

    # ---------------------------------------------
    # 3. Generate analysis plan
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
    # 4. Generate visualization recommendations
    # ---------------------------------------------

    visualization_agent = (
        VisualizationRecommendationAgent()
    )

    visualizations = visualization_agent.generate(
        profile,
        analysis_plan
    )

    # ---------------------------------------------
    # 5. Configure charts
    # ---------------------------------------------

    chart_agent = ChartConfigurationAgent()

    chart_configurations = chart_agent.generate(
        profile,
        visualizations
    )

    # ---------------------------------------------
    # 6. Build dashboard layout
    # ---------------------------------------------

    dashboard_visuals = []

    for index, chart in enumerate(
        chart_configurations
    ):

        dashboard_visuals.append({
            "title": chart.get(
                "title",
                f"Visual {index + 1}"
            ),
            "visual_type": chart.get(
                "visual_type",
                "unknown"
            ),
            "x_axis": chart.get(
                "x_axis"
            ),
            "y_axis": chart.get(
                "y_axis"
            ),
            "position": {
                "x": (index % 2) * 600,
                "y": (index // 2) * 350
            },
            "width": 600,
            "height": 350
        })

    dashboard_layout = {
        "dashboard_title": (
            "Sales Performance Dashboard"
        ),
        "pages": [
            {
                "page_number": 1,
                "page_name": "Overview",
                "layout_type": "standard",
                "visuals": dashboard_visuals
            }
        ]
    }

    # ---------------------------------------------
    # 7. Generate final dashboard configuration
    # ---------------------------------------------

    generation_agent = (
        DashboardGenerationAgent()
    )

    result = generation_agent.generate(
        dashboard_layout
    )

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "dashboard_title": result[
            "dashboard_title"
        ],
        "status": result[
            "status"
        ],
        "pages": result[
            "pages"
        ]
    }