from __future__ import annotations

import re

from core.models import Finding


SUMMARY_PATTERNS = [
    re.compile(r"^\|\s+\d+\s+NVIDIA", flags=re.MULTILINE),
    re.compile(r"^GPU\s+\d+:", flags=re.MULTILINE),
]


def _count_gpus_from_summary(raw_text: str) -> int:
    if not raw_text:
        return 0
    for pattern in SUMMARY_PATTERNS:
        matches = pattern.findall(raw_text)
        if matches:
            return len(matches)
    return 0


def check_gpu(section: dict, best: dict) -> list[Finding]:
    gpu_count = int(section.get("gpu_count", 0) or 0)
    expected_gpu_count = best.get("expected_gpu_count")
    expected_mismatch = expected_gpu_count is not None and gpu_count != expected_gpu_count
    findings = [
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

    summary_count = _count_gpus_from_summary(str(section.get("nvidia_smi_summary_raw", "")))
    if best.get("warn_on_gpu_count_inconsistency", False) and summary_count and summary_count != gpu_count and not expected_mismatch:
        findings.append(
            Finding(
                name="gpu_inventory_consistency",
                category="gpu",
                status="WARN",
                observed_value=f"gpu_count={gpu_count}, summary_count={summary_count}",
                expected_or_recommended_value="structured GPU count should match nvidia-smi summary count",
                impact="Inconsistent GPU visibility suggests a driver, device, or query instability",
                recommendation="Compare nvidia-smi, nvidia-smi -L, and query-gpu outputs to isolate the missing or unhealthy GPU",
                confidence="high",
                evidence_sources=section.get("field_sources", {}).get("nvidia_smi_summary_raw", []) + section.get("field_sources", {}).get("gpu_count", []),
            )
        )

    if expected_gpu_count is not None and gpu_count != expected_gpu_count:
        findings.append(
            Finding(
                name="gpu_inventory_expected_count",
                category="gpu",
                status="FAIL",
                observed_value=gpu_count,
                expected_or_recommended_value=expected_gpu_count,
                impact="Severe error: GPU server does not expose the expected number of devices, so configuration validation and downstream benchmark results are not trustworthy.",
                recommendation="Treat this node as unhealthy, inspect the missing GPU on the PCIe bus and in nvidia-smi output, then re-run validation after the device is restored.",
                confidence=section.get("field_confidence", {}).get("gpu_count", "none"),
                evidence_sources=section.get("field_sources", {}).get("gpu_count", []),
            )
        )

    return findings
