from fastapi import APIRouter, HTTPException

from app.schemas.dashboard import (
    DashboardLayoutRequest,
    DashboardLayoutResponse
)

from app.services.dataset_service import dataset_service
from app.agents.prompt_agent import PromptUnderstandingAgent
from app.agents.analysis_plan_agent import AnalysisPlanAgent

router = APIRouter()


@router.post(
    "/api/dashboard/layout",
    response_model=DashboardLayoutResponse
)
def generate_dashboard_layout(
    request: DashboardLayoutRequest
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

    # ---------------------------------------------
    # Step 1: Understand prompt
    # ---------------------------------------------

    prompt_agent = PromptUnderstandingAgent(profile)

    prompt_result = prompt_agent.understand(
        request.prompt
    )

    # ---------------------------------------------
    # Step 2: Generate analysis plan
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
    # Step 3: Create dashboard layout
    # ---------------------------------------------

    pages = []

    visuals = []

    for step in analysis_plan:

        metric = step.get("metric")
        group_by = step.get("group_by")
        aggregation = step.get("aggregation")
        analysis_type = step.get("analysis_type")
        time_granularity = step.get(
            "time_granularity"
        )

        if analysis_type == "trend":

            visuals.append({
                "title": (
                    f"{time_granularity.title()} "
                    f"{metric} Trend"
                ),
                "visual_type": "line_chart",

                "x_axis": {
                    "field": group_by,
                    "granularity": time_granularity
                },

                "y_axis": {
                    "field": metric,
                    "aggregation": aggregation
                },

                "position": {
                    "x": 0,
                    "y": 0
                },

                "width": 600,
                "height": 350
            })

        elif analysis_type == "comparison":

            visuals.append({
                "title": (
                    f"{metric} by {group_by}"
                ),
                "visual_type": "bar_chart",

                "x_axis": {
                    "field": group_by
                },

                "y_axis": {
                    "field": metric,
                    "aggregation": aggregation
                },

                "position": {
                    "x": 600,
                    "y": 0
                },

                "width": 600,
                "height": 350
            })

    pages.append({
        "page_number": 1,
        "page_name": "Overview",
        "layout_type": "standard",
        "visuals": visuals
    })

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "dashboard_title": "Sales Performance Dashboard",
        "pages": pages
    }