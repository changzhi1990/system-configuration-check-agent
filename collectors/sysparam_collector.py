from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, run_command_store, save_raw_output, set_field, summarize_raw_index


SYSCTL_KEYS = [
    "kernel.numa_balancing",
    "vm.nr_hugepages",
    "net.core.rmem_max",
    "net.core.wmem_max",
]


def collect_sysparam(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("sysparam")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    sysctl_map = {}
    for key in SYSCTL_KEYS:
        stdout = run_command_store(runner, f"sysparam.{key}", ["sysctl", key], raw_outputs, command_meta, warnings)
        sysctl_map[key] = stdout.split("=", 1)[-1].strip() if "=" in stdout else "unknown"
    thp = run_command_store(runner, "sysparam.thp", ["cat", "/sys/kernel/mm/transparent_hugepage/enabled"], raw_outputs, command_meta, warnings)
    irqbalance = run_command_store(runner, "sysparam.irqbalance", ["systemctl", "is-active", "irqbalance"], raw_outputs, command_meta, warnings)

    governors = []
    for path in Path("/sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq/scaling_governor"):
        try:
            governors.append(path.read_text(encoding="utf-8", errors="replace").strip())
        except OSError:
            continue
    governor_summary = ",".join(sorted(set(governors))) if governors else "unknown"

    set_field(section, "sysctl", sysctl_map, "high", [f"sysctl {key}" for key in SYSCTL_KEYS])
    set_field(section, "procfs", {"transparent_hugepages": thp or "unknown"}, "high" if thp else "none", ["/sys/kernel/mm/transparent_hugepage/enabled"])
    set_field(section, "cmdline_flags", [], "low", ["/proc/cmdline"])
    set_field(section, "irqbalance_status", irqbalance or "unknown", "medium" if irqbalance else "none", ["systemctl is-active irqbalance"])
    set_field(section, "cpu_governor_summary", governor_summary, "medium" if governors else "none", ["/sys/devices/system/cpu"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
