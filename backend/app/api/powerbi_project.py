from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List

from app.schemas.powerbi_project import (
    PowerBIProjectRequest,
    PowerBIProjectResponse
)

from app.services.dataset_service import (
    dataset_service
)

from app.services.powerbi_project_builder import (
    PowerBIProjectBuilder
)

from app.agents.powerbi_project_agent import (
    PowerBIProjectGenerationAgent
)

from app.agents.dashboard_plan_agent import (
    DashboardPlanningAgent
)

from app.agents.dashboard_layout_agent import (
    DashboardLayoutAgent
)

from app.agents.analysis_plan_agent import (
    AnalysisPlanAgent
)

from app.agents.visualization_agent import (
    VisualizationRecommendationAgent
)

from app.agents.insight_agent import (
    InsightGenerationAgent
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api/powerbi",
    tags=["Power BI Project Generation"]
)


# =========================================================
# AGENT INSTANCES
# =========================================================

powerbi_agent = PowerBIProjectGenerationAgent()

planning_agent = DashboardPlanningAgent()

layout_agent = DashboardLayoutAgent()

analysis_plan_agent = AnalysisPlanAgent()

visualization_agent = VisualizationRecommendationAgent()

insight_agent = InsightGenerationAgent()

project_builder = PowerBIProjectBuilder()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def _get_profile(
    dataset: Dict[str, Any]
) -> Dict[str, Any]:

    profile = dataset.get("profile")

    if profile is None:
        raise HTTPException(
            status_code=400,
            detail="Dataset has not been analyzed yet."
        )

    return profile


def _get_kpis(
    profile: Dict[str, Any]
) -> List[Dict[str, Any]]:

    """
    Generate basic KPI definitions from the
    numeric columns in the dataset profile.

    This keeps the project generation pipeline
    functional even when a separate KPI agent
    is not being used.
    """

    numeric_columns = profile.get(
        "numeric_columns",
        []
    )

    kpis = []

    for column in numeric_columns[:4]:

        column_lower = column.lower()

        if "sales" in column_lower:
            kpi_name = "Total Sales"

        elif "profit" in column_lower:
            kpi_name = "Total Profit"

        elif "quantity" in column_lower:
            kpi_name = "Total Quantity"

        elif "revenue" in column_lower:
            kpi_name = "Total Revenue"

        else:
            kpi_name = f"Total {column}"

        kpis.append({
            "name": kpi_name,
            "metric": column,
            "aggregation": "sum",
            "description": (
                f"Total value of {column} "
                "across all records."
            ),
            "business_meaning": (
                f"Measures the overall "
                f"{column} performance."
            )
        })

    return kpis


def _normalize_analysis_plan(
    analysis_plan_result: Any
) -> List[Dict[str, Any]]:

    """
    Converts different possible analysis-plan
    response structures into a simple list.

    Expected final format:

    [
        {
            "metric": "Sales",
            "aggregation": "sum",
            "group_by": "Order_Date",
            "time_granularity": "month",
            "analysis_type": "trend"
        }
    ]
    """

    if isinstance(
        analysis_plan_result,
        dict
    ):

        plan = analysis_plan_result.get(
            "analysis_plan",
            []
        )

    elif isinstance(
        analysis_plan_result,
        list
    ):

        plan = analysis_plan_result

    else:

        return []

    if not isinstance(
        plan,
        list
    ):

        return []

    return plan


def _normalize_execution_results(
    execution_results: Any
) -> List[Dict[str, Any]]:

    """
    Ensures InsightGenerationAgent receives
    a list of dictionaries.
    """

    if execution_results is None:
        return []

    if isinstance(
        execution_results,
        list
    ):

        return [
            item
            for item in execution_results
            if isinstance(item, dict)
        ]

    return []


# =========================================================
# MAIN ENDPOINT
# =========================================================

