from typing import Any, Dict


class DashboardGenerationAgent:
    """
    Generates a dashboard definition from the
    dataset profile and user prompt.

    Module 5.3 / 5.4 integration layer.
    """

    def generate(
        self,
        profile: Dict[str, Any],
        prompt: str
    ) -> Dict[str, Any]:

        # ---------------------------------------------
        # Find useful columns
        # ---------------------------------------------

        numeric_columns = profile.get(
            "numeric_columns",
            []
        )

        date_columns = profile.get(
            "date_columns",
            []
        )

        categorical_columns = profile.get(
            "categorical_columns",
            []
        )

        # ---------------------------------------------
        # Detect common business columns
        # ---------------------------------------------

        sales_column = self._find_column(
            numeric_columns,
            [
                "sales",
                "revenue",
                "amount",
                "total_sales"
            ]
        )

        date_column = (
            date_columns[0]
            if date_columns
            else None
        )

        region_column = self._find_column(
            categorical_columns,
            [
                "region",
                "territory",
                "state",
                "city"
            ]
        )

        # ---------------------------------------------
        # Dashboard title
        # ---------------------------------------------

        if sales_column:
            dashboard_title = (
                f"{sales_column} Performance Dashboard"
            )
        else:
            dashboard_title = "Business Performance Dashboard"

        # ---------------------------------------------
        # Visuals
        # ---------------------------------------------

        visuals = []

        # Monthly sales trend
        if sales_column and date_column:

            visuals.append({
                "title": (
                    f"Monthly {sales_column} Trend"
                ),
                "visual_type": "line_chart",
                "x_axis": {
                    "field": date_column,
                    "data_type": "date",
                    "aggregation": None,
                    "granularity": "month"
                },
                "y_axis": {
                    "field": sales_column,
                    "data_type": "numeric",
                    "aggregation": "sum",
                    "granularity": None
                },
                "position": {
                    "x": 0,
                    "y": 0
                },
                "width": 600,
                "height": 350
            })

        # Sales by region
        if sales_column and region_column:

            visuals.append({
                "title": (
                    f"{sales_column} by "
                    f"{region_column}"
                ),
                "visual_type": "bar_chart",
                "x_axis": {
                    "field": region_column,
                    "data_type": "categorical",
                    "aggregation": None,
                    "granularity": None
                },
                "y_axis": {
                    "field": sales_column,
                    "data_type": "numeric",
                    "aggregation": "sum",
                    "granularity": None
                },
                "position": {
                    "x": 620,
                    "y": 0
                },
                "width": 500,
                "height": 350
            })

        # ---------------------------------------------
        # Dashboard result
        # ---------------------------------------------

        return {
            "dashboard_title": dashboard_title,
            "status": "generated",
            "pages": [
                {
                    "page_number": 1,
                    "page_name": "Overview",
                    "layout_type": "standard",
                    "visuals": visuals
                }
            ]
        }

    # ---------------------------------------------
    # Helper
    # ---------------------------------------------

    def _find_column(
        self,
        columns: list,
        possible_names: list
    ) -> str | None:

        column_map = {
            str(column).lower(): column
            for column in columns
        }

        for name in possible_names:

            if name.lower() in column_map:
                return column_map[name.lower()]

        return None