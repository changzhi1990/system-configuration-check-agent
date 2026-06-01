from __future__ import annotations

from core.models import Finding


def check_kernel(section: dict, _: dict) -> list[Finding]:
    return [
        Finding(
            name="kernel_version_visible",
            category="kernel",
            status="PASS" if section.get("kernel_version") not in {"unknown", None} else "WARN",
            observed_value=section.get("kernel_version"),
            expected_or_recommended_value="Kernel version should be visible",
            impact="Kernel version is needed for system reproducibility and tuning context",
            recommendation="Ensure uname and /proc are available",
            confidence=section.get("field_confidence", {}).get("kernel_version", "none"),
            evidence_sources=section.get("field_sources", {}).get("kernel_version", []),
        )
    ]
