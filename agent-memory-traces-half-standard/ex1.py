import json
import secrets
import time
from difflib import SequenceMatcher

NOW = time.time()
STORE = {
    "mem-a": {"type": "semantic", "text": "Customer prefers invoices by email", "created": NOW, "retired": False},
    "mem-b": {"type": "semantic", "text": "Customer prefers invoices by post", "created": NOW, "retired": True},
}


def relevance(query, text):
    return SequenceMatcher(None, query.lower(), text.lower()).ratio()


def search_memory(query):
    started = time.time()
    live = sorted(
        ((relevance(query, m["text"]), key, m) for key, m in STORE.items() if not m["retired"]),
        reverse=True,
    )
    best = next(iter(live), None)
    score, mem_id, mem = best if best else (None, None, None)
    span = {
        "name": "memory.search",
        "span_id": secrets.token_hex(8),
        "start": started,
        "end": time.time(),
        "attributes": {
            # Layer one: the concepts AOS asks for. Map to current OTel GenAI names.
            "std.memory.type": mem["type"] if mem else None,
            "std.memory.query": query,
            "std.memory.content": mem["text"] if mem else None,
            # Layer two: your own conventions, clearly namespaced.
            "app.memory.id": mem_id,
            "app.memory.relevance": score,
            "app.memory.age_seconds": (started - mem["created"]) if mem else None,
            "app.memory.retired_ids": sorted(k for k, m in STORE.items() if m["retired"]),
        },
    }
    return mem, span


if __name__ == "__main__":
    _, span = search_memory("how does the customer want invoices")
    print(json.dumps(span))
