from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, parse_json_if_possible, run_command_store, save_raw_output, set_field, summarize_raw_index


def collect_cuda(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("cuda")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    nvcc_stdout = run_command_store(runner, "cuda.nvcc", ["nvcc", "--version"], raw_outputs, command_meta, warnings)
    version_json = run_command_store(runner, "cuda.version_json", ["cat", "/usr/local/cuda/version.json"], raw_outputs, command_meta, warnings)
    parsed = parse_json_if_possible(version_json)

    toolkit_version = parsed.get("cuda", {}).get("version", "unknown")
    runtime_version = toolkit_version if toolkit_version != "unknown" else "unknown"
    if "release" in nvcc_stdout:
        runtime_version = nvcc_stdout.split("release", 1)[1].split(",", 1)[0].strip()

    set_field(section, "cuda_detected", toolkit_version != "unknown" or bool(nvcc_stdout), "high" if toolkit_version != "unknown" else "medium" if nvcc_stdout else "none", ["nvcc --version", "/usr/local/cuda/version.json"])
    set_field(section, "cuda_runtime_version", runtime_version, "medium" if runtime_version != "unknown" else "none", ["nvcc --version"])
    set_field(section, "cuda_toolkit_version", toolkit_version, "high" if toolkit_version != "unknown" else "none", ["/usr/local/cuda/version.json"])
    set_field(section, "cuda_sources", ["nvcc --version", "/usr/local/cuda/version.json"], "medium", ["collector"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
