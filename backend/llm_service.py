import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_investigation_answer(
    question: str,
    related_incidents: list[dict],
    recent_metrics: list,
    node_comparison: dict | None,
    related_runbooks: list[dict],
) -> str:
    context = build_context(
        related_incidents=related_incidents,
        recent_metrics=recent_metrics,
        node_comparison=node_comparison,
        related_runbooks=related_runbooks,
    )

    prompt = f"""
You are an AI network operations assistant.

Your job is to explain telecom network incidents using only the provided context.
Do not invent facts. If something is not in the context, say that it is not available.

User question:
{question}

Context:
{context}

Write a clear incident investigation answer with:
1. Short conclusion
2. Evidence from metrics/incidents
3. Comparison with other nodes if available
4. Recommended next checks
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a careful AI assistant for telecom network incident investigation.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


def build_context(
    related_incidents: list[dict],
    recent_metrics: list,
    node_comparison: dict | None,
    related_runbooks: list[dict],
) -> str:
    lines = []

    lines.append("INCIDENTS:")
    for incident in related_incidents:
        lines.append(str(incident))

    lines.append("")
    lines.append("RECENT METRICS:")
    for metric in recent_metrics:
        lines.append(
            str(
                {
                    "node_id": metric.node_id,
                    "latency_ms": metric.latency_ms,
                    "packet_loss": metric.packet_loss,
                    "cpu_usage": metric.cpu_usage,
                    "memory_usage": metric.memory_usage,
                    "timestamp": str(metric.timestamp),
                }
            )
        )

    lines.append("")
    lines.append("NODE COMPARISON:")
    lines.append(str(node_comparison))

    lines.append("")
    lines.append("RUNBOOKS:")
    for runbook in related_runbooks[:3]:
        lines.append(
            str(
                {
                    "title": runbook["title"],
                    "file_name": runbook["file_name"],
                    "snippet": runbook["snippet"],
                }
            )
        )

    return "\n".join(lines)