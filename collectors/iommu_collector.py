from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, run_command_store, save_raw_output, set_field, summarize_raw_index


def collect_iommu(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("iommu")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    cmdline = run_command_store(runner, "iommu.cmdline", ["cat", "/proc/cmdline"], raw_outputs, command_meta, warnings)
    tokens = cmdline.split()
    iommu_flags = [token for token in tokens if "iommu" in token.lower()]
    enabled = "true" if iommu_flags else "unknown"
    iommu_type = "amd" if any("amd_iommu" in token for token in iommu_flags) else "intel" if any("intel_iommu" in token for token in iommu_flags) else "unknown"
    passthrough = "true" if any(token.endswith("=pt") for token in iommu_flags) else "false"
    groups = len(list(Path("/sys/kernel/iommu_groups").iterdir())) if Path("/sys/kernel/iommu_groups").exists() else None

    set_field(section, "iommu_enabled", enabled, "high" if iommu_flags else "none", ["/proc/cmdline"])
    set_field(section, "iommu_type", iommu_type, "medium" if iommu_flags else "none", ["/proc/cmdline"])
    set_field(section, "iommu_passthrough", passthrough, "medium" if iommu_flags else "none", ["/proc/cmdline"])
    set_field(section, "kernel_cmdline_iommu_flags", iommu_flags, "high" if iommu_flags else "none", ["/proc/cmdline"])
    set_field(section, "iommu_groups_count", groups if groups is not None else "unknown", "medium" if groups is not None else "none", ["/sys/kernel/iommu_groups"])

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
