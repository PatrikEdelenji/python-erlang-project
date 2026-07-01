from collections import defaultdict
from datetime import datetime, timezone, timedelta
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


def get_metrics_by_node(db: Session, node_id: str) -> List[MetricDB]:
    return (
        db.query(MetricDB)
        .filter(MetricDB.node_id == node_id)
        .all()
    )


def get_recent_metrics_for_node(
    db: Session,
    node_id: str,
    limit: int = 10,
) -> List[MetricDB]:
    return (
        db.query(MetricDB)
        .filter(MetricDB.node_id == node_id)
        .order_by(MetricDB.timestamp.desc())
        .limit(limit)
        .all()
    )


def get_alerts(db: Session) -> List[AlertDB]:
    return db.query(AlertDB).all()


def get_recent_alerts(db: Session, minutes: int = 30) -> List[AlertDB]:
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)

    return (
        db.query(AlertDB)
        .filter(AlertDB.timestamp >= cutoff_time)
        .order_by(AlertDB.timestamp.desc())
        .all()
    )


def get_node_ids(db: Session) -> List[str]:
    node_rows = db.query(MetricDB.node_id).distinct().all()

    return [row[0] for row in node_rows]


def get_latest_metric_per_node(db: Session) -> List[MetricDB]:
    node_ids = get_node_ids(db)

    latest_metrics = []

    for node_id in node_ids:
        latest_metric = (
            db.query(MetricDB)
            .filter(MetricDB.node_id == node_id)
            .order_by(MetricDB.timestamp.desc())
            .first()
        )

        if latest_metric:
            latest_metrics.append(latest_metric)

    return latest_metrics


def get_incidents(db: Session, window_minutes: int = 30):
    alerts = get_recent_alerts(db, minutes=window_minutes)

    grouped_alerts = defaultdict(list)

    for alert in alerts:
        grouped_alerts[alert.node_id].append(alert)

    incidents = []

    for node_id, node_alerts in grouped_alerts.items():
        alert_types = sorted({alert.alert_type for alert in node_alerts})
        alert_count = len(node_alerts)

        severity = calculate_severity(
            alert_types=alert_types,
            alert_count=alert_count,
        )

        incidents.append(
            {
                "node_id": node_id,
                "severity": severity,
                "status": "active",
                "alert_count": alert_count,
                "alert_types": alert_types,
                "status_reason": build_status_reason(
                    severity=severity,
                    alert_types=alert_types,
                    alert_count=alert_count,
                    window_minutes=window_minutes,
                ),
                "summary": build_incident_summary(
                    node_id=node_id,
                    alert_count=alert_count,
                    alert_types=alert_types,
                    window_minutes=window_minutes,
                ),
                "recommended_action": build_recommended_action(alert_types),
            }
        )

    return incidents


def calculate_severity(alert_types: List[str], alert_count: int) -> str:
    serious_alert_types = {
        "HIGH_LATENCY",
        "PACKET_LOSS",
        "HIGH_CPU_USAGE",
        "HIGH_MEMORY_USAGE",
    }

    matching_serious_alerts = set(alert_types) & serious_alert_types

    if len(matching_serious_alerts) >= 3 or alert_count >= 10:
        return "critical"

    if len(matching_serious_alerts) >= 2 or alert_count >= 5:
        return "warning"

    return "minor"


def build_status_reason(
    severity: str,
    alert_types: List[str],
    alert_count: int,
    window_minutes: int = 30,
) -> str:
    serious_alert_types = {
        "HIGH_LATENCY",
        "PACKET_LOSS",
        "HIGH_CPU_USAGE",
        "HIGH_MEMORY_USAGE",
    }

    serious_count = len(set(alert_types) & serious_alert_types)

    if severity == "critical":
        if serious_count >= 3:
            return (
                f"Critical because the node has {serious_count} serious alert types "
                f"in the last {window_minutes} minutes."
            )

        return (
            f"Critical because the node has {alert_count} recent alerts "
            f"in the last {window_minutes} minutes."
        )

    if severity == "warning":
        return (
            f"Warning because the node has {alert_count} recent alert(s) "
            f"and {serious_count} serious alert type(s)."
        )

    return (
        f"Minor because the node has only {alert_count} recent alert(s) "
        f"in the last {window_minutes} minutes."
    )


def build_incident_summary(
    node_id: str,
    alert_count: int,
    alert_types: List[str],
    window_minutes: int = 30,
) -> str:
    readable_alerts = ", ".join(alert_types)

    return (
        f"Node {node_id} has {alert_count} recent alert(s) "
        f"in the last {window_minutes} minutes involving: {readable_alerts}."
    )


def build_recommended_action(alert_types: List[str]) -> str:
    actions = []

    if "HIGH_LATENCY" in alert_types:
        actions.append("check network latency and routing")

    if "PACKET_LOSS" in alert_types:
        actions.append("inspect packet loss and network interface errors")

    if "HIGH_CPU_USAGE" in alert_types:
        actions.append("check CPU-heavy processes")

    if "HIGH_MEMORY_USAGE" in alert_types:
        actions.append("check memory pressure and possible leaks")

    if not actions:
        return "Review recent metrics and node logs."

    return "Recommended checks: " + ", ".join(actions) + "."