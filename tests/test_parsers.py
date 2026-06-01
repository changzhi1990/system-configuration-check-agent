from core.utils import parse_lscpu, parse_numactl, parse_nvidia_query, parse_topology_matrix


def test_parse_lscpu_handles_common_fields() -> None:
    raw = """Architecture: x86_64
CPU(s): 128
Socket(s): 2
Core(s) per socket: 32
Thread(s) per core: 2
Model name: Example CPU
Vendor ID: GenuineIntel
Virtualization: VT-x
"""
    parsed = parse_lscpu(raw)
    assert parsed["architecture"] == "x86_64"
    assert parsed["logical_cpus"] == 128
    assert parsed["physical_cores"] == 64
    assert parsed["threads_per_core"] == 2


def test_parse_numactl_handles_nodes() -> None:
    raw = """available: 2 nodes (0-1)
node 0 cpus: 0 1
node 0 size: 1024 MB
node 1 cpus: 2 3
node 1 size: 2048 MB
"""
    parsed = parse_numactl(raw)
    assert parsed["numa_node_count"] == 2
    assert parsed["nodes"][0]["cpus"] == [0, 1]
    assert parsed["nodes"][1]["memory_mb"] == 2048


def test_parse_nvidia_query_handles_csv() -> None:
    raw = "0, NVIDIA H100, GPU-123, 0000:01:00.0, 550.54.15, 81559"
    rows = parse_nvidia_query(raw)
    assert rows[0]["index"] == 0
    assert rows[0]["name"] == "NVIDIA H100"


def test_parse_topology_matrix_handles_realistic_shape() -> None:
    raw = """\tGPU0\tGPU1\tNIC0\tCPU Affinity\tNUMA Affinity
GPU0\t X \tNODE\tPIX\t0-63\t0
GPU1\tNODE\t X \tPHB\t0-63\t0
NIC0\tPIX\tPHB\t X \t\t
"""
    parsed = parse_topology_matrix(raw)
    assert parsed["topo_nodes"]
    assert parsed["gpu_to_gpu_links"][0]["relation"] == "NODE"
