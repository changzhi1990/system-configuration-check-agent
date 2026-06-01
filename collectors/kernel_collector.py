from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, run_command_store, save_raw_output, set_field, summarize_raw_index


def collect_kernel(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("kernel")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    uname_a = run_command_store(runner, "kernel.uname_a", ["uname", "-a"], raw_outputs, command_meta, warnings)
    uname_r = run_command_store(runner, "kernel.uname_r", ["uname", "-r"], raw_outputs, command_meta, warnings)
    cmdline = run_command_store(runner, "kernel.cmdline", ["cat", "/proc/cmdline"], raw_outputs, command_meta, warnings)
    set_field(section, "kernel_version", uname_r or "unknown", "high" if uname_r else "none", ["uname -r"])
    set_field(section, "kernel_arch", uname_a.split()[-2] if uname_a else "unknown", "medium" if uname_a else "none", ["uname -a"])
    set_field(section, "cmdline", cmdline or "unknown", "high" if cmdline else "none", ["/proc/cmdline"])
    important_args = [token for token in cmdline.split() if any(key in token for key in ("iommu", "isolcpus", "nohz_full", "rcu_nocbs"))]
    set_field(section, "important_kernel_args", important_args, "high" if cmdline else "none", ["/proc/cmdline"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
