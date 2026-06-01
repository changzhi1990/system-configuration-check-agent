from core.models import AgentReport, Finding, ReportMeta, ScoreBreakdown, Scores
from core.normalizer import normalize_report_sections
from core.reporter import build_markdown_summary


def test_report_model_validation() -> None:
    report = AgentReport(
        report_meta=ReportMeta(
            agent_name="system-configuration-check-agent",
            timestamp="2026-06-01T00:00:00+00:00",
            hostname="sample-host",
            collection_status="partial",
            warnings=[],
        ),
        system_summary={"cpu": {"logical_cpus": 128}},
        findings=[
            Finding(
                name="cpu_topology_visible",
                category="cpu",
                status="PASS",
                observed_value=128,
                expected_or_recommended_value="visible",
                impact="none",
                recommendation="none",
                confidence="high",
                evidence_sources=["lscpu"],
            )
        ],
        scores=Scores(overall=100, breakdown=ScoreBreakdown(firmware_bios=10, cpu_numa=20, memory=10, gpu_pcie=25, nic_network=10, software_stack=10, topology=15)),
        tuning_recommendations=[],
        raw_data_index={},
        collection_warnings=[],
    )
    assert report.report_meta.agent_name == "system-configuration-check-agent"
    assert report.scores.overall == 100


def test_normalizer_keeps_sysparam_section() -> None:
    normalized = normalize_report_sections({"sysparam": {"section": "sysparam", "cpu_governor_summary": "performance"}})
    assert "sysparam" in normalized
    assert normalized["sysparam"]["section"] == "sysparam"


def test_markdown_summary_contains_result_tables() -> None:
    report = AgentReport(
        report_meta=ReportMeta(
            agent_name="system-configuration-check-agent",
            timestamp="2026-06-01T00:00:00+00:00",
            hostname="gpu-host",
            collection_status="success",
            warnings=[],
        ),
        system_summary={
            "os": {
                "section": "os",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "pretty_name": "Ubuntu 22.04.5 LTS",
            },
            "kernel": {
                "section": "kernel",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "kernel_version": "6.8.0-94-generic",
            },
            "bios": {
                "section": "bios",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "bios_vendor": "Enginetech",
                "product_name": "EG8621A4",
            },
            "cpu": {
                "section": "cpu",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "model": "AMD EPYC 9535",
                "logical_cpus": 128,
                "sockets": 2,
                "threads_per_core": 1,
            },
            "numa": {
                "section": "numa",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "numa_node_count": 2,
                "nodes": [{"node_id": 0, "cpus": [0, 1, 2], "memory_mb": 1024}],
            },
            "memory": {
                "section": "memory",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "total_memory_mb": 1024,
                "available_memory_mb": 512,
                "transparent_hugepages": "always [madvise] never",
            },
            "gpu": {
                "section": "gpu",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "gpu_count": 2,
                "nvidia_smi_summary_raw": "GPU 0: NVIDIA H100\\nGPU 1: NVIDIA H100",
                "gpus": [
                    {
                        "index": 0,
                        "name": "NVIDIA H100",
                        "pci_bus_id": "0000:01:00.0",
                        "driver_version": "550.54.15",
                        "memory_total_mb": 81559,
                    }
                ],
            },
            "nic": {
                "section": "nic",
                "confidence": "medium",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "nics": [
                    {
                        "name": "ens5f0np0",
                        "state": "up",
                        "pci_bus_id": "0000:33:00.0",
                        "numa_node": "0",
                        "driver": "mlx5_core",
                        "firmware_version": "16.35.4506",
                    }
                ],
            },
            "pcie": {
                "section": "pcie",
                "confidence": "medium",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "pcie_devices": [{"bdf": "0000:33:00.0", "class": "Ethernet controller"}],
            },
            "iommu": {
                "section": "iommu",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "iommu_enabled": "true",
                "iommu_type": "amd",
                "iommu_passthrough": "true",
            },
            "driver": {
                "section": "driver",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "gpu_driver_version": "550.54.15",
            },
            "cuda": {
                "section": "cuda",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "cuda_toolkit_version": "12.4.1",
            },
            "nccl": {
                "section": "nccl",
                "confidence": "medium",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "nccl_version": "2.20.5",
            },
            "sysparam": {
                "section": "sysparam",
                "confidence": "high",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "sysctl": {"kernel.numa_balancing": "0"},
                "irqbalance_status": "active",
                "cpu_governor_summary": "performance",
            },
            "topology": {
                "section": "topology",
                "confidence": "medium",
                "field_confidence": {},
                "field_sources": {},
                "notes": [],
                "topo_matrix_raw": "GPU0\\tGPU1\\nGPU0\\tX\\tNODE",
                "topo_p2p_rw_raw": "GPU0\\tGPU1\\nGPU0\\tX\\tOK",
                "gpu_nic_topology_detected": True,
                "gpu_nic_pairs": [{"gpu_index": 0, "nic_name": "ens5f0np0", "relation": "NODE"}],
            },
        },
        findings=[
            Finding(
                name="gpu_inventory_detected",
                category="gpu",
                status="PASS",
                observed_value=2,
                expected_or_recommended_value=">=1",
                impact="none",
                recommendation="none",
                confidence="high",
                evidence_sources=["nvidia-smi"],
            )
        ],
        scores=Scores(
            overall=100,
            breakdown=ScoreBreakdown(
                firmware_bios=10,
                cpu_numa=20,
                memory=10,
                gpu_pcie=25,
                nic_network=10,
                software_stack=10,
                topology=15,
            ),
        ),
        tuning_recommendations=["[gpu] none"],
        raw_data_index={
            "gpu": {"commands": [], "raw_files": ["output/raw/gpu_gpu_nvidia_query.txt"]},
            "topology": {"commands": [], "raw_files": ["output/raw/topology_topology_nvidia_topo.txt"]},
        },
        collection_warnings=[],
    )
    summary = build_markdown_summary(report)
    assert "## System Summary" in summary
    assert "## NUMA Layout" in summary
    assert "## GPU Inventory" in summary
    assert "## NIC Inventory" in summary
    assert "## Software Stack" in summary
    assert "## PCIe Summary" in summary
    assert "## Tuning Recommendations" in summary
    assert "## Raw Evidence" in summary
    assert "## NVIDIA SMI Summary" in summary
    assert "## NVIDIA Topology Matrix" in summary
    assert "## NVIDIA P2P RW Matrix" in summary
    assert "NVIDIA H100" in summary
    assert "output/raw/gpu_gpu_nvidia_query.txt" in summary
