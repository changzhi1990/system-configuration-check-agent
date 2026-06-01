from __future__ import annotations

from core.models import Finding


def check_topology(section: dict, best: dict) -> list[Finding]:
    matrix = section.get("topo_matrix_raw", "")
    require_topology = bool(best.get("require_gpu_topology_if_nvidia_present", True))
    status = "PASS" if matrix else "WARN" if require_topology else "INFO"
    return [
        Finding(
            name="gpu_topology_matrix_available",
            category="topology",
            status=status,
            observed_value=bool(matrix),
            expected_or_recommended_value=require_topology,
            impact="Missing topology matrix reduces locality and peer-path analysis quality",
            recommendation="Ensure nvidia-smi topo -m is available when NVIDIA GPUs are present",
            confidence=section.get("field_confidence", {}).get("topo_matrix_raw", "none"),
            evidence_sources=section.get("field_sources", {}).get("topo_matrix_raw", []),
        )
    ]
