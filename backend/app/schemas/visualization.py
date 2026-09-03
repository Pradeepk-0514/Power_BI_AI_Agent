from typing import List, Optional
from pydantic import BaseModel


class VisualizationRecommendation(BaseModel):
    title: str
    chart_type: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    aggregation: Optional[str] = None
    time_granularity: Optional[str] = None
    reason: str


class VisualizationGenerationRequest(BaseModel):
    dataset_id: str
    prompt: str


class VisualizationGenerationResponse(BaseModel):
    dataset_id: str
    prompt: str
    visualizations: List[VisualizationRecommendation]