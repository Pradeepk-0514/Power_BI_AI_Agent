from typing import Any, Dict, List


class PromptUnderstandingAgent:
    """
    Converts a user's natural-language prompt into a
    structured analytical intent and list of tasks.

    Rule-based implementation.
    LLM integration can be added later.
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

    # =====================================================
    # MAIN FUNCTION
    # =====================================================

    def generate(
        self,
        prompt: str
    ) -> Dict[str, Any]:

        prompt_lower = prompt.lower()

        tasks: List[Dict[str, Any]] = []

        # -------------------------------------------------
        # Find important columns
        # -------------------------------------------------

        metric = self._find_metric(prompt_lower)

        date_column = (
            self.date_columns[0]
            if self.date_columns
            else None
        )

        category_column = self._find_category(
            prompt_lower
        )

        # =================================================
        # 1. Trend / Monthly / Growth analysis
        # =================================================

        trend_keywords = [
            "monthly",
            "month",
            "trend",
            "growth",
            "over time",
            "yearly",
            "year",
            "quarter",
            "quarterly"
        ]

        if (
            metric
            and date_column
            and any(
                keyword in prompt_lower
                for keyword in trend_keywords
            )
        ):

            time_granularity = self._detect_time_granularity(
                prompt_lower
            )

            tasks.append({
                "metric": metric,
                "operation": "sum",
                "dimension": date_column,
                "analysis": "trend",
                "time_granularity": time_granularity
            })

        # =================================================
        # 2. Category comparison
        # =================================================

        comparison_keywords = [
            "compare",
            "comparison",
            "across",
            "by region",
            "by category",
            "by segment"
        ]

        if (
            metric
            and category_column
            and any(
                keyword in prompt_lower
                for keyword in comparison_keywords
            )
        ):

            tasks.append({
                "metric": metric,
                "operation": "sum",
                "dimension": category_column,
                "analysis": "comparison",
                "time_granularity": None
            })

        # =================================================
        # 3. Generic category analysis
        # =================================================

        if (
            metric
            and category_column
            and not tasks
        ):

            tasks.append({
                "metric": metric,
                "operation": "sum",
                "dimension": category_column,
                "analysis": "comparison",
                "time_granularity": None
            })

        # =================================================
        # 4. Generic metric aggregation
        # =================================================

        if metric and not tasks:

            tasks.append({
                "metric": metric,
                "operation": "sum",
                "dimension": None,
                "analysis": "aggregation",
                "time_granularity": None
            })

        # =================================================
        # Intent
        # =================================================

        if tasks:
            intent = "business_analysis"
        else:
            intent = "general_query"

        return {
            "intent": intent,
            "tasks": tasks
        }

    # =====================================================
    # FIND METRIC
    # =====================================================

    def _find_metric(
        self,
        prompt_lower: str
    ) -> str | None:

        priority_names = [
            "sales",
            "revenue",
            "profit",
            "amount",
            "quantity",
            "cost",
            "discount"
        ]

        # First check prompt-mentioned metrics
        for name in priority_names:

            for column in self.numeric_columns:

                if column.lower() == name:

                    if name in prompt_lower:

                        return column

        # Then use any matching numeric column
        for column in self.numeric_columns:

            column_lower = column.lower()

            if column_lower in prompt_lower:

                return column

        # Fallback
        if self.numeric_columns:

            return self.numeric_columns[0]

        return None

    # =====================================================
    # FIND CATEGORY
    # =====================================================

    def _find_category(
        self,
        prompt_lower: str
    ) -> str | None:

        # Common business dimensions
        preferred_categories = [
            "region",
            "category",
            "sub_category",
            "customer_segment",
            "segment",
            "state",
            "city",
            "product_name",
            "payment_mode",
            "order_status"
        ]

        for preferred in preferred_categories:

            for column in self.categorical_columns:

                if column.lower() == preferred:

                    # Handle phrases such as:
                    # "across regions"
                    # "by category"
                    # "compare regions"

                    if (
                        preferred.replace(
                            "_",
                            " "
                        ) in prompt_lower
                        or preferred in prompt_lower
                    ):

                        return column

        # Check any categorical column explicitly
        for column in self.categorical_columns:

            column_text = column.lower().replace(
                "_",
                " "
            )

            if column_text in prompt_lower:

                return column

        return None

    # =====================================================
    # TIME GRANULARITY
    # =====================================================

    def _detect_time_granularity(
        self,
        prompt_lower: str
    ) -> str:

        if (
            "monthly" in prompt_lower
            or "month" in prompt_lower
        ):
            return "month"

        if (
            "quarterly" in prompt_lower
            or "quarter" in prompt_lower
        ):
            return "quarter"

        if (
            "yearly" in prompt_lower
            or "annual" in prompt_lower
            or "year" in prompt_lower
        ):
            return "year"

        return "month"