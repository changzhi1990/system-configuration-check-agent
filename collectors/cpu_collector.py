from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, parse_lscpu, run_command_store, save_raw_output, set_field, summarize_raw_index


def collect_cpu(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("cpu")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    lscpu_stdout = run_command_store(runner, "cpu.lscpu", ["lscpu"], raw_outputs, command_meta, warnings)
    parsed = parse_lscpu(lscpu_stdout)
    for field, value in parsed.items():
        set_field(section, field, value if value not in ("", None) else "unknown", "high" if value not in ("", None) else "none", ["lscpu"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
