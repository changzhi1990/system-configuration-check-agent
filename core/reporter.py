from __future__ import annotations

import json
from pathlib import Path

from core.models import AgentReport, Finding


def _stringify(value: object) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _render_table(headers: list[str], rows: list[list[object]]) -> str:
    rendered = [[_stringify(cell) for cell in row] for row in rows]
    widths = [len(header) for header in headers]
    for row in rendered:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def fmt(cells: list[str]) -> str:
        return " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells))

    sep = "-+-".join("-" * width for width in widths)
    lines = ["```text", fmt(headers), sep]
    lines.extend(fmt(row) for row in rendered)
    lines.append("```")
    return "\n".join(lines)


def _section_rows(section: dict) -> list[list[object]]:
    ignored = {"section", "status", "confidence", "field_confidence", "field_sources", "notes"}
    rows = []
    for key, value in section.items():
        if key in ignored:
            continue
        rows.append([key, value, section.get("field_confidence", {}).get(key, section.get("confidence", "none"))])
    return rows or [["unavailable", "unknown", "none"]]


def _summary_rows(report: AgentReport) -> list[list[object]]:
    return [
        ["Hostname", report.report_meta.hostname],
        ["Collection Status", report.report_meta.collection_status],
        ["Overall Score", report.scores.overall],
        ["OS", report.system_summary["os"].get("pretty_name", "unknown")],
        ["Kernel", report.system_summary["kernel"].get("kernel_version", "unknown")],
        ["CPU", report.system_summary["cpu"].get("model", "unknown")],
        ["GPU Count", report.system_summary["gpu"].get("gpu_count", "unknown")],
        ["NIC Count", len(report.system_summary["nic"].get("nics", []))],
        ["CUDA", report.system_summary["cuda"].get("cuda_toolkit_version", "unknown")],
        ["NCCL", report.system_summary["nccl"].get("nccl_version", "unknown")],
    ]


def _numa_rows(report: AgentReport) -> list[list[object]]:
    nodes = report.system_summary["numa"].get("nodes", [])
    if not nodes:
        return [["unknown", "unknown", "unknown"]]
    return [
        [
            node.get("node_id", "unknown"),
            ",".join(str(cpu) for cpu in node.get("cpus", [])[:8]) + ("..." if len(node.get("cpus", [])) > 8 else ""),
            node.get("memory_mb", "unknown"),
        ]
        for node in nodes
    ]


def _gpu_rows(report: AgentReport) -> list[list[object]]:
    gpus = report.system_summary["gpu"].get("gpus", [])
    if not gpus:
        return [["unknown", "unknown", "unknown", "unknown", "unknown"]]
    return [
        [gpu.get("index"), gpu.get("name"), gpu.get("pci_bus_id"), gpu.get("driver_version"), gpu.get("memory_total_mb")]
        for gpu in gpus
    ]


def _nic_rows(report: AgentReport) -> list[list[object]]:
    nics = report.system_summary["nic"].get("nics", [])
    if not nics:
        return [["unknown", "unknown", "unknown", "unknown", "unknown"]]
    return [
        [nic.get("name"), nic.get("state"), nic.get("pci_bus_id"), nic.get("numa_node"), nic.get("driver")]
        for nic in nics
    ]


def _software_rows(report: AgentReport) -> list[list[object]]:
    iommu = report.system_summary["iommu"]
    return [
        ["BIOS Vendor", report.system_summary["bios"].get("bios_vendor", "unknown")],
        ["BIOS Version", report.system_summary["bios"].get("bios_version", "unknown")],
        ["Boot Mode", report.system_summary["bios"].get("boot_mode", "unknown")],
        ["Driver", report.system_summary["driver"].get("gpu_driver_version", "unknown")],
        ["CUDA", report.system_summary["cuda"].get("cuda_toolkit_version", "unknown")],
        ["NCCL", report.system_summary["nccl"].get("nccl_version", "unknown")],
        ["IOMMU Enabled", iommu.get("iommu_enabled", "unknown")],
        ["IOMMU Type", iommu.get("iommu_type", "unknown")],
        ["IOMMU Passthrough", iommu.get("iommu_passthrough", "unknown")],
    ]


def _pcie_rows(report: AgentReport) -> list[list[object]]:
    devices = report.system_summary["pcie"].get("pcie_devices", [])
    if not devices:
        return [["unknown", "unknown", "unknown"]]
    return [[device.get("bdf"), device.get("class"), device.get("device")] for device in devices[:20]]


def _topology_rows(report: AgentReport) -> list[list[object]]:
    topology = report.system_summary["topology"]
    return [
        ["GPU/NIC Topology Detected", topology.get("gpu_nic_topology_detected", "unknown")],
        ["GPU/NIC Pair Count", len(topology.get("gpu_nic_pairs", []))],
        ["GPU-GPU Link Count", len(topology.get("gpu_to_gpu_links", []))],
        ["GPUDirect RDMA Signal", topology.get("gpudirect_rdma_signal", "unknown")],
    ]


