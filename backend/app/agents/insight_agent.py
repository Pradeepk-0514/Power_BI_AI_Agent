from typing import Any, Dict, List


class InsightGenerationAgent:
    """
    Processes executed analysis results and generates
    business-oriented insights.
    """

    def generate(
        self,
        execution_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        insights = []

        for result in execution_results:

            analysis_type = result.get(
                "analysis_type"
            )

            metric = result.get(
                "metric"
            )

            rows = result.get(
                "rows",
                []
            )

            if not rows or not metric:
                continue

            # -------------------------------------------------
            # Trend Analysis
            # -------------------------------------------------

            if analysis_type == "trend":

                trend_insights = self._process_trend(
                    metric,
                    rows
                )

                insights.extend(
                    trend_insights
                )

            # -------------------------------------------------
            # Comparison Analysis
            # -------------------------------------------------

            elif analysis_type == "comparison":

                comparison_insights = (
                    self._process_comparison(
                        metric,
                        rows
                    )
                )

                insights.extend(
                    comparison_insights
                )

            # -------------------------------------------------
            # Other Analysis Types
            # -------------------------------------------------

            else:

                generic_insight = (
                    self._process_generic(
                        metric,
                        rows
                    )
                )

                insights.extend(
                    generic_insight
                )

        return insights

    # =================================================
    # Trend Processing
    # =================================================

    def _process_trend(
        self,
        metric: str,
        rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        insights = []

        if not rows:
            return insights

        values = []

        for row in rows:

            value = row.get(metric)

            if isinstance(value, (int, float)):

                values.append({
                    "period": row,
                    "value": float(value)
                })

        if not values:
            return insights

        # Highest
        highest = max(
            values,
            key=lambda item: item["value"]
        )

        # Lowest
        lowest = min(
            values,
            key=lambda item: item["value"]
        )

        # Total
        total = sum(
            item["value"]
            for item in values
        )

        # Average
        average = (
            total / len(values)
        )

        highest_period = (
            self._extract_period(
                highest["period"],
                metric
            )
        )

        lowest_period = (
            self._extract_period(
                lowest["period"],
                metric
            )
        )

        # -------------------------------------------------
        # Total
        # -------------------------------------------------

        insights.append({
            "type": "trend_summary",
            "metric": metric,
            "period": None,
            "value": None,
            "category": None,
            "percentage": None,
            "growth_percentage": None,
            "insight": (
                f"Total {metric} across the "
                f"analyzed period is "
                f"{total:,.2f}."
            )
        })

        # -------------------------------------------------
        # Average
        # -------------------------------------------------

        insights.append({
            "type": "average",
            "metric": metric,
            "period": None,
            "value": None,
            "category": None,
            "percentage": None,
            "growth_percentage": None,
            "insight": (
                f"Average {metric} per period "
                f"is {average:,.2f}."
            )
        })

        # -------------------------------------------------
        # Highest
        # -------------------------------------------------

        insights.append({
            "type": "highest_period",
            "metric": metric,
            "period": highest_period,
            "value": round(
                highest["value"],
                2
            ),
            "category": None,
            "percentage": None,
            "growth_percentage": None,
            "insight": (
                f"The highest {metric} was "
                f"{highest['value']:,.2f} "
                f"in {highest_period}."
            )
        })

        # -------------------------------------------------
        # Lowest
        # -------------------------------------------------

        insights.append({
            "type": "lowest_period",
            "metric": metric,
            "period": lowest_period,
            "value": round(
                lowest["value"],
                2
            ),
            "category": None,
            "percentage": None,
            "growth_percentage": None,
            "insight": (
                f"The lowest {metric} was "
                f"{lowest['value']:,.2f} "
                f"in {lowest_period}."
            )
        })

        # -------------------------------------------------
        # Growth
        # -------------------------------------------------

        if len(values) >= 2:

            first_value = (
                values[0]["value"]
            )

            last_value = (
                values[-1]["value"]
            )

            if first_value != 0:

                growth_percentage = (
                    (
                        last_value -
                        first_value
                    )
                    / first_value
                ) * 100

                direction = (
                    "increased"
                    if growth_percentage >= 0
                    else "decreased"
                )

                insights.append({
                    "type": "growth",
                    "metric": metric,
                    "period": None,
                    "value": None,
                    "category": None,
                    "percentage": None,
                    "growth_percentage": round(
                        growth_percentage,
                        2
                    ),
                    "insight": (
                        f"{metric} {direction} by "
                        f"{abs(growth_percentage):.2f}% "
                        "from the first to the last "
                        "analyzed period."
                    )
                })

        return insights

    # =================================================
    # Comparison Processing
    # =================================================

    def _process_comparison(
        self,
        metric: str,
        rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        insights = []

        if not rows:
            return insights

        values = []

        for row in rows:

            value = row.get(metric)

            if not isinstance(
                value,
                (int, float)
            ):
                continue

            dimension = (
                self._extract_dimension(
                    row,
                    metric
                )
            )

            values.append({
                "dimension": dimension,
                "value": float(value)
            })

        if not values:
            return insights

        highest = max(
            values,
            key=lambda item: item["value"]
        )

        lowest = min(
            values,
            key=lambda item: item["value"]
        )

        total = sum(
            item["value"]
            for item in values
        )

        # -------------------------------------------------
        # Top Category
        # -------------------------------------------------

        insights.append({
            "type": "top_category",
            "metric": metric,
            "period": None,
            "value": round(
                highest["value"],
                2
            ),
            "category": highest["dimension"],
            "percentage": None,
            "growth_percentage": None,
            "insight": (
                f"{highest['dimension']} has the "
                f"highest {metric} with "
                f"{highest['value']:,.2f}."
            )
        })

        # -------------------------------------------------
        # Bottom Category
        # -------------------------------------------------

        insights.append({
            "type": "bottom_category",
            "metric": metric,
            "period": None,
            "value": round(
                lowest["value"],
                2
            ),
            "category": lowest["dimension"],
            "percentage": None,
            "growth_percentage": None,
            "insight": (
                f"{lowest['dimension']} has the "
                f"lowest {metric} with "
                f"{lowest['value']:,.2f}."
            )
        })

        # -------------------------------------------------
        # Category Contribution
        # -------------------------------------------------

        if total != 0:

            contribution = (
                highest["value"]
                / total
            ) * 100

            insights.append({
                "type": "category_contribution",
                "metric": metric,
                "period": None,
                "value": None,
                "category": highest["dimension"],
                "percentage": round(
                    contribution,
                    2
                ),
                "growth_percentage": None,
                "insight": (
                    f"{highest['dimension']} contributes "
                    f"{contribution:.2f}% of the total "
                    f"{metric} among the analyzed "
                    "categories."
                )
            })

        return insights

    # =================================================
    # Generic Processing
    # =================================================

    def _process_generic(
        self,
        metric: str,
        rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        if not rows:
            return []

        numeric_values = []

        for row in rows:

            value = row.get(metric)

            if isinstance(
                value,
                (int, float)
            ):

                numeric_values.append(
                    float(value)
                )

        if not numeric_values:
            return []

        total = sum(
            numeric_values
        )

        average = (
            total /
            len(numeric_values)
        )

        return [{
            "type": "summary",
            "metric": metric,
            "period": None,
            "value": None,
            "category": None,
            "percentage": None,
            "growth_percentage": None,
            "insight": (
                f"Total {metric} is "
                f"{total:,.2f}, with an "
                f"average value of "
                f"{average:,.2f}."
            )
        }]

    # =================================================
    # Helper Functions
    # =================================================

    def _extract_period(
        self,
        row: Dict[str, Any],
        metric: str
    ) -> Any:

        for key, value in row.items():

            if key != metric:
                return value

        return "Unknown"

    def _extract_dimension(
        self,
        row: Dict[str, Any],
        metric: str
    ) -> Any:

        for key, value in row.items():

            if key != metric:
                return value

        return "Unknown"