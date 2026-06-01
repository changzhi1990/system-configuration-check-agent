from __future__ import annotations

from core.models import Finding


def check_iommu(section: dict, _: dict) -> list[Finding]:
    enabled = section.get("iommu_enabled", "unknown")
    return [
        Finding(
            name="iommu_visibility",
            category="iommu",
            status="PASS" if enabled == "true" else "INFO" if enabled == "unknown" else "WARN",
            observed_value=enabled,
            expected_or_recommended_value="IOMMU enabled when platform policy requires it",
            impact="IOMMU state affects passthrough and DMA policy interpretation",
            recommendation="Verify kernel cmdline IOMMU flags if DMA isolation or passthrough mode matters",
            confidence=section.get("field_confidence", {}).get("iommu_enabled", "none"),
            evidence_sources=section.get("field_sources", {}).get("iommu_enabled", []),
        )
    ]
