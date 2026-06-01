from __future__ import annotations

import os
from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, run_command_store, save_raw_output, set_field, summarize_raw_index


def collect_nccl(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("nccl")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    ldconfig = run_command_store(runner, "nccl.ldconfig", ["ldconfig", "-p"], raw_outputs, command_meta, warnings)
    lib_lines = [line.strip() for line in ldconfig.splitlines() if "nccl" in line.lower()]
    version = "unknown"
    for path in [Path("/usr/include/nccl.h"), Path("/usr/local/cuda/include/nccl.h")]:
        if path.exists():
            version = "header_present"
            break
    env = {key: value for key, value in os.environ.items() if key.startswith("NCCL_")}

    set_field(section, "nccl_detected", bool(lib_lines) or version != "unknown", "medium" if lib_lines or version != "unknown" else "none", ["ldconfig -p", "nccl.h"])
    set_field(section, "nccl_version", version, "medium" if version != "unknown" else "none", ["nccl.h"])
    set_field(section, "nccl_lib_paths", lib_lines[:20], "medium" if lib_lines else "none", ["ldconfig -p"])
    set_field(section, "nccl_env", env, "high" if env else "none", ["environment"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
