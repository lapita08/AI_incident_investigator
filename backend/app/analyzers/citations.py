from typing import Any


def validate_evidence_references(references: list[str], evidence_items: list[Any]) -> list[str]:
    allowed = {item.display_id for item in evidence_items}
    return [reference for reference in references if reference in allowed]


def invalid_evidence_references(references: list[str], evidence_items: list[Any]) -> list[str]:
    allowed = {item.display_id for item in evidence_items}
    return [reference for reference in references if reference not in allowed]

