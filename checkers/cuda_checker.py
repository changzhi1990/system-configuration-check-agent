from __future__ import annotations

from core.models import Finding


def check_cuda(section: dict, _: dict) -> list[Finding]:
    detected = bool(section.get("cuda_detected"))
    return [
        Finding(
            name="cuda_detectable",
            category="cuda",
            status="PASS" if detected else "INFO",
            observed_value=section.get("cuda_toolkit_version", "unknown"),
            expected_or_recommended_value="CUDA visible when toolkit is installed",
            impact="Missing CUDA toolkit visibility may limit downstream workload readiness",
            recommendation="Install or expose CUDA toolkit only if downstream workloads require it",
            confidence=section.get("confidence", "none"),
            evidence_sources=section.get("field_sources", {}).get("cuda_toolkit_version", []),
        )
    ]
