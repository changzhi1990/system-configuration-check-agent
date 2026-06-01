from __future__ import annotations

from core.models import Finding


def check_nccl(section: dict, best: dict) -> list[Finding]:
    detected = bool(section.get("nccl_detected"))
    allow_missing = bool(best.get("allow_missing_nccl", True))
    status = "PASS" if detected else "INFO" if allow_missing else "WARN"
    return [
        Finding(
            name="nccl_detectable",
            category="nccl",
            status=status,
            observed_value=section.get("nccl_version", "unknown"),
            expected_or_recommended_value="NCCL optional but should be visible if installed",
            impact="Missing NCCL visibility reduces readiness for communication benchmarks",
            recommendation="Install or expose NCCL if downstream agents depend on collective communication",
            confidence=section.get("confidence", "none"),
            evidence_sources=section.get("field_sources", {}).get("nccl_version", []),
        )
    ]
