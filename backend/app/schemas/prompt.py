from pydantic import BaseModel, Field
from typing import List, Optional


class PromptRequest(BaseModel):
    dataset_id: str
    prompt: str = Field(..., min_length=3)


class AnalysisTask(BaseModel):
    metric: Optional[str] = None
    operation: Optional[str] = None
    dimension: Optional[str] = None
    analysis: Optional[str] = None
    time_granularity: Optional[str] = None


class PromptAnalysisResponse(BaseModel):
    dataset_id: str
    prompt: str
    intent: str
    tasks: List[AnalysisTask]