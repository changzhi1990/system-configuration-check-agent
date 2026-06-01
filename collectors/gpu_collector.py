from __future__ import annotations

import re
from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, parse_nvidia_query, run_command_store, save_raw_output, set_field, summarize_raw_index


def _parse_nvidia_smi_q(text: str) -> dict[int, dict[str, str]]:
    devices: dict[int, dict[str, str]] = {}
    current_index = -1
    for line in text.splitlines():
        if line.strip().startswith("Minor Number"):
            current_index += 1
            devices[current_index] = {}
        elif current_index >= 0 and ":" in line:
            key, value = line.split(":", 1)
            devices[current_index][key.strip()] = value.strip()
    return devices


def collect_gpu(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("gpu")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    summary_stdout = run_command_store(runner, "gpu.nvidia_summary", ["nvidia-smi"], raw_outputs, command_meta, warnings)
    query_stdout = run_command_store(
        runner,
        "gpu.nvidia_query",
        ["nvidia-smi", "--query-gpu=index,name,uuid,pci.bus_id,driver_version,memory.total", "--format=csv,noheader,nounits"],
        raw_outputs,
        command_meta,
        warnings,
    )
    q_stdout = run_command_store(runner, "gpu.nvidia_q", ["nvidia-smi", "-q"], raw_outputs, command_meta, warnings)
    query_rows = parse_nvidia_query(query_stdout)
    q_data = _parse_nvidia_smi_q(q_stdout)

    gpus = []
    for item in query_rows:
        idx = item["index"] or 0
        details = q_data.get(idx, {})
        gpus.append(
            {
                "index": idx,
                "vendor": item["vendor"],
                "name": item["name"],
                "pci_bus_id": item["pci_bus_id"],
                "uuid": item["uuid"],
                "memory_total_mb": item["memory_total_mb"],
                "vbios_version": details.get("VBIOS Version", "unknown"),
                "driver_model_info": details.get("Driver Model", "unknown"),
                "max_pcie_gen": details.get("Max", "unknown"),
                "current_pcie_gen": details.get("Current", "unknown"),
                "max_pcie_width": details.get("Max Link Width", "unknown"),
                "current_pcie_width": details.get("Current Link Width", "unknown"),
                "numa_affinity": details.get("NUMA ID", "unknown"),
                "mig_mode": details.get("MIG Mode", "unknown"),
                "compute_capability": details.get("CUDA Compute Capability", "unknown"),
                "confidence": "high",
            }
        )

    set_field(section, "gpu_count", len(gpus), "high" if gpus else "none", ["nvidia-smi"])
    set_field(section, "gpus", gpus, "high" if gpus else "none", ["nvidia-smi --query-gpu", "nvidia-smi -q"])
    set_field(section, "nvidia_smi_summary_raw", summary_stdout or "unknown", "high" if summary_stdout else "none", ["nvidia-smi"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
