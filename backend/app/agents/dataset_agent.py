from pathlib import Path
from typing import Any

import pandas as pd


class DatasetUnderstandingAgent:
    """
    Analyzes uploaded CSV datasets and generates
    a structured dataset profile.

    Large CSV files are processed in chunks to
    avoid loading the complete dataset into memory.
    """

    def __init__(self, chunk_size: int = 10_000):
        self.chunk_size = chunk_size

    def analyze(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {file_path}")

        if path.suffix.lower() != ".csv":
            raise ValueError("Currently only CSV analysis is supported.")

        return self._analyze_csv(path)

    def _analyze_csv(self, path: Path) -> dict[str, Any]:

        total_rows = 0
        total_missing = {}
        numeric_columns = set()
        categorical_columns = set()
        date_columns = set()
        text_columns = set()

        column_names = None
        sample_df = None

        for chunk in pd.read_csv(
            path,
            chunksize=self.chunk_size,
            low_memory=False
        ):

            if column_names is None:
                column_names = list(chunk.columns)
                sample_df = chunk.head(1000).copy()

                for column in column_names:
                    total_missing[column] = 0

            total_rows += len(chunk)

            # Missing values
            missing_counts = chunk.isna().sum()

            for column, count in missing_counts.items():
                total_missing[column] += int(count)

        # Analyze column types using a sample
        if sample_df is not None:

            for column in sample_df.columns:

                series = sample_df[column]

                # Numeric
                if pd.api.types.is_numeric_dtype(series):
                    numeric_columns.add(column)
                    continue

                # Try detecting date columns
                converted_dates = pd.to_datetime(
                    series,
                    errors="coerce"
                )

                valid_date_ratio = converted_dates.notna().mean()

                if valid_date_ratio >= 0.8:
                    date_columns.add(column)
                    continue

                # Object/string columns
                if pd.api.types.is_object_dtype(series):

                    unique_ratio = (
                        series.nunique(dropna=True) /
                        max(len(series), 1)
                    )

                    average_length = (
                        series.dropna()
                        .astype(str)
                        .str.len()
                        .mean()
                    )

                    # High-cardinality and long text
                    # is treated as text rather than category.
                    if unique_ratio > 0.5 or average_length > 100:
                        text_columns.add(column)
                    else:
                        categorical_columns.add(column)

        return {
            "filename": path.name,
            "file_size_bytes": path.stat().st_size,
            "rows": total_rows,
            "columns": len(column_names or []),
            "column_names": column_names or [],
            "numeric_columns": sorted(numeric_columns),
            "categorical_columns": sorted(categorical_columns),
            "date_columns": sorted(date_columns),
            "text_columns": sorted(text_columns),
            "missing_values": total_missing,
        }