@router.post(
    "/project",
    response_model=PowerBIProjectResponse
)
def generate_powerbi_project(
    request: PowerBIProjectRequest
):

    try:

        # =================================================
        # 1. GET DATASET
        # =================================================

        dataset = dataset_service.get_dataset(
            request.dataset_id
        )

        if dataset is None:

            raise HTTPException(
                status_code=404,
                detail="Dataset not found."
            )


        # =================================================
        # 2. GET DATASET PROFILE
        # =================================================

        profile = _get_profile(
            dataset
        )


        # =================================================
        # 3. GENERATE KPI DEFINITIONS
        # =================================================

        kpis = _get_kpis(
            profile
        )


        # =================================================
        # 4. ANALYSIS INPUT
        # =================================================
        #
        # IMPORTANT:
        #
        # Your current AnalysisPlanAgent expects:
        #
        #     generate_plan(prompt_result: Dict)
        #
        # It does NOT accept a raw prompt string.
        #
        # Therefore we create a lightweight prompt result
        # from the user's prompt and dataset profile.
        #
        # If you later create prompt_understanding_agent.py,
        # replace this section with its output.
        #
        # =================================================

        prompt_result = {
            "intent": request.prompt,
            "tasks": []
        }


        # =================================================
        # 5. BASIC PROMPT INTERPRETATION
        # =================================================
        #
        # Until PromptUnderstandingAgent is created,
        # interpret common requests directly.
        #
        # This is intentionally simple and deterministic.
        #
        # =================================================

        prompt_lower = request.prompt.lower()

        numeric_columns = profile.get(
            "numeric_columns",
            []
        )

        categorical_columns = profile.get(
            "categorical_columns",
            []
        )

        date_columns = profile.get(
            "date_columns",
            []
        )


        # -------------------------------------------------
        # Detect Sales / Revenue / Profit metric
        # -------------------------------------------------

        selected_metric = None

        metric_keywords = [
            "sales",
            "revenue",
            "profit",
            "quantity",
            "cost",
            "discount"
        ]

        for keyword in metric_keywords:

            for column in numeric_columns:

                if keyword in column.lower():

                    selected_metric = column

                    break

            if selected_metric:
                break


        # Fallback to first numeric column

        if selected_metric is None:

            if numeric_columns:

                selected_metric = (
                    numeric_columns[0]
                )


        # -------------------------------------------------
        # Detect date column
        # -------------------------------------------------

        selected_date = None

        if date_columns:

            selected_date = (
                date_columns[0]
            )


        # -------------------------------------------------
        # Detect category/dimension
        # -------------------------------------------------

        selected_dimension = None

        dimension_keywords = [
            "region",
            "category",
            "state",
            "city",
            "segment",
            "product",
            "sub_category",
            "payment",
            "status"
        ]

        for keyword in dimension_keywords:

            for column in categorical_columns:

                if keyword in column.lower():

                    selected_dimension = column

                    break

            if selected_dimension:
                break


        # -------------------------------------------------
        # Trend task
        # -------------------------------------------------

        if (
            selected_metric
            and selected_date
            and (
                "trend" in prompt_lower
                or "growth" in prompt_lower
                or "monthly" in prompt_lower
                or "over time" in prompt_lower
            )
        ):

            prompt_result["tasks"].append({

                "metric": selected_metric,

                "operation": "sum",

                "dimension": selected_date,

                "analysis": "trend",

                "time_granularity": "month"

            })


        # -------------------------------------------------
        # Comparison task
        # -------------------------------------------------

        if (
            selected_metric
            and selected_dimension
            and (
                "compare" in prompt_lower
                or "comparison" in prompt_lower
                or "across" in prompt_lower
                or "by" in prompt_lower
            )
        ):

            prompt_result["tasks"].append({

                "metric": selected_metric,

                "operation": "sum",

                "dimension": selected_dimension,

                "analysis": "comparison",

                "time_granularity": None

            })


        # -------------------------------------------------
        # Fallback task
        # -------------------------------------------------

        if not prompt_result["tasks"]:

            if (
                selected_metric
                and selected_date
            ):

                prompt_result["tasks"].append({

                    "metric": selected_metric,

                    "operation": "sum",

                    "dimension": selected_date,

                    "analysis": "trend",

                    "time_granularity": "month"

                })

            elif (
                selected_metric
                and selected_dimension
            ):

                prompt_result["tasks"].append({

                    "metric": selected_metric,

                    "operation": "sum",

                    "dimension": selected_dimension,

                    "analysis": "comparison",

                    "time_granularity": None

                })


        # =================================================
        # 6. GENERATE ANALYSIS PLAN
        # =================================================

        analysis_plan_result = (
            analysis_plan_agent.generate_plan(
                prompt_result
            )
        )

        analysis_plan = (
            _normalize_analysis_plan(
                analysis_plan_result
            )
        )


        # =================================================
        # 7. GENERATE VISUALIZATION RECOMMENDATIONS
        # =================================================

        charts = visualization_agent.generate(
            profile,
            analysis_plan
        )


        # =================================================
        # 8. GENERATE INSIGHTS
        # =================================================
        #
        # IMPORTANT:
        #
        # InsightGenerationAgent.generate()
        # accepts ONLY:
        #
        #     execution_results
        #
        # It does NOT accept profile + analysis_plan.
        #
        # At this stage, if an analysis execution engine
        # already exists, use its results here.
        #
        # Since the current project generation pipeline
        # does not show an execution agent, we create
        # empty execution results.
        #
        # This means the endpoint remains functional.
        #
        # =================================================

        execution_results = []

        execution_results = (
            _normalize_execution_results(
                execution_results
            )
        )

        insights = insight_agent.generate(
            execution_results
        )


        # =================================================
        # 9. GENERATE DASHBOARD PLAN
        # =================================================
        #
        # Your DashboardPlanningAgent requires:
        #
        # generate_plan(
        #     prompt,
        #     kpis,
        #     visualizations,
        #     insights
        # )
        #
        # =================================================

        dashboard_plan = (
            planning_agent.generate_plan(
                request.prompt,
                kpis,
                charts,
                insights
            )
        )


        # =================================================
        # 10. GENERATE DASHBOARD LAYOUT
        # =================================================
        #
        # Your DashboardLayoutAgent requires:
        #
        # generate_layout(
        #     dashboard_plan,
        #     kpis,
        #     charts,
        #     insights
        # )
        #
        # =================================================

        dashboard = (
            layout_agent.generate_layout(
                dashboard_plan,
                kpis,
                charts,
                insights
            )
        )


        # =================================================
        # 11. GENERATE POWER BI PROJECT
        # =================================================

        result = powerbi_agent.generate(
            profile,
            dashboard
        )


        # =================================================
        # 12. BUILD POWER BI PROJECT ON DISK
        # =================================================

        build_result = project_builder.build(
            project_name=result["project_name"],
            files=result["files"]
        )


        # =================================================
        # 13. RETURN RESPONSE
        # =================================================

        return {
            "dataset_id": request.dataset_id,
            "prompt": request.prompt,
            "project_name": result["project_name"],
            "status": build_result["status"],
            "project_type": result["project_type"],
            "project_directory": (
                build_result["project_directory"]
            ),
            "files_created": (
                build_result["files_created"]
            ),
            "created_files": (
                build_result["created_files"]
            ),
            "files": result["files"]
        }


    # =====================================================
    # HTTP EXCEPTION
    # =====================================================

    except HTTPException:

        raise


    # =====================================================
    # GENERAL EXCEPTION
    # =====================================================

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Power BI project generation failed: "
                f"{str(exc)}"
            )
        )