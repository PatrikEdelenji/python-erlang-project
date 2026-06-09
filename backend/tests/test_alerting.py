from datetime import datetime, timezone
from unittest.mock import Mock

from alerting import check_for_alerts
from models import AlertDB, MetricDB


def test_high_latency_creates_alert():
    db = Mock()

    metric = MetricDB(
        node_id="node_test",
        latency_ms=250,
        packet_loss=1.0,
        cpu_usage=40,
        memory_usage=50,
        timestamp=datetime.now(timezone.utc),
    )

    check_for_alerts(metric, db)

    db.add.assert_called_once()
    db.commit.assert_called_once()

    created_alert = db.add.call_args.args[0]

    assert isinstance(created_alert, AlertDB)
    assert created_alert.node_id == "node_test"
    assert created_alert.alert_type == "HIGH_LATENCY"