from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, parse_topology_matrix, run_command_store, save_raw_output, set_field, summarize_raw_index


def collect_topology(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("topology")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    topo_raw = run_command_store(runner, "topology.nvidia_topo", ["nvidia-smi", "topo", "-m"], raw_outputs, command_meta, warnings)
    p2p_raw = run_command_store(runner, "topology.nvidia_p2p_rw", ["nvidia-smi", "topo", "-p2p", "rw"], raw_outputs, command_meta, warnings)
    parsed = parse_topology_matrix(topo_raw)
    set_field(section, "topo_matrix_raw", parsed["topo_matrix_raw"], "high" if topo_raw else "none", ["nvidia-smi topo -m"])
    set_field(section, "topo_p2p_rw_raw", p2p_raw or "unknown", "high" if p2p_raw else "none", ["nvidia-smi topo -p2p rw"])
    set_field(section, "topo_nodes", parsed["topo_nodes"], "medium" if parsed["topo_nodes"] else "none", ["nvidia-smi topo -m"])
    set_field(section, "gpu_to_gpu_links", parsed["gpu_to_gpu_links"], "medium" if parsed["gpu_to_gpu_links"] else "none", ["nvidia-smi topo -m"])
    set_field(section, "topo_cpu_affinity", parsed["topo_cpu_affinity"], "medium" if parsed["topo_cpu_affinity"] else "none", ["nvidia-smi topo -m"])
    set_field(section, "gpu_nic_topology_detected", bool(parsed["gpu_nic_pairs"]), "medium" if parsed["gpu_nic_pairs"] else "low", ["nvidia-smi topo -m"])
    set_field(section, "gpu_nic_pairs", parsed["gpu_nic_pairs"], "medium" if parsed["gpu_nic_pairs"] else "low", ["nvidia-smi topo -m"])
    set_field(section, "gpudirect_rdma_signal", "unknown", "none", ["not directly observable"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
