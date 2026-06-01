from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import file_value, finalize_section, new_section, parse_numactl, run_command_store, save_raw_output, set_field, summarize_raw_index


def collect_numa(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("numa")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    numactl_stdout = run_command_store(runner, "numa.numactl", ["numactl", "--hardware"], raw_outputs, command_meta, warnings)
    parsed = parse_numactl(numactl_stdout)
    set_field(section, "numa_node_count", parsed["numa_node_count"], "high" if parsed["numa_node_count"] else "none", ["numactl --hardware"])
    set_field(section, "nodes", parsed["nodes"], "high" if parsed["nodes"] else "none", ["numactl --hardware"])
    balancing = file_value(Path("/proc/sys/kernel/numa_balancing"))
    set_field(section, "numa_balancing", balancing if balancing is not None else "unknown", "high" if balancing is not None else "none", ["/proc/sys/kernel/numa_balancing"])
    set_field(section, "gpu_numa_affinity", [], "low", ["topology collector"])
    set_field(section, "nic_numa_affinity", [], "low", ["nic collector"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
