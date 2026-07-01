from pathlib import Path


RUNBOOK_DIR = Path(__file__).resolve().parent / "runbooks"


def search_runbooks(query: str) -> list[dict]:
    results = []

    query_words = set(query.lower().split())

    for file_path in RUNBOOK_DIR.glob("*.md"):
        content = file_path.read_text(encoding="utf-8")
        content_lower = content.lower()

        score = sum(1 for word in query_words if word in content_lower)

        if score > 0:
            results.append(
                {
                    "title": file_path.stem.replace("_", " ").title(),
                    "file_name": file_path.name,
                    "score": score,
                    "snippet": content[:500] + "..." if len(content) > 500 else content,
                }
            )

    results.sort(key=lambda item: item["score"], reverse=True)

    return results