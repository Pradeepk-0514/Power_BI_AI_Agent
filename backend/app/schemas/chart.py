from typing import List, Optional

from pydantic import BaseModel


class AxisConfiguration(BaseModel):
    field: Optional[str] = None
    data_type: Optional[str] = None
    aggregation: Optional[str] = None
    granularity: Optional[str] = None


class SortingConfiguration(BaseModel):
    field: Optional[str] = None
    direction: Optional[str] = None


class InteractionConfiguration(BaseModel):
    cross_filter: bool = True
    tooltip: bool = True


class ChartConfiguration(BaseModel):
    title: str
    visual_type: str

    x_axis: AxisConfiguration
    y_axis: AxisConfiguration

    sorting: SortingConfiguration

    interactions: InteractionConfiguration

    description: str


class ChartConfigurationRequest(BaseModel):
    dataset_id: str
    prompt: str


class ChartConfigurationResponse(BaseModel):
    dataset_id: str
    prompt: str
    charts: List[ChartConfiguration]