from __future__ import annotations

from pathlib import Path

from core.command_runner import CommandRunner
from core.utils import finalize_section, new_section, run_command_store, save_raw_output, set_field, summarize_raw_index


def _non_loopback_interfaces() -> list[str]:
    return [path.name for path in Path("/sys/class/net").iterdir() if path.name != "lo"]


def collect_nic(runner: CommandRunner, project_root: Path, save_raw: bool = False, raw_dir: Path | None = None) -> dict:
    section = new_section("nic")
    raw_outputs: dict[str, str] = {}
    command_meta: list[dict] = []
    warnings: list[str] = []
    raw_files: list[str] = []

    run_command_store(runner, "nic.ip_link", ["ip", "-br", "link"], raw_outputs, command_meta, warnings)
    interfaces = _non_loopback_interfaces()
    nics = []
    for iface in interfaces:
        state = Path(f"/sys/class/net/{iface}/operstate").read_text(encoding="utf-8", errors="replace").strip()
        mac = Path(f"/sys/class/net/{iface}/address").read_text(encoding="utf-8", errors="replace").strip()
        numa_node = "unknown"
        device_path = Path(f"/sys/class/net/{iface}/device/numa_node")
        if device_path.exists():
            numa_node = device_path.read_text(encoding="utf-8", errors="replace").strip()
        ethtool_i = run_command_store(runner, f"nic.ethtool_i_{iface}", ["ethtool", "-i", iface], raw_outputs, command_meta, warnings)
        driver = firmware = "unknown"
        for line in ethtool_i.splitlines():
            if line.startswith("driver:"):
                driver = line.split(":", 1)[1].strip()
            if line.startswith("firmware-version:"):
                firmware = line.split(":", 1)[1].strip()
        nics.append(
            {
                "name": iface,
                "state": state,
                "mac": mac,
                "speed": "unknown",
                "pci_bus_id": Path(f"/sys/class/net/{iface}/device").resolve().name if Path(f"/sys/class/net/{iface}/device").exists() else "unknown",
                "numa_node": numa_node,
                "driver": driver,
                "firmware_version": firmware,
                "rdma_capable": "unknown",
                "link_layer": "ethernet",
                "vendor": "unknown",
                "model": "unknown",
                "confidence": "medium",
            }
        )

    set_field(section, "nics", nics, "medium" if nics else "none", ["ip -br link", "/sys/class/net", "ethtool -i"])
    if save_raw and raw_dir:
        for label, text in raw_outputs.items():
            raw_files.append(save_raw_output(raw_dir, f"{section['section']}_{label.replace('.', '_')}", text))
    return {"data": finalize_section(section), "raw_data_index": summarize_raw_index(command_meta, raw_files), "warnings": warnings}
