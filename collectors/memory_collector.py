from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import file_value, finalize_section, new_section, parse_meminfo, run_command_store, save_raw_output, set_field, summarize_raw_index


def collect_memory(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("memory")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    meminfo_stdout = run_command_store(runner, "memory.meminfo", ["cat", "/proc/meminfo"], raw_outputs, command_meta, warnings)
    parsed = parse_meminfo(meminfo_stdout)
    set_field(section, "total_memory_mb", parsed["total_memory_mb"], "high", ["/proc/meminfo"])
    set_field(section, "available_memory_mb", parsed["available_memory_mb"], "high", ["/proc/meminfo"])
    set_field(section, "free_memory_mb", parsed["free_memory_mb"], "high", ["/proc/meminfo"])
    set_field(section, "dimm_count", "unknown", "none", ["dmidecode --type memory"])
    set_field(section, "dimms", [], "none", ["dmidecode --type memory"])
    set_field(section, "memory_speed_mt_s", "unknown", "none", ["dmidecode --type memory"])
    set_field(section, "memory_channels", "unknown", "none", ["not directly inferable"])
    thp = file_value(Path("/sys/kernel/mm/transparent_hugepage/enabled"))
    set_field(section, "transparent_hugepages", thp if thp else "unknown", "high" if thp else "none", ["/sys/kernel/mm/transparent_hugepage/enabled"])
    set_field(section, "hugepages_summary", {"total": parsed["hugepages_total"], "free": parsed["hugepages_free"]}, "high", ["/proc/meminfo"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
