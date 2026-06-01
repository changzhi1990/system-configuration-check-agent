from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, parse_os_release, run_command_store, save_raw_output, set_field, summarize_raw_index


def collect_os(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("os")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    os_release = run_command_store(runner, "os.os_release", ["cat", "/etc/os-release"], raw_outputs, command_meta, warnings)
    parsed = parse_os_release(os_release)
    set_field(section, "distro", parsed.get("ID", "unknown"), "high" if parsed else "none", ["/etc/os-release"])
    set_field(section, "version", parsed.get("VERSION_ID", "unknown"), "high" if parsed else "none", ["/etc/os-release"])
    set_field(section, "pretty_name", parsed.get("PRETTY_NAME", "unknown"), "high" if parsed else "none", ["/etc/os-release"])
    set_field(section, "os_release_raw_source", "/etc/os-release", "high", ["/etc/os-release"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
