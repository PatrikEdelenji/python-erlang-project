import re
from sqlalchemy.orm import Session

import crud
from runbook_search import search_runbooks


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

    runbook_query = build_runbook_query(question, related_incidents)
    related_runbooks = search_runbooks(runbook_query)

    answer = build_answer(
        question=question,
        node_id=node_id,
        related_incidents=related_incidents,
        related_runbooks=related_runbooks,
    )

    return {
        "question": question,
        "answer": answer,
        "used_tools": [
            "extract_node_id",
            "get_incidents",
            "search_runbooks",
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