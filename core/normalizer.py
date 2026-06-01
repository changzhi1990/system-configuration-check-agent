from __future__ import annotations

from copy import deepcopy


EXPECTED_SECTIONS = [
    "os",
    "kernel",
    "bios",
    "cpu",
    "numa",
    "memory",
    "gpu",
    "nic",
    "pcie",
    "iommu",
    "driver",
    "cuda",
    "nccl",
    "sysparam",
    "topology",
]


def _unknown_section(name: str) -> dict:
    return {
        "section": name,
        "status": "unknown",
        "confidence": "none",
        "field_confidence": {},
        "field_sources": {},
        "notes": ["section unavailable"],
    }


def normalize_report_sections(collected: dict[str, dict]) -> dict[str, dict]:
    normalized = {}
    for section in EXPECTED_SECTIONS:
        if section in collected:
            normalized[section] = deepcopy(collected[section])
        else:
            normalized[section] = _unknown_section(section)
    return normalized
