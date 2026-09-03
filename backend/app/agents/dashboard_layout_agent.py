from typing import Any, Dict, List


class DashboardLayoutAgent:
    """
    Creates the physical layout of dashboard elements.

    Module 5.2 takes generated KPIs, chart configurations,
    and insights and assigns them to dashboard positions.
    """

    def generate_layout(
        self,
        dashboard_plan: Dict[str, Any],
        kpis: List[Dict[str, Any]],
        charts: List[Dict[str, Any]],
        insights: List[Dict[str, Any]]
    ) -> Dict[str, Any]:

        pages = dashboard_plan.get("pages", [])

        if not pages:
            pages = [
                {
                    "page_number": 1,
                    "page_name": "Overview",
                    "purpose": (
                        "Provides an overview of the main "
                        "business metrics, trends, comparisons "
                        "and generated insights."
                    )
                }
            ]

        visuals = []

        # -------------------------------------------------
        # 1. KPI CARDS
        # -------------------------------------------------

        kpi_positions = [
            {
                "x": 0,
                "y": 0,
                "width": 3,
                "height": 2
            },
            {
                "x": 3,
                "y": 0,
                "width": 3,
                "height": 2
            },
            {
                "x": 6,
                "y": 0,
                "width": 3,
                "height": 2
            },
            {
                "x": 9,
                "y": 0,
                "width": 3,
                "height": 2
            }
        ]

        for index, kpi in enumerate(kpis):

            if index >= len(kpi_positions):
                break

            visuals.append({
                "visual_id": f"kpi_{index + 1}",
                "visual_type": "kpi_card",
                "title": kpi.get(
                    "name",
                    "KPI"
                ),
                "position": kpi_positions[index],
                "configuration": kpi
            })

        # -------------------------------------------------
        # 2. CHARTS
        # -------------------------------------------------

        chart_start_y = 3

        for index, chart in enumerate(charts):

            row = index // 2
            column = index % 2

            position = {
                "x": column * 6,
                "y": chart_start_y + row * 5,
                "width": 6,
                "height": 5
            }

            visuals.append({
                "visual_id": f"chart_{index + 1}",
                "visual_type": chart.get(
                    "visual_type",
                    chart.get(
                    "chart_type",
                    "chart"
                )
            ),
                "title": chart.get(
                    "title",
                    "Chart"
                ),
                "position": position,
                "configuration": chart
            })

        # -------------------------------------------------
        # 3. INSIGHTS
        # -------------------------------------------------

        insight_y = chart_start_y + (
            ((len(charts) + 1) // 2) * 5
        )

        for index, insight in enumerate(insights):

            visuals.append({
                "visual_id": f"insight_{index + 1}",
                "visual_type": "insight_card",
                "title": (
                    f"Insight {index + 1}"
                ),
                "position": {
                    "x": 0,
                    "y": insight_y + index * 2,
                    "width": 12,
                    "height": 2
                },
                "configuration": insight
            })

        # -------------------------------------------------
        # 4. ADD VISUALS TO FIRST PAGE
        # -------------------------------------------------

        pages[0]["visuals"] = visuals

        return {
            "dashboard_title": dashboard_plan.get(
                "dashboard_title",
                "Business Analytics Dashboard"
            ),
            "pages": pages
        }