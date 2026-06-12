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

def test_normal_metric_creates_no_alert():
    db = Mock()

    metric = MetricDB(
        node_id="node_test",
        latency_ms=100,
        packet_loss=1.0,
        cpu_usage=40,
        memory_usage=50,
        timestamp=datetime.now(timezone.utc),
    )

    check_for_alerts(metric, db)

    db.add.assert_not_called()
    db.commit.assert_called_once()

def test_packet_loss_creates_alert():
    db = Mock()

    metric = MetricDB(
        node_id="node_test",
        latency_ms=100,
        packet_loss=10.0,
        cpu_usage=40,
        memory_usage=50,
        timestamp=datetime.now(timezone.utc),
    )

    check_for_alerts(metric, db)

    db.add.assert_called_once()
    created_alert = db.add.call_args.args[0]

    assert created_alert.alert_type == "PACKET_LOSS"

def test_multiple_bad_values_create_multiple_alerts():
    db = Mock()

    metric = MetricDB(
        node_id="node_test",
        latency_ms=250,
        packet_loss=10.0,
        cpu_usage=95,
        memory_usage=95,
        timestamp=datetime.now(timezone.utc),
    )

    check_for_alerts(metric, db)

    assert db.add.call_count == 4
    db.commit.assert_called_once()