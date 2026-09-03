from typing import Dict, List
import re


class PromptValidationAgent:
    """
    Validates an analysis plan against the uploaded dataset profile.

    It checks:
    1. Metrics
    2. Dimensions
    3. Aggregations
    4. Time granularity
    5. Business terms mentioned directly in the user prompt
    """

    def validate(
        self,
        profile: Dict,
        analysis_plan: List[Dict],
        prompt: str = ""
    ) -> Dict:

        issues = []

        # -------------------------------------------------
        # Dataset profile
        # -------------------------------------------------

        available_columns = profile.get(
            "column_names",
            []
        )

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

        # Convert everything to lowercase for
        # case-insensitive comparison.
        available_lower = {
            str(column).lower(): column
            for column in available_columns
        }

        numeric_lower = {
            str(column).lower()
            for column in numeric_columns
        }

        categorical_lower = {
            str(column).lower()
            for column in categorical_columns
        }

        date_lower = {
            str(column).lower()
            for column in date_columns
        }

        # -------------------------------------------------
        # Helper function
        # -------------------------------------------------

        def add_issue(
            step: int,
            field: str,
            value: str,
            message: str
        ) -> None:

            issues.append({
                "step": step,
                "field": field,
                "value": value,
                "message": message
            })

        # -------------------------------------------------
        # 1. Validate analysis plan
        # -------------------------------------------------

        for step in analysis_plan:

            step_number = step.get("step", 0)

            metric = step.get("metric")
            group_by = step.get("group_by")
            aggregation = step.get("aggregation")
            time_granularity = step.get(
                "time_granularity"
            )

            # ---------------------------------------------
            # Validate metric
            # ---------------------------------------------

            if metric:

                metric_key = str(metric).strip().lower()

                if metric_key not in available_lower:

                    add_issue(
                        step_number,
                        "metric",
                        str(metric),
                        (
                            f"Metric '{metric}' does not "
                            "exist in the dataset."
                        )
                    )

                elif metric_key not in numeric_lower:

                    add_issue(
                        step_number,
                        "metric",
                        str(metric),
                        (
                            f"Metric '{metric}' is not "
                            "a numeric column."
                        )
                    )

            # ---------------------------------------------
            # Validate dimension
            # ---------------------------------------------

            if group_by:

                group_key = str(group_by).strip().lower()

                if group_key not in available_lower:

                    add_issue(
                        step_number,
                        "dimension",
                        str(group_by),
                        (
                            f"Dimension '{group_by}' does "
                            "not exist in the dataset."
                        )
                    )

                elif (
                    group_key not in categorical_lower
                    and group_key not in date_lower
                    and group_key not in numeric_lower
                ):

                    add_issue(
                        step_number,
                        "dimension",
                        str(group_by),
                        (
                            f"Column '{group_by}' cannot "
                            "be used as a supported "
                            "analysis dimension."
                        )
                    )

            # ---------------------------------------------
            # Validate aggregation
            # ---------------------------------------------

            if aggregation:

                aggregation_key = (
                    str(aggregation).strip().lower()
                )

                allowed_operations = {
                    "sum",
                    "average",
                    "mean",
                    "count",
                    "min",
                    "max"
                }

                if aggregation_key not in allowed_operations:

                    add_issue(
                        step_number,
                        "aggregation",
                        str(aggregation),
                        (
                            f"Aggregation '{aggregation}' "
                            "is not supported."
                        )
                    )

            # ---------------------------------------------
            # Validate time granularity
            # ---------------------------------------------

            if time_granularity:

                granularity_key = (
                    str(time_granularity)
                    .strip()
                    .lower()
                )

                allowed_granularities = {
                    "day",
                    "week",
                    "month",
                    "quarter",
                    "year"
                }

                if granularity_key not in allowed_granularities:

                    add_issue(
                        step_number,
                        "time_granularity",
                        str(time_granularity),
                        (
                            f"Time granularity "
                            f"'{time_granularity}' "
                            "is not supported."
                        )
                    )

                if not group_by:

                    add_issue(
                        step_number,
                        "time_granularity",
                        str(time_granularity),
                        (
                            "Time granularity requires "
                            "a date column."
                        )
                    )

                else:

                    group_key = (
                        str(group_by)
                        .strip()
                        .lower()
                    )

                    if group_key not in date_lower:

                        add_issue(
                            step_number,
                            "time_granularity",
                            str(time_granularity),
                            (
                                f"'{group_by}' is not "
                                "a date column, so "
                                f"'{time_granularity}' "
                                "cannot be applied."
                            )
                        )

        # -------------------------------------------------
        # 2. Validate business terms from user prompt
        # -------------------------------------------------

        prompt_lower = str(prompt).lower()

        business_terms = {

            "revenue": {
                "type": "metric",
                "suggestions": [
                    "Sales"
                ]
            },

            "turnover": {
                "type": "metric",
                "suggestions": [
                    "Sales"
                ]
            },

            "income": {
                "type": "metric",
                "suggestions": [
                    "Sales",
                    "Profit"
                ]
            },

            "department": {
                "type": "dimension",
                "suggestions": [
                    "Category",
                    "Sub_Category"
                ]
            },

            "territory": {
                "type": "dimension",
                "suggestions": [
                    "Region",
                    "State",
                    "City"
                ]
            }
        }

        for term, info in business_terms.items():

            pattern = rf"\b{re.escape(term)}\b"

            if not re.search(
                pattern,
                prompt_lower
            ):
                continue

            term_type = info["type"]

            # ---------------------------------------------
            # Metric business term
            # ---------------------------------------------

            if term_type == "metric":

                if term not in available_lower:

                    suggestions = [
                        column
                        for column in info["suggestions"]
                        if column.lower()
                        in available_lower
                    ]

                    if suggestions:

                        message = (
                            f"Requested metric '{term}' "
                            "is not directly available "
                            "in the dataset. Possible "
                            "matching dataset column(s): "
                            f"{', '.join(suggestions)}."
                        )

                    else:

                        message = (
                            f"Requested metric '{term}' "
                            "is not available in the "
                            "dataset."
                        )

                    add_issue(
                        0,
                        "metric",
                        term,
                        message
                    )

            # ---------------------------------------------
            # Dimension business term
            # ---------------------------------------------

            elif term_type == "dimension":

                if term not in available_lower:

                    suggestions = [
                        column
                        for column in info["suggestions"]
                        if column.lower()
                        in available_lower
                    ]

                    if suggestions:

                        message = (
                            f"Requested dimension "
                            f"'{term}' is not directly "
                            "available in the dataset. "
                            "Possible matching dataset "
                            "column(s): "
                            f"{', '.join(suggestions)}."
                        )

                    else:

                        message = (
                            f"Requested dimension "
                            f"'{term}' is not available "
                            "in the dataset."
                        )

                    add_issue(
                        0,
                        "dimension",
                        term,
                        message
                    )

        # -------------------------------------------------
        # 3. Remove duplicate issues
        # -------------------------------------------------

        unique_issues = []
        seen = set()

        for issue in issues:

            key = (
                issue["step"],
                issue["field"],
                issue["value"],
                issue["message"]
            )

            if key not in seen:

                seen.add(key)
                unique_issues.append(issue)

        # -------------------------------------------------
        # 4. Final validation result
        # -------------------------------------------------

        return {
            "valid": len(unique_issues) == 0,
            "issues": unique_issues
        }