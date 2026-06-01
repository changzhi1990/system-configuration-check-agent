from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, run_command_store, save_raw_output, set_field, summarize_raw_index


INTERESTING_CLASSES = ("VGA compatible controller", "Ethernet controller", "Non-Volatile memory controller", "PCI bridge")


def collect_pcie(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("pcie")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    lspci_stdout = run_command_store(runner, "pcie.lspci", ["lspci", "-D", "-nn"], raw_outputs, command_meta, warnings)
    devices = []
    for line in lspci_stdout.splitlines():
        if not any(cls in line for cls in INTERESTING_CLASSES):
            continue
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        bdf, description = parts
        devices.append(
            {
                "bdf": bdf,
                "class": description.split(":", 1)[0],
                "vendor": description,
                "device": description,
                "numa_node": "unknown",
                "link_cap_speed": "unknown",
                "link_cap_width": "unknown",
                "link_status_speed": "unknown",
                "link_status_width": "unknown",
                "mps": "unknown",
                "mrrs": "unknown",
                "confidence": "medium",
            }
        )

    set_field(section, "pcie_devices", devices, "medium" if devices else "none", ["lspci -D -nn"])
    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
