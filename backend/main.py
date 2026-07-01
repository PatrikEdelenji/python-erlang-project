import crud

from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from fastapi import Depends, FastAPI

from schemas import MetricCreate, MetricResponse, AlertResponse, IncidentResponse
from alerting import check_for_alerts




app = FastAPI(
    title = "Network Intelligence Simulator",
    description = "Python backed for receiving telecom network metrics",
    version = "0.1.0"
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/metrics", response_model=MetricResponse)
def create_metric(metric: MetricCreate, db: Session = Depends(get_db)):
    db_metric = crud.create_metric(db, metric)

    check_for_alerts(db_metric, db)

    return db_metric

@app.get("/metrics", response_model=list[MetricResponse])
def get_metrics(db: Session = Depends(get_db)):
    return crud.get_metrics(db)


@app.get("/alerts", response_model=list[AlertResponse])
def get_alerts(db: Session = Depends(get_db)):
    return crud.get_alerts(db)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/nodes")
def get_nodes(db: Session = Depends(get_db)):
    node_ids = crud.get_node_ids(db)

    return {
        "nodes": sorted(node_ids),
        "count": len(node_ids),
    }

@app.get("/incidents", response_model=list[IncidentResponse])
def read_incidents(db: Session = Depends(get_db)):
    return crud.get_incidents(db)




    
