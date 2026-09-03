from typing import Any, Dict, List


class DashboardPlanningAgent:
    """
    Module 5.2 — Dashboard Planning Agent

    Converts KPI, visualization, and insight information
    into a structured Power BI dashboard layout.
    """

    def __init__(self):
        pass

    def generate_plan(
        self,
        prompt: str,
        kpis: List[Dict[str, Any]],
        visualizations: List[Dict[str, Any]],
        insights: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        dashboard_title = self._generate_title(prompt)

        visuals = []

        # -----------------------------------------
        # KPI Cards
        # -----------------------------------------

        for kpi in kpis[:4]:

            visuals.append({
                "type": "kpi_card",
                "title": kpi.get("name"),
                "metric": kpi.get("metric"),
                "aggregation": kpi.get("aggregation"),
                "description": kpi.get("business_meaning")
            })

        # -----------------------------------------
        # Charts
        # -----------------------------------------

        for visualization in visualizations:

            visuals.append({
                "type": "chart",
                "title": visualization.get("title"),
                "chart_type": visualization.get("chart_type"),
                "x_axis": visualization.get("x_axis"),
                "y_axis": visualization.get("y_axis"),
                "aggregation": visualization.get(
                    "aggregation"
                ),
                "time_granularity": visualization.get(
                    "time_granularity"
                )
            })

        # -----------------------------------------
        # Insight section
        # -----------------------------------------

        insight_items = []

        for insight in insights[:5]:

            insight_items.append({
                "type": insight.get("type"),
                "text": insight.get("insight")
            })

        return {
            "dashboard_title": dashboard_title,
            "description": (
                "Interactive Power BI dashboard generated "
                "from the user's analytical request."
            ),
            "pages": [
                {
                    "page_number": 1,
                    "page_name": "Overview",
                    "purpose": (
                        "Provides an overview of key KPIs, "
                        "business trends, comparisons, "
                        "and generated insights."
                    ),
                    "visuals": visuals,
                    "insights": insight_items
                }
            ]
        }

    # -----------------------------------------
    # Dashboard title generation
    # -----------------------------------------

    def _generate_title(self, prompt: str) -> str:

        prompt_lower = prompt.lower()

        if "sales" in prompt_lower:
            return "Sales Performance Dashboard"

        if "revenue" in prompt_lower:
            return "Revenue Performance Dashboard"

        if "profit" in prompt_lower:
            return "Profitability Dashboard"

        return "Business Analytics Dashboard"