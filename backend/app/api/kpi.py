from fastapi import APIRouter, HTTPException

from app.schemas.kpi import (
    KPIGenerationRequest,
    KPIGenerationResponse
)

from app.agents.kpi_agent import KPIGenerationAgent

from app.services.dataset_service import DatasetService


router = APIRouter(
    prefix="/api/kpi",
    tags=["KPI"]
)

dataset_service = DatasetService()


@router.post(
    "/generate",
    response_model=KPIGenerationResponse
)
def generate_kpis(
    request: KPIGenerationRequest
):

    # -------------------------------------------------
    # 1. Get dataset
    # -------------------------------------------------

    dataset = dataset_service.get_dataset(
        request.dataset_id
    )

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found"
        )

    # -------------------------------------------------
    # 2. Check dataset analysis
    # -------------------------------------------------

    profile = dataset.get("profile")

    if not profile:
        raise HTTPException(
            status_code=400,
            detail=(
                "Dataset has not been analyzed yet. "
                "Analyze the dataset before generating KPIs."
            )
        )

    # -------------------------------------------------
    # 3. Create KPI agent
    # -------------------------------------------------

    agent = KPIGenerationAgent(profile)

    # -------------------------------------------------
    # 4. Generate KPIs
    # -------------------------------------------------

    try:

        kpis = agent.generate(
            request.prompt
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"KPI generation failed: {str(exc)}"
        )

    # -------------------------------------------------
    # 5. Return response
    # -------------------------------------------------

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "kpis": kpis
    }