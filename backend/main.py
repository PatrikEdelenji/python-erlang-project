from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import MetricDB, AlertDB

from pydantic import BaseModel, Field
from fastapi import Depends, FastAPI

app = FastAPI(
    title = "Network Intelligence Simulator",
    description = "Python backed for receiving telecom network metrics",
    version = "0.1.0"
)

Base.metadata.create_all(bind=engine)


#pydantic uses ... to represent "required"
#and fastapi is using pydantic models for request validation
#we could have skipped the whole "Field(..., example="node_001")" thing, and just went with node_id: str
class MetricCreate(BaseModel):
    node_id: str = Field(..., min_length=1,example="node_001")
    latency_ms: float = Field(..., ge=0, example=120)
    packet_loss: float = Field(..., ge=0, le=100, example=1.2)
    cpu_usage: float = Field(..., ge=0, le=100, example=45.0)
    memory_usage: float = Field(..., ge=0, le=100, example=60.0)
    
#backed creates the datetime, because the client should not decite the timestamp
#this is the data the backed sends back
class MetricResponse(MetricCreate):
    timestamp:datetime

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


#metrics_store: List[MetricResponse] = []
#alerts_store: List[AlertResponse] = []

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_for_alerts(metric: MetricDB, db: Session):
    if metric.latency_ms > 200:
        db.add(
            AlertDB(
                node_id=metric.node_id,
                alert_type="HIGH_LATENCY",
                message=f"High latency detected: {metric.latency_ms} ms",
                timestamp=datetime.now(timezone.utc),
            )
        )

    if metric.packet_loss > 5:
        db.add(
            AlertDB(
                node_id=metric.node_id,
                alert_type="PACKET_LOSS",
                message=f"Packet loss detected: {metric.packet_loss}%",
                timestamp=datetime.now(timezone.utc),
            )
        )

    if metric.cpu_usage > 90:
        db.add(
            AlertDB(
                node_id=metric.node_id,
                alert_type="HIGH_CPU_USAGE",
                message=f"High CPU usage detected: {metric.cpu_usage}%",
                timestamp=datetime.now(timezone.utc),
            )
        )

    if metric.memory_usage > 90:
        db.add(
            AlertDB(
                node_id=metric.node_id,
                alert_type="HIGH_MEMORY_USAGE",
                message=f"High memory usage detected: {metric.memory_usage}%",
                timestamp=datetime.now(timezone.utc),
            )
        )

    db.commit()


@app.post("/metrics", response_model = MetricResponse)
#there is a parameter called metric, fastapi should create it from the request body, the request body must match the metriccreate model
#metric - actuall data   MetricCreate - blueprint for what that data should look like
def create_metric(metric: MetricCreate, db: Session = Depends(get_db)):
    db_metric = MetricDB(
        **metric.model_dump(),
        timestamp=datetime.now(timezone.utc),
    )

    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)

    check_for_alerts(db_metric, db)


    return db_metric

@app.get("/metrics", response_model=List[MetricResponse])
def get_metrics(db: Session = Depends(get_db)):
    return db.query(MetricDB).all()

@app.get("/alerts", response_model=List[AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    return db.query(AlertDB).all()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/nodes")
def get_nodes(db: Session = Depends(get_db)):
    node_rows = db.query(MetricDB.node_id).distinct().all()

    node_ids = [row[0] for row in node_rows]

    return {
        "nodes": sorted(node_ids),
        "count": len(node_ids),
    }




    
