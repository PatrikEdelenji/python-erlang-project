from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field
from fastapi import FastAPI

app = FastAPI(
    title = "Network Intelligence Simulator",
    description = "Python backed for receiving telecom network metrics",
    version = "0.1.0"
)


#pydantic uses ... to represent "required"
#and fastapi is using pydantic models for request validation
#we could have skipped the whole "Field(..., example="node_001")" thing, and just went with node_id: str
class MetricCreate(BaseModel):
    node_id: str = Field(..., example="node_001")
    latency_ms: float = Field(..., example=120)
    packet_loss: float = Field(..., example=1.2)
    cpu_usage: float = Field(..., example=45.0)
    memory_usage: float = Field(..., example=60.0)
    
#backed creates the datetime, because the client should not decite the timestamp
#this is the data the backed sends back
class MetricResponse(MetricCreate):
    timestamp:datetime

metrics_store: List[MetricResponse] = []



@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/metrics", response_model = MetricResponse)
#there is a parameter called metric, fastapi should create it from the request body, the request body must match the metriccreate model
def create_metric(metric: MetricCreate):
    new_metric = MetricResponse(
        #the ** basically unpacks the dictionary into keywords... "node_id"="node_001" to node_id="node_001"
        **metric.model_dump(),
        timestamp=datetime.now(timezone.utc),        
    )

    metrics_store.append(new_metric)

    return new_metric

@app.get("/metrics", response_model=List[MetricResponse])
def get_metrics():
    return metrics_store
