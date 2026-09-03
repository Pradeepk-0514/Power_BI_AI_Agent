from fastapi import APIRouter, HTTPException

from app.schemas.powerbi import (
    PowerBIProjectRequest,
    PowerBIProjectResponse
)

from app.services.dataset_service import dataset_service

from app.agents.dashboard_generation_agent import (
    DashboardGenerationAgent
)

from app.agents.powerbi_project_agent import (
    PowerBIProjectGenerationAgent
)


router = APIRouter(
    prefix="/api/powerbi",
    tags=["Power BI"]
)


# =========================================================
# AGENTS
# =========================================================

dashboard_agent = DashboardGenerationAgent()

powerbi_agent = PowerBIProjectGenerationAgent()


# =========================================================
# POWER BI PROJECT GENERATION
# =========================================================

@router.post(
    "/generate",
    response_model=PowerBIProjectResponse
)
def generate_powerbi_project(
    request: PowerBIProjectRequest
):

    # -----------------------------------------------------
    # 1. Get dataset
    # -----------------------------------------------------

    dataset = dataset_service.get_dataset(
        request.dataset_id
    )

    if dataset is None:

        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # -----------------------------------------------------
    # 2. Get dataset profile
    # -----------------------------------------------------

    profile = dataset.get(
        "profile"
    )

    if profile is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "Dataset has not been analyzed yet"
            )
        )

    # -----------------------------------------------------
    # 3. Generate dashboard configuration
    # -----------------------------------------------------

    dashboard_result = dashboard_agent.generate(
        profile,
        request.prompt
    )

    if not dashboard_result:

        raise HTTPException(
            status_code=500,
            detail=(
                "Dashboard generation failed"
            )
        )

    # -----------------------------------------------------
    # 4. Generate Power BI project
    # -----------------------------------------------------

    project_result = powerbi_agent.generate(
        profile,
        dashboard_result
    )

    # -----------------------------------------------------
    # 5. Return project
    # -----------------------------------------------------

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "project_name": project_result[
            "project_name"
        ],
        "status": project_result[
            "status"
        ],
        "project_type": project_result[
            "project_type"
        ],
        "files": project_result[
            "files"
        ]
    }