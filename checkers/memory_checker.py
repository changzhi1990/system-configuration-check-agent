from __future__ import annotations

from core.models import Finding


def check_memory(section: dict, best: dict) -> list[Finding]:
    thp = str(section.get("transparent_hugepages", "unknown"))
    status = "WARN" if thp and "[always]" in thp else "PASS" if "madvise" in thp or "[never]" in thp else "INFO"
    return [
        Finding(
            name="transparent_hugepages_state",
            category="memory",
            status=status,
            observed_value=thp,
            expected_or_recommended_value=best.get("transparent_hugepage_recommended", "madvise"),
            impact="THP can affect latency stability for some GPU/HPC workloads",
            recommendation="Prefer madvise for many benchmark and HPC tuning scenarios unless workload-specific guidance differs",
            confidence=section.get("field_confidence", {}).get("transparent_hugepages", "none"),
            evidence_sources=section.get("field_sources", {}).get("transparent_hugepages", []),
        )
    ]
