from typing import List, Optional

from pydantic import BaseModel


class KPIItem(BaseModel):
    name: str
    metric: str
    aggregation: str
    description: str
    business_meaning: str


class KPIGenerationRequest(BaseModel):
    dataset_id: str
    prompt: str


class KPIGenerationResponse(BaseModel):
    dataset_id: str
    prompt: str
    kpis: List[KPIItem]