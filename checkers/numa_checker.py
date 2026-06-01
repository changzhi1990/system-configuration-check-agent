from __future__ import annotations

from core.models import Finding


def check_numa(section: dict, best: dict) -> list[Finding]:
    balancing = str(section.get("numa_balancing", "unknown"))
    return [
        Finding(
            name="numa_balancing_state",
            category="numa",
            status="WARN" if balancing == str(best.get("numa_balancing", 0)) == "1" or balancing == "1" else "PASS" if balancing == "0" else "INFO",
            observed_value=balancing,
            expected_or_recommended_value=str(best.get("numa_balancing", 0)),
            impact="Kernel NUMA balancing can interfere with deterministic GPU/HPC placement",
            recommendation="Set kernel.numa_balancing=0 for controlled GPU server tuning if workload policy requires it",
            confidence=section.get("field_confidence", {}).get("numa_balancing", "none"),
            evidence_sources=section.get("field_sources", {}).get("numa_balancing", []),
        )
    ]
