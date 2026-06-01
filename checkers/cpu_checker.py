from __future__ import annotations

from core.models import Finding


def check_cpu(section: dict, _: dict) -> list[Finding]:
    status = "PASS" if section.get("logical_cpus", 0) > 0 else "WARN"
    return [
        Finding(
            name="cpu_topology_visible",
            category="cpu",
            status=status,
            observed_value=section.get("logical_cpus"),
            expected_or_recommended_value="CPU topology should be visible",
            impact="Missing CPU topology reduces scheduler and placement confidence",
            recommendation="Ensure lscpu is available and /proc/cpuinfo is readable",
            confidence=section.get("field_confidence", {}).get("logical_cpus", "none"),
            evidence_sources=section.get("field_sources", {}).get("logical_cpus", []),
        )
    ]
