from __future__ import annotations

from core.models import Finding


def check_pcie(section: dict, _: dict) -> list[Finding]:
    devices = section.get("pcie_devices", [])
    return [
        Finding(
            name="pcie_inventory_visible",
            category="pcie",
            status="PASS" if devices else "WARN",
            observed_value=len(devices),
            expected_or_recommended_value="Relevant PCIe devices should be visible",
            impact="Missing PCIe inventory reduces GPU/NIC placement analysis",
            recommendation="Verify lspci availability and required permissions",
            confidence=section.get("confidence", "none"),
            evidence_sources=section.get("field_sources", {}).get("pcie_devices", []),
        )
    ]
