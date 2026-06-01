from __future__ import annotations

from core.models import Finding


def check_gpu(section: dict, _: dict) -> list[Finding]:
    gpu_count = int(section.get("gpu_count", 0) or 0)
    return [
        Finding(
            name="gpu_inventory_detected",
            category="gpu",
            status="PASS" if gpu_count > 0 else "FAIL",
            observed_value=gpu_count,
            expected_or_recommended_value="At least one GPU visible on GPU server",
            impact="No GPU inventory means GPU benchmark pipeline cannot proceed",
            recommendation="Verify nvidia-smi, driver installation, and device visibility",
            confidence=section.get("field_confidence", {}).get("gpu_count", "none"),
            evidence_sources=section.get("field_sources", {}).get("gpu_count", []),
        )
    ]
