from __future__ import annotations

from pathlib import Path

from collectors.bios_collector import collect_bios
from collectors.cpu_collector import collect_cpu
from collectors.cuda_collector import collect_cuda
from collectors.gpu_collector import collect_gpu
from collectors.iommu_collector import collect_iommu
from collectors.kernel_collector import collect_kernel
from collectors.memory_collector import collect_memory
from collectors.nccl_collector import collect_nccl
from collectors.nic_collector import collect_nic
from collectors.numa_collector import collect_numa
from collectors.os_collector import collect_os
from collectors.pcie_collector import collect_pcie
from collectors.sysparam_collector import collect_sysparam
from collectors.topology_collector import collect_topology
from core.command_runner import CommandRunner


def build_collectors(project_root: Path) -> dict[str, callable]:
    def wrap(fn):
        def _inner(save_raw: bool = False, raw_dir: Path | None = None):
            runner = CommandRunner()
            return fn(runner, project_root, save_raw=save_raw, raw_dir=raw_dir)

        return _inner

    return {
        "bios": wrap(collect_bios),
        "cpu": wrap(collect_cpu),
        "numa": wrap(collect_numa),
        "memory": wrap(collect_memory),
        "gpu": wrap(collect_gpu),
        "nic": wrap(collect_nic),
        "pcie": wrap(collect_pcie),
        "iommu": wrap(collect_iommu),
        "cuda": wrap(collect_cuda),
        "nccl": wrap(collect_nccl),
        "os": wrap(collect_os),
        "kernel": wrap(collect_kernel),
        "sysparam": wrap(collect_sysparam),
        "topology": wrap(collect_topology),
    }
