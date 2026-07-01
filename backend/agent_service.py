import re
from sqlalchemy.orm import Session

import crud
from runbook_search import search_runbooks

from llm_service import generate_investigation_answer


def answer_question(db: Session, question: str) -> dict:
    node_id = extract_node_id(question)

    incidents = crud.get_incidents(db)

    if node_id:
        related_incidents = [
            incident for incident in incidents
            if incident["node_id"] == node_id
        ]
    else:
        related_incidents = incidents

    recent_metrics = []
    node_comparison = None

    if node_id:
        recent_metrics = crud.get_recent_metrics_for_node(
            db=db,
            node_id=node_id,
            limit=5,
        )

        node_comparison = compare_node_to_others(
            db=db,
            node_id=node_id,
        )

    runbook_query = build_runbook_query(question, related_incidents)
    related_runbooks = search_runbooks(runbook_query)

    answer = generate_investigation_answer(
        question=question,
        related_incidents=related_incidents,
        recent_metrics=recent_metrics,
        node_comparison=node_comparison,
        related_runbooks=related_runbooks,
    )

    return {
        "question": question,
        "answer": answer,
        "used_tools": [
            "extract_node_id",
            "get_incidents",
            "get_recent_metrics",
            "compare_node_to_others",
            "search_runbooks",
            "generate_llm_answer",
        ],
        "related_incidents": related_incidents,
        "related_runbooks": related_runbooks[:3],
    }


def extract_node_id(question: str) -> str | None:
    match = re.search(r"erlang_node_\d+", question)

    if match:
        return match.group(0)

    return None


def build_runbook_query(question: str, related_incidents: list[dict]) -> str:
    alert_types = []

    for incident in related_incidents:
        alert_types.extend(incident["alert_types"])

    return question + " " + " ".join(alert_types)


def build_answer(
    question: str,
    node_id: str | None,
    related_incidents: list[dict],
    related_runbooks: list[dict],
) -> str:
    if not related_incidents:
        if node_id:
            return (
                f"I could not find an active incident for {node_id}. "
                "Check whether the node has recent alerts or whether the simulator is currently running."
            )

        return (
            "I could not find active incidents. "
            "Check whether alerts have been generated or whether the simulator is currently running."
        )

    lines = []

    if node_id:
        lines.append(f"Investigation result for {node_id}:")
    else:
        lines.append("Current incident investigation summary:")

    lines.append("")

    for incident in related_incidents:
        lines.append(
            f"- Node {incident['node_id']} is marked as {incident['severity']} "
            f"with {incident['alert_count']} alert(s)."
        )
        lines.append(
            f"  Alert types: {', '.join(incident['alert_types'])}."
        )
        lines.append(
            f"  {incident['recommended_action']}"
        )

    if related_runbooks:
        lines.append("")
        lines.append("Relevant runbooks:")
        for runbook in related_runbooks[:3]:
            lines.append(f"- {runbook['title']} ({runbook['file_name']})")

    return "\n".join(lines)

def compare_node_to_others(db: Session, node_id: str) -> dict | None:
    latest_metrics = crud.get_latest_metric_per_node(db)

    target_metric = None
    other_metrics = []

    for metric in latest_metrics:
        if metric.node_id == node_id:
            target_metric = metric
        else:
            other_metrics.append(metric)

    if not target_metric or not other_metrics:
        return None

    avg_latency = sum(metric.latency_ms for metric in other_metrics) / len(other_metrics)
    avg_packet_loss = sum(metric.packet_loss for metric in other_metrics) / len(other_metrics)
    avg_cpu_usage = sum(metric.cpu_usage for metric in other_metrics) / len(other_metrics)
    avg_memory_usage = sum(metric.memory_usage for metric in other_metrics) / len(other_metrics)

    return {
        "node_id": node_id,
        "latency_ms": {
            "node": target_metric.latency_ms,
            "others_average": round(avg_latency, 2),
            "difference": round(target_metric.latency_ms - avg_latency, 2),
        },
        "packet_loss": {
            "node": target_metric.packet_loss,
            "others_average": round(avg_packet_loss, 2),
            "difference": round(target_metric.packet_loss - avg_packet_loss, 2),
        },
        "cpu_usage": {
            "node": target_metric.cpu_usage,
            "others_average": round(avg_cpu_usage, 2),
            "difference": round(target_metric.cpu_usage - avg_cpu_usage, 2),
        },
        "memory_usage": {
            "node": target_metric.memory_usage,
            "others_average": round(avg_memory_usage, 2),
            "difference": round(target_metric.memory_usage - avg_memory_usage, 2),
        },
    }