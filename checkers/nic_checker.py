from __future__ import annotations

from core.models import Finding


def check_nic(section: dict, _: dict) -> list[Finding]:
    nics = section.get("nics", [])
    return [
        Finding(
            name="nic_inventory_visible",
            category="nic",
            status="PASS" if nics else "INFO",
            observed_value=len(nics),
            expected_or_recommended_value="NIC inventory should be visible if present",
            impact="Missing NIC metadata reduces network topology clarity",
            recommendation="Verify ip and sysfs visibility for host interfaces",
            confidence=section.get("confidence", "none"),
            evidence_sources=section.get("field_sources", {}).get("nics", []),
        )
    ]
