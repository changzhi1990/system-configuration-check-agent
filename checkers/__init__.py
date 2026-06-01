from __future__ import annotations

from checkers.bios_checker import check_bios
from checkers.cpu_checker import check_cpu
from checkers.cuda_checker import check_cuda
from checkers.gpu_checker import check_gpu
from checkers.iommu_checker import check_iommu
from checkers.kernel_checker import check_kernel
from checkers.memory_checker import check_memory
from checkers.nccl_checker import check_nccl
from checkers.nic_checker import check_nic
from checkers.numa_checker import check_numa
from checkers.pcie_checker import check_pcie
from checkers.sysparam_checker import check_sysparam
from checkers.topology_checker import check_topology


def build_checkers(best_practices: dict) -> dict[str, callable]:
    return {
        "bios": lambda report: check_bios(report["bios"], best_practices.get("bios", {})),
        "cpu": lambda report: check_cpu(report["cpu"], best_practices.get("cpu", {})),
        "numa": lambda report: check_numa(report["numa"], best_practices.get("numa", {})),
        "memory": lambda report: check_memory(report["memory"], best_practices.get("memory", {})),
        "gpu": lambda report: check_gpu(report["gpu"], best_practices.get("gpu", {})),
        "nic": lambda report: check_nic(report["nic"], best_practices.get("nic", {})),
        "pcie": lambda report: check_pcie(report["pcie"], best_practices.get("pcie", {})),
        "iommu": lambda report: check_iommu(report["iommu"], best_practices.get("iommu", {})),
        "cuda": lambda report: check_cuda(report["cuda"], best_practices.get("cuda", {})),
        "nccl": lambda report: check_nccl(report["nccl"], best_practices.get("nccl", {})),
        "kernel": lambda report: check_kernel(report["kernel"], best_practices.get("kernel", {})),
        "sysparam": lambda report: check_sysparam(report["sysparam"], best_practices.get("kernel", {})),
        "topology": lambda report: check_topology(report["topology"], best_practices.get("topology", {})),
    }
