from typing import Dict, List


class PromptUnderstandingAgent:

    def __init__(self, dataset_profile: Dict):
        self.dataset_profile = dataset_profile

    def understand(self, prompt: str) -> Dict:
        prompt_lower = prompt.lower()

        columns = self.dataset_profile.get("column_names", [])
        numeric_columns = self.dataset_profile.get("numeric_columns", [])
        categorical_columns = self.dataset_profile.get(
            "categorical_columns", []
        )
        date_columns = self.dataset_profile.get("date_columns", [])

        tasks: List[Dict] = []

        # Detect metrics
        detected_metrics = []

        for column in numeric_columns:
            if column.lower() in prompt_lower:
                detected_metrics.append(column)

        # Detect dimensions
        detected_dimensions = []

        for column in categorical_columns:
            if column.lower() in prompt_lower:
                detected_dimensions.append(column)

        # Detect date analysis
        detected_date = None

        for column in date_columns:
            if column.lower() in prompt_lower:
                detected_date = column

        # Detect common business terms
        if "sales" in prompt_lower and "Sales" in numeric_columns:
            if "growth" in prompt_lower or "trend" in prompt_lower:
                tasks.append({
                    "metric": "Sales",
                    "operation": "sum",
                    "dimension": detected_date or "Order_Date",
                    "analysis": "trend",
                    "time_granularity": "month"
                })

        # Regional comparison
        if "region" in prompt_lower and "Sales" in numeric_columns:
            tasks.append({
                "metric": "Sales",
                "operation": "sum",
                "dimension": "Region",
                "analysis": "comparison",
                "time_granularity": None
            })

        # Profit analysis
        if "profit" in prompt_lower and "Profit" in numeric_columns:
            if "trend" in prompt_lower:
                tasks.append({
                    "metric": "Profit",
                    "operation": "sum",
                    "dimension": detected_date or "Order_Date",
                    "analysis": "trend",
                    "time_granularity": "month"
                })

        # Generic metric detection
        if not tasks:
            for metric in detected_metrics:

                dimension = (
                    detected_dimensions[0]
                    if detected_dimensions
                    else None
                )

                tasks.append({
                    "metric": metric,
                    "operation": "sum",
                    "dimension": dimension,
                    "analysis": "aggregation",
                    "time_granularity": None
                })

        # Determine intent
        if tasks:
            intent = "business_analysis"
        else:
            intent = "unknown"

        return {
            "intent": intent,
            "tasks": tasks
        }