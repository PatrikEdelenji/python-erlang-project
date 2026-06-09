from sqlalchemy import Column, DateTime, Float, Integer, String
from datetime import datetime, timezone

from database import Base


class MetricDB(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, index=True, nullable=False)
    latency_ms = Column(Float, nullable=False)
    packet_loss = Column(Float, nullable=False)
    cpu_usage = Column(Float, nullable=False)
    memory_usage = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AlertDB(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, index=True, nullable=False)
    alert_type = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
