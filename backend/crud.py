from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session

from models import AlertDB, MetricDB
from schemas import MetricCreate


def create_metric(db: Session, metric: MetricCreate) -> MetricDB:
    db_metric = MetricDB(
        **metric.model_dump(),
        timestamp=datetime.now(timezone.utc),
    )

    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)

    return db_metric


def get_metrics(db: Session) -> List[MetricDB]:
    return db.query(MetricDB).all()


def get_alerts(db: Session) -> List[AlertDB]:
    return db.query(AlertDB).all()


def get_node_ids(db: Session) -> List[str]:
    node_rows = db.query(MetricDB.node_id).distinct().all()

    return [row[0] for row in node_rows]