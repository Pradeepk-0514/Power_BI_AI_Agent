from typing import Any, List, Dict

from pydantic import BaseModel


class InsightRequest(BaseModel):

    dataset_id: str
    prompt: str


class InsightItem(BaseModel):

    type: str
    metric: str | None = None
    period: Any | None = None
    value: float | None = None
    category: str | None = None
    percentage: float | None = None
    growth_percentage: float | None = None
    insight: str


class InsightResponse(BaseModel):

    dataset_id: str
    prompt: str
    intent: str
    insights: List[InsightItem]