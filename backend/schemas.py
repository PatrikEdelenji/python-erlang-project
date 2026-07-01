from datetime import datetime

from pydantic import BaseModel, Field

from pydantic import BaseModel
from typing import List


class MetricCreate(BaseModel):
    node_id: str = Field(..., min_length=1, example="node_001")
    latency_ms: float = Field(..., ge=0, example=120)
    packet_loss: float = Field(..., ge=0, le=100, example=1.2)
    cpu_usage: float = Field(..., ge=0, le=100, example=45.0)
    memory_usage: float = Field(..., ge=0, le=100, example=60.0)


class MetricResponse(MetricCreate):
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }


class AlertResponse(BaseModel):
    node_id: str
    alert_type: str
    message: str
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }


class IncidentResponse(BaseModel):
    node_id: str
    severity: str
    status: str
    alert_count: int
    alert_types: List[str]
    summary: str
    recommended_action: str


class AgentAskRequest(BaseModel):
    question: str


class AgentAskResponse(BaseModel):
    question: str
    answer: str
    used_tools: list[str]
    related_incidents: list[IncidentResponse]
    related_runbooks: list[dict]