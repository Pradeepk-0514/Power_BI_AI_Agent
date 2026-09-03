from typing import Dict, List


class ChartConfigurationAgent:
    """
    Converts visualization recommendations into
    detailed chart configurations.
    """

    def generate(
        self,
        profile: Dict,
        visualizations: List[Dict]
    ) -> List[Dict]:

        configurations = []

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

        for visualization in visualizations:

            title = visualization.get(
                "title",
                "Untitled Chart"
            )

            chart_type = visualization.get(
                "chart_type"
            )

            x_axis = visualization.get(
                "x_axis"
            )

            y_axis = visualization.get(
                "y_axis"
            )

            aggregation = visualization.get(
                "aggregation"
            )

            time_granularity = visualization.get(
                "time_granularity"
            )

            # -----------------------------------------
            # Determine X-axis data type
            # -----------------------------------------

            x_data_type = "unknown"

            if x_axis in date_columns:
                x_data_type = "date"

            elif x_axis in categorical_columns:
                x_data_type = "categorical"

            elif x_axis in numeric_columns:
                x_data_type = "numeric"

            # -----------------------------------------
            # Determine Y-axis data type
            # -----------------------------------------

            y_data_type = "unknown"

            if y_axis in numeric_columns:
                y_data_type = "numeric"

            elif y_axis in categorical_columns:
                y_data_type = "categorical"

            elif y_axis in date_columns:
                y_data_type = "date"

            # -----------------------------------------
            # X-axis configuration
            # -----------------------------------------

            x_axis_config = {
                "field": x_axis,
                "data_type": x_data_type,
                "aggregation": None,
                "granularity": time_granularity
            }

            # -----------------------------------------
            # Y-axis configuration
            # -----------------------------------------

            y_axis_config = {
                "field": y_axis,
                "data_type": y_data_type,
                "aggregation": aggregation,
                "granularity": None
            }

            # -----------------------------------------
            # Sorting
            # -----------------------------------------

            sorting = {
                "field": x_axis,
                "direction": "ascending"
            }

            # -----------------------------------------
            # Interactions
            # -----------------------------------------

            interactions = {
                "cross_filter": True,
                "tooltip": True
            }

            # -----------------------------------------
            # Description
            # -----------------------------------------

            if chart_type == "line_chart":

                description = (
                    "Line chart showing "
                    f"{y_axis} over "
                    f"{time_granularity or 'time'}."
                )

            elif chart_type == "bar_chart":

                description = (
                    "Bar chart comparing "
                    f"{y_axis} across "
                    f"{x_axis}."
                )

            elif chart_type == "pie_chart":

                description = (
                    "Pie chart showing the "
                    f"distribution of {y_axis} "
                    f"across {x_axis}."
                )

            else:

                description = (
                    f"{chart_type} visual "
                    f"showing {y_axis} by {x_axis}."
                )

            # -----------------------------------------
            # Build configuration
            # -----------------------------------------

            configuration = {
                "title": title,
                "visual_type": chart_type,
                "x_axis": x_axis_config,
                "y_axis": y_axis_config,
                "sorting": sorting,
                "interactions": interactions,
                "description": description
            }

            configurations.append(
                configuration
            )

        return configurations