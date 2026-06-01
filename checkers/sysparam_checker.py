from __future__ import annotations

from core.models import Finding


def check_sysparam(section: dict, best: dict) -> list[Finding]:
    governor = str(section.get("cpu_governor_summary", "unknown"))
    preferred = best.get("preferred_cpu_governor", "performance")
    status = "WARN" if governor not in {"unknown", preferred} else "PASS" if governor == preferred else "INFO"
    return [
        Finding(
            name="cpu_governor_summary",
            category="sysparam",
            status=status,
            observed_value=governor,
            expected_or_recommended_value=preferred,
            impact="CPU governor may affect determinism for benchmark workloads",
            recommendation="Prefer performance governor if reproducibility is more important than energy saving",
            confidence=section.get("field_confidence", {}).get("cpu_governor_summary", "none"),
            evidence_sources=section.get("field_sources", {}).get("cpu_governor_summary", []),
        )
    ]
