from __future__ import annotations

from core.models import Finding


def check_bios(section: dict, _: dict) -> list[Finding]:
    findings = []
    findings.append(
        Finding(
            name="bios_metadata_visible",
            category="bios",
            status="PASS" if section.get("bios_vendor") != "unknown" else "WARN",
            observed_value=section.get("bios_vendor"),
            expected_or_recommended_value="Linux-visible BIOS metadata should be accessible",
            impact="Missing firmware metadata limits observability",
            recommendation="Run with elevated permissions or verify DMI/sysfs exposure if firmware metadata is needed",
            confidence=section.get("field_confidence", {}).get("bios_vendor", "none"),
            evidence_sources=section.get("field_sources", {}).get("bios_vendor", []),
        )
    )
    findings.append(
        Finding(
            name="boot_mode_detected",
            category="bios",
            status="PASS" if section.get("boot_mode") != "legacy_or_unknown" else "INFO",
            observed_value=section.get("boot_mode"),
            expected_or_recommended_value="UEFI preferred when detectable",
            impact="Unknown boot mode reduces firmware clarity",
            recommendation="Verify UEFI presence via /sys/firmware/efi on the target system",
            confidence=section.get("field_confidence", {}).get("boot_mode", "none"),
            evidence_sources=section.get("field_sources", {}).get("boot_mode", []),
        )
    )
    return findings
