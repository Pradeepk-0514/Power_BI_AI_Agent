from typing import Dict, List


class DashboardPlanningAgent:
    """
    Generates a structured dashboard plan from
    KPIs, visualization configurations and insights.
    """

    def generate_plan(
        self,
        profile: Dict,
        kpis: List[Dict],
        visualizations: List[Dict],
        insights: List[Dict],
        prompt: str
    ) -> Dict:

        dashboard_title = self._generate_title(
            prompt
        )

        dashboard_description = (
            "Interactive dashboard generated from "
            "the user's analytical request."
        )

        visuals = []

        # -------------------------------------------------
        # 1. KPI cards
        # -------------------------------------------------

        for index, kpi in enumerate(kpis[:4], start=1):

            visuals.append(
                {
                    "visual_id": f"kpi_{index}",
                    "title": kpi.get(
                        "name",
                        f"KPI {index}"
                    ),
                    "visual_type": "kpi_card",
                    "section": "kpi_section",
                    "priority": index
                }
            )

        # -------------------------------------------------
        # 2. Recommended charts
        # -------------------------------------------------

        for index, visualization in enumerate(
            visualizations,
            start=1
        ):

            chart_type = visualization.get(
                "chart_type",
                "bar_chart"
            )

            title = visualization.get(
                "title",
                f"Chart {index}"
            )

            visuals.append(
                {
                    "visual_id": f"chart_{index}",
                    "title": title,
                    "visual_type": chart_type,
                    "section": "analysis_section",
                    "priority": index
                }
            )

        # -------------------------------------------------
        # 3. Insights
        # -------------------------------------------------

        if insights:

            visuals.append(
                {
                    "visual_id": "insights_1",
                    "title": "Key Business Insights",
                    "visual_type": "insight_panel",
                    "section": "insights_section",
                    "priority": 1
                }
            )

        # -------------------------------------------------
        # 4. Dashboard page
        # -------------------------------------------------

        page = {
            "page_number": 1,
            "page_name": "Overview",
            "purpose": (
                "Provides an overview of the main "
                "business metrics, trends, comparisons "
                "and generated insights."
            ),
            "visuals": visuals
        }

        return {
            "dashboard_title": dashboard_title,
            "description": dashboard_description,
            "pages": [page]
        }

    def _generate_title(
        self,
        prompt: str
    ) -> str:

        prompt_lower = prompt.lower()

        if "sales" in prompt_lower:
            return "Sales Performance Dashboard"

        if "profit" in prompt_lower:
            return "Profit Performance Dashboard"

        if "revenue" in prompt_lower:
            return "Revenue Performance Dashboard"

        return "Business Analytics Dashboard"