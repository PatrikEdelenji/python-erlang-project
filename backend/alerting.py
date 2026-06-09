from datetime import datetime, timezone

from sqlalchemy.orm import Session

from models import AlertDB, MetricDB


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