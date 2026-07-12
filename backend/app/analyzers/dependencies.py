from collections import defaultdict, deque
from typing import Any


def analyze_blast_radius(evidence_items: list[Any], affected_services: list[str]) -> dict[str, Any]:
    graph = _load_graph(evidence_items)
    downstream = {service: _walk(graph["downstream"], service) for service in affected_services}
    upstream = {service: _walk(graph["upstream"], service) for service in affected_services}
    shared = sorted({node for nodes in downstream.values() for node in nodes if sum(node in values for values in downstream.values()) > 1})
    paths = []
    for source in affected_services:
        for target in downstream.get(source, []):
            paths.append({"source": source, "target": target, "type": "possible_downstream_impact"})
    return {
        "affected_services": affected_services,
        "upstream_services": upstream,
        "downstream_dependencies": downstream,
        "shared_dependencies": shared,
        "possible_propagation_paths": paths,
        "graph_present": bool(graph["services"]),
    }


def _load_graph(evidence_items: list[Any]) -> dict[str, Any]:
    services: set[str] = set()
    downstream: dict[str, list[str]] = defaultdict(list)
    upstream: dict[str, list[str]] = defaultdict(list)
    for item in evidence_items:
        if item.evidence_type != "dependency":
            continue
        content = item.normalized_content
        payload = content.get("dependencies", content)
        if isinstance(payload, dict):
            for service in payload.get("services", []):
                services.add(service.get("id") or service.get("name"))
            edges = payload.get("dependencies", [])
        elif isinstance(payload, list):
            edges = payload
        else:
            edges = []
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                services.update([source, target])
                downstream[source].append(target)
                upstream[target].append(source)
    return {"services": services, "downstream": downstream, "upstream": upstream}


def _walk(graph: dict[str, list[str]], start: str) -> list[str]:
    seen: set[str] = set()
    queue: deque[str] = deque(graph.get(start, []))
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        queue.extend(graph.get(node, []))
    return sorted(seen)