def _finding_rows(report: AgentReport) -> list[list[object]]:
    if not report.findings:
        return [["none", "INFO", "none", "none"]]
    return [[finding.category, finding.status, finding.name, finding.observed_value] for finding in report.findings]


def _raw_rows(report: AgentReport) -> list[list[object]]:
    rows = []
    for section, item in report.raw_data_index.items():
        for path in item.get("raw_files", []):
            rows.append([section, path])
    return rows or [["none", "none"]]


def _multiline_rows(text: str) -> list[list[object]]:
    lines = [line for line in text.splitlines() if line.strip()]
    return [[index + 1, line] for index, line in enumerate(lines)] or [[1, "none"]]


def build_tuning_recommendations(findings: list[Finding]) -> list[str]:
    recommendations: list[str] = []
    for finding in findings:
        if finding.status in {"WARN", "FAIL"} and finding.recommendation:
            recommendations.append(f"[{finding.category}] {finding.recommendation}")
    return recommendations[:20]


def build_markdown_summary(report: AgentReport) -> str:
    top_findings = [finding for finding in report.findings if finding.status in {"FAIL", "WARN"}][:10]
    unavailable = [name for name, section in report.system_summary.items() if section.get("confidence") == "none"]
    lines = [
        f"# {report.report_meta.agent_name}",
        "",
        "## Report Meta",
        "",
        _render_table(
            ["Field", "Value"],
            [
                ["hostname", report.report_meta.hostname],
                ["timestamp", report.report_meta.timestamp],
                ["collection_status", report.report_meta.collection_status],
                ["overall_score", report.scores.overall],
            ],
        ),
        "",
        "## System Summary",
        "",
        _render_table(["Item", "Value"], _summary_rows(report)),
        "",
        "## NUMA Layout",
        "",
        _render_table(["NUMA Node", "CPU Sample", "Memory (MB)"], _numa_rows(report)),
        "",
        "## GPU Inventory",
        "",
        _render_table(["GPU", "Name", "PCI Bus ID", "Driver", "Memory (MB)"], _gpu_rows(report)),
        "",
        "## NIC Inventory",
        "",
        _render_table(["NIC", "State", "PCI Bus ID", "NUMA", "Driver"], _nic_rows(report)),
        "",
        "## Software Stack",
        "",
        _render_table(["Item", "Value"], _software_rows(report)),
        "",
        "## PCIe Summary",
        "",
        _render_table(["BDF", "Class", "Description"], _pcie_rows(report)),
        "",
        "## Topology Summary",
        "",
        _render_table(["Item", "Value"], _topology_rows(report)),
        "",
        "## NVIDIA SMI Summary",
        "",
        _render_table(["Line", "Content"], _multiline_rows(report.system_summary["gpu"].get("nvidia_smi_summary_raw", ""))),
        "",
        "## NVIDIA Topology Matrix",
        "",
        _render_table(["Line", "Content"], _multiline_rows(report.system_summary["topology"].get("topo_matrix_raw", ""))),
        "",
        "## NVIDIA P2P RW Matrix",
        "",
        _render_table(["Line", "Content"], _multiline_rows(report.system_summary["topology"].get("topo_p2p_rw_raw", ""))),
        "",
    ]
    lines.extend(
        [
            "## Findings Summary",
            "",
            _render_table(
                ["Category", "Status", "Name", "Observed"],
                _finding_rows(report),
            ),
            "",
            "## Unavailable Sections",
            "",
            _render_table(["Section"], [[item] for item in unavailable] or [["none"]]),
            "",
            "## Score Summary",
            "",
            _render_table(
                ["Bucket", "Score"],
                [
                    ["firmware_bios", report.scores.breakdown.firmware_bios],
                    ["cpu_numa", report.scores.breakdown.cpu_numa],
                    ["memory", report.scores.breakdown.memory],
                    ["gpu_pcie", report.scores.breakdown.gpu_pcie],
                    ["nic_network", report.scores.breakdown.nic_network],
                    ["software_stack", report.scores.breakdown.software_stack],
                    ["topology", report.scores.breakdown.topology],
                ],
            ),
            "",
            "## Tuning Recommendations",
            "",
            _render_table(["Recommendation"], [[item] for item in report.tuning_recommendations] or [["none"]]),
            "",
            "## Raw Evidence",
            "",
            _render_table(["Section", "Raw File"], _raw_rows(report)),
        ]
    )
    return "\n".join(lines)


def write_json_report(report: AgentReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")


def write_markdown_report(report: AgentReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_markdown_summary(report), encoding="utf-8")
