from typing import Any, Dict, List


class KPIGenerationAgent:
    """
    Generates business KPIs based on the dataset profile
    and the user's analysis prompt.

    Rule-based implementation.
    An LLM layer can be integrated later.
    """

    def __init__(self, profile: Dict[str, Any]):
        self.profile = profile

        self.numeric_columns = profile.get(
            "numeric_columns",
            []
        )

        self.date_columns = profile.get(
            "date_columns",
            []
        )

        self.categorical_columns = profile.get(
            "categorical_columns",
            []
        )

    def generate(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Generate KPI recommendations from the
        dataset profile and user prompt.
        """

        prompt_lower = prompt.lower()

        kpis = []

        # -------------------------------------------------
        # 1. Total Sales
        # -------------------------------------------------

        sales_column = self._find_column(
            [
                "sales",
                "revenue",
                "amount",
                "total_sales"
            ]
        )

        if sales_column:

            kpis.append({
                "name": "Total Sales",
                "metric": sales_column,
                "aggregation": "sum",
                "description": (
                    f"Total value of {sales_column} "
                    "across all records."
                ),
                "business_meaning": (
                    "Measures the overall sales "
                    "performance of the business."
                )
            })

        # -------------------------------------------------
        # 2. Total Profit
        # -------------------------------------------------

        profit_column = self._find_column(
            [
                "profit",
                "net_profit",
                "gross_profit"
            ]
        )

        if profit_column:

            kpis.append({
                "name": "Total Profit",
                "metric": profit_column,
                "aggregation": "sum",
                "description": (
                    f"Total {profit_column} generated "
                    "across all records."
                ),
                "business_meaning": (
                    "Measures the overall profitability "
                    "of the business."
                )
            })

        # -------------------------------------------------
        # 3. Total Quantity
        # -------------------------------------------------

        quantity_column = self._find_column(
            [
                "quantity",
                "units",
                "units_sold"
            ]
        )

        if quantity_column:

            kpis.append({
                "name": "Total Quantity",
                "metric": quantity_column,
                "aggregation": "sum",
                "description": (
                    f"Total number of {quantity_column} "
                    "recorded."
                ),
                "business_meaning": (
                    "Measures the total volume of "
                    "products or units sold."
                )
            })

        # -------------------------------------------------
        # 4. Average Sales
        # -------------------------------------------------

        if sales_column:

            kpis.append({
                "name": "Average Sales",
                "metric": sales_column,
                "aggregation": "average",
                "description": (
                    f"Average value of {sales_column} "
                    "per record."
                ),
                "business_meaning": (
                    "Helps understand the typical "
                    "sales value per transaction."
                )
            })

        # -------------------------------------------------
        # 5. Average Profit
        # -------------------------------------------------

        if profit_column:

            kpis.append({
                "name": "Average Profit",
                "metric": profit_column,
                "aggregation": "average",
                "description": (
                    f"Average {profit_column} "
                    "per record."
                ),
                "business_meaning": (
                    "Shows the typical profit "
                    "generated per transaction."
                )
            })

        # -------------------------------------------------
        # 6. Profit Margin
        # -------------------------------------------------

        if sales_column and profit_column:

            kpis.append({
                "name": "Profit Margin",
                "metric": (
                    f"{profit_column} / "
                    f"{sales_column}"
                ),
                "aggregation": "ratio",
                "description": (
                    "Profit expressed as a percentage "
                    "of sales."
                ),
                "business_meaning": (
                    "Measures how efficiently sales "
                    "are converted into profit."
                )
            })

        # -------------------------------------------------
        # 7. Sales Trend
        # -------------------------------------------------

        if self.date_columns and sales_column:

            trend_keywords = [
                "monthly",
                "month",
                "growth",
                "trend",
                "time",
                "year",
                "quarter"
            ]

            if any(
                keyword in prompt_lower
                for keyword in trend_keywords
            ):

                date_column = self.date_columns[0]

                kpis.append({
                    "name": "Sales Trend",
                    "metric": sales_column,
                    "aggregation": "sum",
                    "description": (
                        f"{sales_column} aggregated "
                        f"over time using "
                        f"{date_column}."
                    ),
                    "business_meaning": (
                        "Helps identify sales growth, "
                        "decline, and seasonal patterns."
                    )
                })

        # -------------------------------------------------
        # 8. Remove duplicates
        # -------------------------------------------------

        unique_kpis = []
        seen = set()

        for kpi in kpis:

            name = kpi["name"]

            if name not in seen:
                seen.add(name)
                unique_kpis.append(kpi)

        return unique_kpis

    # -----------------------------------------------------
    # Helper
    # -----------------------------------------------------

    def _find_column(
        self,
        possible_names: List[str]
    ) -> str | None:

        column_map = {
            str(column).lower(): column
            for column in self.numeric_columns
        }

        for name in possible_names:

            if name.lower() in column_map:
                return column_map[name.lower()]

        return None