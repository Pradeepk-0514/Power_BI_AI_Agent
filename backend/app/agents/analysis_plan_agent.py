from typing import Dict, List


class AnalysisPlanAgent:

    def generate_plan(self, prompt_result: Dict) -> Dict:

        tasks = prompt_result.get("tasks", [])

        analysis_plan: List[Dict] = []

        for index, task in enumerate(tasks, start=1):

            metric = task.get("metric")
            operation = task.get("operation")
            dimension = task.get("dimension")
            analysis = task.get("analysis")
            time_granularity = task.get("time_granularity")

            step = {
                "step": index,
                "operation": "aggregate",
                "metric": metric,
                "aggregation": operation,
                "group_by": dimension,
                "time_granularity": time_granularity,
                "analysis_type": analysis
            }

            analysis_plan.append(step)

        return {
            "intent": prompt_result.get(
                "intent",
                "unknown"
            ),
            "analysis_plan": analysis_plan
        }