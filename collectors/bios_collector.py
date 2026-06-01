from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import file_value, finalize_section, new_section, run_command_store, save_raw_output, set_field, summarize_raw_index


def collect_bios(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("bios")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    dmi_paths = {
        "bios_vendor": Path("/sys/class/dmi/id/bios_vendor"),
        "bios_version": Path("/sys/class/dmi/id/bios_version"),
        "bios_release_date": Path("/sys/class/dmi/id/bios_date"),
        "system_vendor": Path("/sys/class/dmi/id/sys_vendor"),
        "product_name": Path("/sys/class/dmi/id/product_name"),
        "board_vendor": Path("/sys/class/dmi/id/board_vendor"),
        "board_name": Path("/sys/class/dmi/id/board_name"),
    }
    for field, path in dmi_paths.items():
        value = file_value(path)
        set_field(section, field, value or "unknown", "high" if value else "none", [str(path)])

    boot_mode = "UEFI" if Path("/sys/firmware/efi").exists() else "legacy_or_unknown"
    set_field(section, "boot_mode", boot_mode, "high" if Path("/sys/firmware/efi").exists() else "medium", ["/sys/firmware/efi"])

    lscpu_stdout = run_command_store(runner, "bios.lscpu", ["lscpu"], raw_outputs, command_meta, warnings)
    threads_per_core = 1
    numa_nodes = 0
    for line in lscpu_stdout.splitlines():
        if line.startswith("Thread(s) per core:"):
            threads_per_core = int(line.split(":", 1)[1].strip() or "0")
        if line.startswith("NUMA node(s):"):
            numa_nodes = int(line.split(":", 1)[1].strip() or "0")
    set_field(section, "smt_enabled", "enabled" if threads_per_core > 1 else "disabled_or_unknown", "medium", ["lscpu"])
    set_field(section, "numa_enabled_signal", "enabled" if numa_nodes > 1 else "disabled_or_unknown", "medium", ["lscpu"])

    lspci_vv = run_command_store(runner, "bios.lspci_vv", ["lspci", "-vv"], raw_outputs, command_meta, warnings)
    observable_signals = [line.strip() for line in lspci_vv.splitlines() if "MaxPayload" in line or "MaxReadReq" in line][:10]
    section["bios_observable_signals"] = observable_signals
    section["bios_unavailable_items"] = [field for field in dmi_paths if section[field] == "unknown"]

    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))

    return {
        "data": finalize_section(section),
        "raw_data_index": summarize_raw_index(command_meta, raw_files),
        "warnings": warnings,
    }
