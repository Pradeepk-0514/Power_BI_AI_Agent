from typing import Dict, List


class VisualizationRecommendationAgent:
    """
    Recommends suitable visualizations based on
    the dataset profile and generated analysis plan.
    """

    def generate(
        self,
        profile: Dict,
        analysis_plan: List[Dict]
    ) -> List[Dict]:

        recommendations = []

        date_columns = profile.get(
            "date_columns",
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

        # Convert to sets for safer/faster lookup
        date_columns_set = set(date_columns)
        numeric_columns_set = set(numeric_columns)
        categorical_columns_set = set(categorical_columns)

        for step in analysis_plan:

            metric = step.get("metric")
            aggregation = step.get("aggregation")
            group_by = step.get("group_by")

            time_granularity = step.get(
                "time_granularity"
            )

            analysis_type = step.get(
                "analysis_type"
            )

            # Ignore incomplete steps
            if not metric or not group_by:
                continue

            # -------------------------------------------------
            # Trend analysis
            # -------------------------------------------------

            if analysis_type == "trend":

                if (
                    group_by in date_columns_set
                    and metric in numeric_columns_set
                ):

                    recommendations.append({
                        "title": (
                            f"{(time_granularity or 'Time').title()} "
                            f"{metric} Trend"
                        ),
                        "chart_type": "line_chart",
                        "x_axis": group_by,
                        "y_axis": metric,
                        "aggregation": aggregation,
                        "time_granularity": (
                            time_granularity
                        ),
                        "reason": (
                            "A line chart is suitable "
                            "for showing changes and "
                            "growth over time."
                        )
                    })

                continue

            # -------------------------------------------------
            # Comparison analysis
            # -------------------------------------------------

            if analysis_type == "comparison":

                if (
                    group_by in categorical_columns_set
                    and metric in numeric_columns_set
                ):

                    recommendations.append({
                        "title": (
                            f"{metric} by {group_by}"
                        ),
                        "chart_type": "bar_chart",
                        "x_axis": group_by,
                        "y_axis": metric,
                        "aggregation": aggregation,
                        "time_granularity": None,
                        "reason": (
                            "A bar chart is suitable "
                            "for comparing values "
                            "across categories."
                        )
                    })

                continue

            # -------------------------------------------------
            # Generic aggregation
            # -------------------------------------------------

            if group_by in date_columns_set:

                recommendations.append({
                    "title": (
                        f"{metric} over time"
                    ),
                    "chart_type": "line_chart",
                    "x_axis": group_by,
                    "y_axis": metric,
                    "aggregation": aggregation,
                    "time_granularity": (
                        time_granularity
                    ),
                    "reason": (
                        "A line chart provides "
                        "a clear view of trends "
                        "over time."
                    )
                })

            elif group_by in categorical_columns_set:

                recommendations.append({
                    "title": (
                        f"{metric} by {group_by}"
                    ),
                    "chart_type": "bar_chart",
                    "x_axis": group_by,
                    "y_axis": metric,
                    "aggregation": aggregation,
                    "time_granularity": None,
                    "reason": (
                        "A bar chart clearly "
                        "compares values across "
                        "categories."
                    )
                })

        # -------------------------------------------------
        # Remove duplicates
        # -------------------------------------------------

        unique_recommendations = []
        seen = set()

        for recommendation in recommendations:

            key = (
                recommendation.get("title"),
                recommendation.get("chart_type"),
                recommendation.get("x_axis"),
                recommendation.get("y_axis")
            )

            if key not in seen:

                seen.add(key)

                unique_recommendations.append(
                    recommendation
                )

        return unique_recommendations