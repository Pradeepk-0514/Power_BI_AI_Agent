from pydantic import BaseModel
from typing import List, Optional


class AnalysisPlanRequest(BaseModel):
    dataset_id: str
    prompt: str


class AnalysisStep(BaseModel):
    step: int
    operation: str
    metric: Optional[str] = None
    aggregation: Optional[str] = None
    group_by: Optional[str] = None
    time_granularity: Optional[str] = None
    analysis_type: Optional[str] = None


class AnalysisPlanResponse(BaseModel):
    dataset_id: str
    prompt: str
    intent: str
    analysis_plan: List[AnalysisStep]