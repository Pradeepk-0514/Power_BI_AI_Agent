from fastapi import FastAPI, HTTPException

from app.api.upload import router as upload_router
from app.api.powerbi import router as powerbi_router

from app.schemas.prompt import (
    PromptRequest,
    PromptAnalysisResponse
)

from app.agents.prompt_agent import (
    PromptUnderstandingAgent
)

from app.services.dataset_service import dataset_service

from app.schemas.analysis import (
    AnalysisPlanRequest,
    AnalysisPlanResponse
)

from app.agents.analysis_plan_agent import (
    AnalysisPlanAgent
)

from app.schemas.validation import (
    ValidationRequest,
    ValidationResponse
)

from app.agents.validation_agent import (
    PromptValidationAgent
)

from app.schemas.kpi import (
    KPIGenerationRequest,
    KPIGenerationResponse
)

from app.agents.kpi_agent import (
    KPIGenerationAgent
)

from app.api.visualization import (
    router as visualization_router
)

from app.api.chart import (
    router as chart_router
)

from app.schemas.execution import (
    ExecutionRequest,
    ExecutionResponse
)

from app.agents.execution_agent import (
    DataExecutionAgent
)

from app.api.insight import router as insight_router

from app.api.dashboard import router as dashboard_router

from app.api.dashboard_layout import (
    router as dashboard_layout_router
)

from app.api.dashboard_generate import (
    router as dashboard_generate_router
)

from app.api.powerbi_project import (
    router as powerbi_project_router
)

execution_agent = DataExecutionAgent()


app = FastAPI(
    title="Prompt-Driven AI Agent",
    description=(
        "AI-powered data analytics and "
        "Power BI dashboard generation system"
    ),
    version="1.0.0"
)

app.include_router(upload_router)

app.include_router(powerbi_router)

app.include_router(
    visualization_router
)

app.include_router(upload_router)

app.include_router(
    visualization_router
)

app.include_router(
    chart_router
)

app.include_router(upload_router)
app.include_router(insight_router)

app.include_router(upload_router)
app.include_router(dashboard_router)

app.include_router(
    dashboard_layout_router
)

app.include_router(
    dashboard_generate_router
)

app.include_router(
    powerbi_project_router
)

# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------

app.include_router(upload_router)


# ---------------------------------------------------------
# Root
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "AI Dashboard Backend Running"
    }


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "Backend is running"
    }


# =========================================================
# MODULE 2.1 — Prompt Understanding
# =========================================================

@app.post(
    "/api/prompt/analyze",
    response_model=PromptAnalysisResponse
)
def analyze_prompt(
    request: PromptRequest
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

    agent = PromptUnderstandingAgent(profile)

    result = agent.understand(
        request.prompt
    )

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "intent": result["intent"],
        "tasks": result["tasks"]
    }


# =========================================================
# MODULE 2.2 — Analysis Plan
# =========================================================

@app.post(
    "/api/analysis/plan",
    response_model=AnalysisPlanResponse
)
def generate_analysis_plan(
    request: AnalysisPlanRequest
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

    # Step 1: Understand prompt

    prompt_agent = PromptUnderstandingAgent(profile)

    prompt_result = prompt_agent.understand(
        request.prompt
    )

    # Step 2: Generate analysis plan

    plan_agent = AnalysisPlanAgent()

    plan_result = plan_agent.generate_plan(
        prompt_result
    )

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "intent": plan_result["intent"],
        "analysis_plan": plan_result["analysis_plan"]
    }


# =========================================================
# MODULE 2.3 — Prompt Validation
# =========================================================

@app.post(
    "/api/prompt/validate",
    response_model=ValidationResponse
)
def validate_prompt(
    request: ValidationRequest
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

    # Step 1: Understand prompt

    prompt_agent = PromptUnderstandingAgent(profile)

    prompt_result = prompt_agent.understand(
        request.prompt
    )

    # Step 2: Generate analysis plan

    plan_agent = AnalysisPlanAgent()

    plan_result = plan_agent.generate_plan(
        prompt_result
    )

    # Step 3: Validate plan

    validation_agent = PromptValidationAgent()

    validation_result = validation_agent.validate(
        profile,
        plan_result["analysis_plan"],
        request.prompt
    )

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "valid": validation_result["valid"],
        "issues": validation_result["issues"]
    }


# =========================================================
# MODULE 3.1 — KPI Generation
# =========================================================

@app.post(
    "/api/kpi/generate",
    response_model=KPIGenerationResponse
)
def generate_kpis(
    request: KPIGenerationRequest
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

    profile = dataset.get("profile")

    if profile is None:
        raise HTTPException(
            status_code=400,
            detail="Dataset has not been analyzed yet"
        )

    # -----------------------------------------------------
    # 3. Create KPI Agent using dataset profile
    # -----------------------------------------------------

    kpi_agent = KPIGenerationAgent(
        profile
    )

    # -----------------------------------------------------
    # 4. Generate KPIs from prompt
    # -----------------------------------------------------

    try:

        kpis = kpi_agent.generate(
            request.prompt
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"KPI generation failed: {str(exc)}"
        )

    # -----------------------------------------------------
    # 5. Return response
    # -----------------------------------------------------

    return {
        "dataset_id": request.dataset_id,
        "prompt": request.prompt,
        "kpis": kpis
    }

@app.post(
    "/api/analysis/execute",
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

    # -------------------------------------------------
    # Step 1: Understand prompt
    # -------------------------------------------------

    prompt_agent = PromptUnderstandingAgent(
        profile
    )

    prompt_result = prompt_agent.understand(
        request.prompt
    )

    # -------------------------------------------------
    # Step 2: Generate analysis plan
    # -------------------------------------------------

    plan_agent = AnalysisPlanAgent()

    plan_result = plan_agent.generate_plan(
        prompt_result
    )

    analysis_plan = plan_result.get(
        "analysis_plan",
        []
    )

    # -------------------------------------------------
    # Step 3: Execute analysis
    # -------------------------------------------------

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