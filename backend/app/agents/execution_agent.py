from pathlib import Path
from typing import Any

import pandas as pd


class DataExecutionAgent:
    """
    Executes analysis plans and chart configurations
    against the uploaded dataset.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Main execution method
    # ---------------------------------------------------------

    def execute(
        self,
        file_path: str,
        analysis_plan: list[dict]
    ) -> list[dict]:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {file_path}"
            )

        if path.suffix.lower() != ".csv":
            raise ValueError(
                "Currently only CSV execution is supported."
            )

        df = pd.read_csv(path)

        if df.empty:
            raise ValueError(
                "Dataset is empty."
            )

        results = []

        for step in analysis_plan:

            result = self._execute_step(
                df,
                step
            )

            results.append(result)

        return results

    # ---------------------------------------------------------
    # Execute individual analysis step
    # ---------------------------------------------------------

    def _execute_step(
        self,
        df: pd.DataFrame,
        step: dict
    ) -> dict:

        metric = step.get("metric")
        aggregation = step.get("aggregation")
        group_by = step.get("group_by")
        time_granularity = step.get(
            "time_granularity"
        )
        analysis_type = step.get(
            "analysis_type",
            "general"
        )

        if not metric:
            raise ValueError(
                "Metric is required."
            )

        if metric not in df.columns:
            raise ValueError(
                f"Metric '{metric}' not found "
                "in dataset."
            )

        # -----------------------------------------------------
        # Date-based analysis
        # -----------------------------------------------------

        if time_granularity:

            if not group_by:
                raise ValueError(
                    "Date grouping requires "
                    "a group_by column."
                )

            if group_by not in df.columns:
                raise ValueError(
                    f"Column '{group_by}' not found "
                    "in dataset."
                )

            working_df = df.copy()

            working_df[group_by] = pd.to_datetime(
                working_df[group_by],
                errors="coerce"
            )

            working_df = working_df.dropna(
                subset=[group_by]
            )

            working_df["_time_group"] = (
                self._create_time_group(
                    working_df[group_by],
                    time_granularity
                )
            )

            grouped = (
                working_df
                .groupby("_time_group")[metric]
                .agg(self._get_aggregation(aggregation))
                .reset_index()
            )

            grouped.columns = [
                group_by,
                metric
            ]

            grouped = grouped.sort_values(
                by=group_by
            )

            return {
                "step": step.get("step"),
                "analysis_type": analysis_type,
                "metric": metric,
                "aggregation": aggregation,
                "group_by": group_by,
                "time_granularity": time_granularity,
                "rows": self._records(
                    grouped
                )
            }

        # -----------------------------------------------------
        # Categorical analysis
        # -----------------------------------------------------

        if group_by:

            if group_by not in df.columns:
                raise ValueError(
                    f"Column '{group_by}' not found "
                    "in dataset."
                )

            grouped = (
                df
                .groupby(group_by)[metric]
                .agg(self._get_aggregation(aggregation))
                .reset_index()
            )

            grouped = grouped.sort_values(
                by=metric,
                ascending=False
            )

            return {
                "step": step.get("step"),
                "analysis_type": analysis_type,
                "metric": metric,
                "aggregation": aggregation,
                "group_by": group_by,
                "time_granularity": None,
                "rows": self._records(
                    grouped
                )
            }

        # -----------------------------------------------------
        # Overall metric
        # -----------------------------------------------------

        value = self._aggregate_series(
            df[metric],
            aggregation
        )

        return {
            "step": step.get("step"),
            "analysis_type": analysis_type,
            "metric": metric,
            "aggregation": aggregation,
            "group_by": None,
            "time_granularity": None,
            "value": value
        }

    # ---------------------------------------------------------
    # Time grouping
    # ---------------------------------------------------------

    def _create_time_group(
        self,
        series: pd.Series,
        granularity: str
    ):

        granularity = granularity.lower()

        if granularity == "day":
            return series.dt.to_period(
                "D"
            ).astype(str)

        if granularity == "week":
            return series.dt.to_period(
                "W"
            ).astype(str)

        if granularity == "month":
            return series.dt.to_period(
                "M"
            ).astype(str)

        if granularity == "quarter":
            return series.dt.to_period(
                "Q"
            ).astype(str)

        if granularity == "year":
            return series.dt.to_period(
                "Y"
            ).astype(str)

        raise ValueError(
            f"Unsupported time granularity: "
            f"{granularity}"
        )

    # ---------------------------------------------------------
    # Aggregation mapping
    # ---------------------------------------------------------

    def _get_aggregation(
        self,
        aggregation: str
    ):

        aggregation = str(
            aggregation
        ).lower()

        mapping = {
            "sum": "sum",
            "average": "mean",
            "mean": "mean",
            "min": "min",
            "max": "max",
            "count": "count"
        }

        if aggregation not in mapping:
            raise ValueError(
                f"Unsupported aggregation: "
                f"{aggregation}"
            )

        return mapping[aggregation]

    # ---------------------------------------------------------
    # Aggregate single series
    # ---------------------------------------------------------

    def _aggregate_series(
        self,
        series: pd.Series,
        aggregation: str
    ):

        aggregation = str(
            aggregation
        ).lower()

        if aggregation == "sum":
            return float(series.sum())

        if aggregation in {
            "average",
            "mean"
        }:
            return float(series.mean())

        if aggregation == "min":
            return float(series.min())

        if aggregation == "max":
            return float(series.max())

        if aggregation == "count":
            return int(series.count())

        raise ValueError(
            f"Unsupported aggregation: "
            f"{aggregation}"
        )

    # ---------------------------------------------------------
    # Convert DataFrame to JSON-safe records
    # ---------------------------------------------------------

    def _records(
        self,
        df: pd.DataFrame
    ) -> list[dict[str, Any]]:

        records = df.to_dict(
            orient="records"
        )

        cleaned = []

        for record in records:

            clean_record = {}

            for key, value in record.items():

                if hasattr(value, "item"):
                    value = value.item()

                clean_record[str(key)] = value

            cleaned.append(clean_record)

        return cleaned