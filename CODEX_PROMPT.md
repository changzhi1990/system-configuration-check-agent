# Codex Prompt For system-configuration-check-agent

You are asked to generate a production-grade, runnable Linux project named:

`system-configuration-check-agent`

This project is the first agent in a larger Agentic-AI-Benchmark-Agent suite.

================================================================================
1. MISSION
================================================================================

Build a production-quality Linux-only agent that performs:

1. system configuration inspection
2. configuration normalization
3. best-practice validation
4. structured reporting
5. tuning recommendation generation

This agent is ONLY responsible for system configuration check.

It must:
- collect low-level Linux-visible hardware / firmware / OS / driver / topology signals
- validate common GPU server misconfigurations
- produce machine-readable outputs for downstream benchmarking/workload agents
- degrade gracefully if tools are missing or permissions are insufficient
- save raw evidence for traceability
- include NVIDIA topology and peer-access signals when NVIDIA tools are available

It must NOT:
- run heavy benchmarks
- run NCCL bandwidth test workloads
- run agentic workload simulation
- claim unsupported observability
- fabricate BIOS settings, CUDA versions, NCCL versions, or topology relations

================================================================================
2. REQUIRED OBSERVABILITY SCOPE
================================================================================

The agent MUST attempt to collect the following:

- BIOS (Linux-visible signals only)
- CPU information
- NUMA topology
- memory summary
- GPU information
- NIC information
- PCIe device information
- IOMMU status
- GPU driver version
- CUDA version (if accessible)
- NCCL version (if accessible)
- OS version
- kernel version
- key system parameters from sysctl / procfs / kernel cmdline
- GPU topology from `nvidia-smi topo -m`
- GPU peer capability from `nvidia-smi topo -p2p rw`
- plain `nvidia-smi` summary output
- GPU/NIC topology relationship (if accessible)

Important observability rules:
- distinguish direct facts vs inferred signals vs unavailable information
- if not reliably detectable, return `"unknown"` or `"not_accessible"`
- never fabricate values
- for BIOS: Linux can only access partial signals, not full BIOS menu state
- for GPU/NIC topology: if exact mapping is weak, return lower confidence
- always preserve command raw outputs where possible

================================================================================
3. TARGET ENVIRONMENT
================================================================================

- Linux only
- Python 3.10+
- local CLI execution
- no external network dependency at runtime
- should work in root and non-root mode
- if privileged commands fail (e.g. dmidecode), continue with degraded visibility
- if NVIDIA tools are absent, still generate a valid partial report
- if CUDA/NCCL are absent, still generate a valid partial report

================================================================================
4. OUTPUT STYLE REQUIRED FROM YOU
================================================================================

You MUST generate:
- full runnable project code
- all source files
- README.md
- AGENT.md
- SKILLS.md
- requirements.txt
- best_practices.yaml
- sample_report.json
- sample_report.md

You MUST generate REAL code, not pseudocode.

Do NOT:
- output concept explanation only
- output architecture discussion only
- skip file contents
- leave TODO placeholders for core logic
- generate empty stubs without implementation

================================================================================
5. REQUIRED PROJECT STRUCTURE
================================================================================

system-configuration-check-agent/
├── README.md
├── AGENT.md
├── SKILLS.md
├── requirements.txt
├── .gitignore
├── agent.py
├── core/
│   ├── __init__.py
│   ├── command_runner.py
│   ├── logging_utils.py
│   ├── models.py
│   ├── normalizer.py
│   ├── scoring.py
│   ├── reporter.py
│   └── utils.py
├── collectors/
│   ├── __init__.py
│   ├── bios_collector.py
│   ├── cpu_collector.py
│   ├── numa_collector.py
│   ├── memory_collector.py
│   ├── gpu_collector.py
│   ├── nic_collector.py
│   ├── pcie_collector.py
│   ├── iommu_collector.py
│   ├── cuda_collector.py
│   ├── nccl_collector.py
│   ├── os_collector.py
│   ├── kernel_collector.py
│   ├── sysparam_collector.py
│   └── topology_collector.py
├── checkers/
│   ├── __init__.py
│   ├── bios_checker.py
│   ├── cpu_checker.py
│   ├── numa_checker.py
│   ├── memory_checker.py
│   ├── gpu_checker.py
│   ├── nic_checker.py
│   ├── pcie_checker.py
│   ├── iommu_checker.py
│   ├── cuda_checker.py
│   ├── nccl_checker.py
│   ├── kernel_checker.py
│   ├── sysparam_checker.py
│   └── topology_checker.py
├── knowledge/
│   └── best_practices.yaml
├── output/
│   ├── sample_report.json
│   ├── sample_report.md
│   └── raw/
└── tests/
    ├── test_parsers.py
    ├── test_models.py
    ├── test_scoring.py
    └── test_collectors.py

================================================================================
6. CLI REQUIREMENTS
================================================================================

Implement CLI in `agent.py`.

Required examples:
```bash
python agent.py --output output/report.json
python agent.py --output output/report.json --format json
python agent.py --output output/report.md --format markdown
python agent.py --verbose
python agent.py --save-raw
```

Optional:
```bash
python agent.py --category gpu
python agent.py --category topology
python agent.py --raw-dir output/raw
python agent.py --best-practices knowledge/best_practices.yaml
```

CLI behavior:
- `--save-raw` stores raw command outputs in `output/raw/`
- `--verbose` prints collection/check progress
- command failures must not abort the whole run
- final exit code:
  - `0` if report generated successfully or partially successfully
  - non-zero only for unrecoverable framework errors
- report must still be produced if some collectors fail
- `--category` should support collector-only categories even if there is no same-named checker

================================================================================
7. CORE ENGINEERING REQUIREMENTS
================================================================================

Implement these shared capabilities:

7.1 command runner
- safe subprocess execution
- timeout support
- capture stdout/stderr/return code
- sanitize logging
- no shell injection risk
- support command-not-found handling
- support privileged command failure handling

7.2 structured models
Use Python dataclasses or pydantic models for:
- report metadata
- collector outputs
- findings
- scores
- evidence references
- command execution metadata

7.3 confidence levels
All collected or inferred signals must include confidence:
- high   = directly observed from trusted source
- medium = observed from indirect but credible source
- low    = weak inference
- none   = unavailable

7.4 evidence/source traceability
Each key field or finding should include source references when possible, such as:
- command names
- file paths
- parser note

7.5 graceful degradation
If commands like dmidecode / nvidia-smi / ethtool / ibv_devinfo / numactl are missing:
- do not crash
- continue
- mark corresponding sections unavailable
- record failure in `raw_data_index` or `collection_warnings`

================================================================================
8. COLLECTION REQUIREMENTS BY MODULE
================================================================================

------------------------------------------------------------------------------
8.1 BIOS COLLECTOR
------------------------------------------------------------------------------

Linux usually cannot access full BIOS configuration.
Collect ONLY Linux-visible BIOS / firmware signals.

Try to collect:
- BIOS vendor
- BIOS version
- BIOS release date
- system vendor
- product name
- board vendor / board name
- SMBIOS / DMI signals
- boot mode: UEFI vs legacy
- SMT / hyperthreading signal
- NUMA enabled signal
- runtime power / governor clues if accessible
- PCIe MPS / MRRS clues from `lspci -vv`
- kernel cmdline firmware-related signals if relevant

Preferred sources:
- `/sys/class/dmi/id/*`
- `dmidecode`
- `lscpu`
- `/proc/cmdline`
- `lspci -vv`
- `/sys/firmware/efi`

Required BIOS output object:
```json
{
  "bios_vendor": "",
  "bios_version": "",
  "bios_release_date": "",
  "system_vendor": "",
  "product_name": "",
  "board_vendor": "",
  "board_name": "",
  "boot_mode": "",
  "smt_enabled": "",
  "numa_enabled_signal": "",
  "bios_observable_signals": [],
  "bios_unavailable_items": [],
  "confidence": ""
}
```

Do NOT claim:
- exact hidden BIOS toggle values
- full BIOS menu configuration
unless directly verifiable from Linux-visible signals

------------------------------------------------------------------------------
8.2 CPU COLLECTOR
------------------------------------------------------------------------------

Collect:
- CPU model
- architecture
- vendor
- sockets
- cores per socket
- physical core count
- logical CPU count
- threads per core
- base/max frequency if available
- cache summary if available
- selected important CPU flags
- virtualization signal if available

Preferred sources:
- `lscpu`
- `/proc/cpuinfo`

Required fields:
- model
- vendor
- architecture
- sockets
- physical_cores
- logical_cpus
- threads_per_core
- cpu_mhz_info
- cache_summary
- important_flags[]
- virtualization_support
- confidence

------------------------------------------------------------------------------
8.3 NUMA COLLECTOR
------------------------------------------------------------------------------

Collect:
- number of NUMA nodes
- CPUs belonging to each node
- memory per NUMA node if accessible
- automatic NUMA balancing state
- GPU to NUMA affinity if accessible
- NIC to NUMA affinity if accessible

Preferred sources:
- `numactl --hardware`
- `lscpu`
- `/sys/devices/system/node/`
- `/proc/sys/kernel/numa_balancing`
- sysfs links for devices

Required output:
```json
{
  "numa_node_count": 0,
  "nodes": [
    {
      "node_id": 0,
      "cpus": [],
      "memory_mb": null
    }
  ],
  "numa_balancing": "",
  "gpu_numa_affinity": [],
  "nic_numa_affinity": [],
  "confidence": ""
}
```

------------------------------------------------------------------------------
8.4 MEMORY COLLECTOR
------------------------------------------------------------------------------

Collect:
- total system memory
- available memory
- free memory
- DIMM information if accessible
- memory size/speed per DIMM if accessible
- memory channels ONLY if directly inferable, else unknown
- transparent hugepages status
- hugepages summary

Preferred sources:
- `free -m`
- `/proc/meminfo`
- `dmidecode --type memory`
- `/sys/kernel/mm/transparent_hugepage/enabled`

Required fields:
- total_memory_mb
- available_memory_mb
- free_memory_mb
- dimm_count
- dimms[]
- memory_speed_mt_s
- memory_channels
- transparent_hugepages
- hugepages_summary
- confidence

Do NOT fabricate memory channel count.

------------------------------------------------------------------------------
8.5 GPU COLLECTOR
------------------------------------------------------------------------------

Collect:
- GPU vendor
- GPU count
- GPU model
- PCI bus ID
- UUID
- VBIOS version if available
- total memory
- power limit if available
- driver model info if available
- max/current PCIe generation
- max/current PCIe width
- NUMA affinity if accessible
- MIG mode if applicable
- compute capability if accessible
- plain `nvidia-smi` summary output as raw text

Preferred sources:
- `nvidia-smi`
- `nvidia-smi -q`
- `nvidia-smi --query-gpu=... --format=csv,noheader,nounits`
- `lspci`
- `/proc/driver/nvidia/`
- fallback to generic PCIe detection if nvidia-smi absent

Required fields:
```json
{
  "gpu_count": 0,
  "nvidia_smi_summary_raw": "",
  "gpus": [
    {
      "index": 0,
      "vendor": "",
      "name": "",
      "pci_bus_id": "",
      "uuid": "",
      "memory_total_mb": null,
      "vbios_version": "",
      "driver_model_info": "",
      "max_pcie_gen": null,
      "current_pcie_gen": null,
      "max_pcie_width": "",
      "current_pcie_width": "",
      "numa_affinity": "",
      "mig_mode": "",
      "compute_capability": "",
      "confidence": ""
    }
  ]
}
```

------------------------------------------------------------------------------
8.6 NIC COLLECTOR
------------------------------------------------------------------------------

Collect:
- interface names
- state
- MAC address
- vendor/model if available
- PCI bus ID
- link speed if available
- NUMA node if available
- driver version if accessible
- firmware version if accessible
- RDMA / InfiniBand / RoCE signals if available
- link layer if accessible

Preferred sources:
- `ip -br link`
- `ip addr`
- `ethtool -i <iface>`
- `ethtool <iface>`
- `lspci`
- `/sys/class/net/*`
- `ibstat`
- `rdma link`
- `ibv_devinfo`

Required fields:
```json
{
  "nics": [
    {
      "name": "",
      "state": "",
      "mac": "",
      "speed": "",
      "pci_bus_id": "",
      "numa_node": "",
      "driver": "",
      "firmware_version": "",
      "rdma_capable": "",
      "link_layer": "",
      "vendor": "",
      "model": "",
      "confidence": ""
    }
  ]
}
```

------------------------------------------------------------------------------
8.7 PCIE COLLECTOR
------------------------------------------------------------------------------

Collect relevant PCIe devices for GPU server analysis:
- GPUs
- NICs
- NVMe devices
- PCIe bridges / switches if visible

Collect:
- BDF
- class
- vendor/device
- NUMA node if available
- link capability vs negotiated link
- MPS
- MRRS

Preferred sources:
- `lspci`
- `lspci -tv`
- `lspci -vv`

Required fields:
```json
{
  "pcie_devices": [
    {
      "bdf": "",
      "class": "",
      "vendor": "",
      "device": "",
      "numa_node": "",
      "link_cap_speed": "",
      "link_cap_width": "",
      "link_status_speed": "",
      "link_status_width": "",
      "mps": "",
      "mrrs": "",
      "confidence": ""
    }
  ]
}
```

------------------------------------------------------------------------------
8.8 IOMMU COLLECTOR
------------------------------------------------------------------------------

Collect:
- whether IOMMU is enabled
- whether Intel or AMD IOMMU signal exists
- passthrough mode if visible
- kernel cmdline flags
- iommu group count if accessible

Preferred sources:
- `/proc/cmdline`
- `dmesg | grep -i iommu`
- `/sys/kernel/iommu_groups/`

Required fields:
```json
{
  "iommu_enabled": "",
  "iommu_type": "",
  "iommu_passthrough": "",
  "kernel_cmdline_iommu_flags": [],
  "iommu_groups_count": null,
  "confidence": ""
}
```

------------------------------------------------------------------------------
8.9 GPU DRIVER COLLECTOR
------------------------------------------------------------------------------

Collect:
- NVIDIA driver version
- driver source signal if accessible

Preferred sources:
- `nvidia-smi`
- `/proc/driver/nvidia/version`
- package query if safe

Required fields:
- gpu_driver_version
- driver_source_signal
- confidence

------------------------------------------------------------------------------
8.10 CUDA COLLECTOR
------------------------------------------------------------------------------

Collect ONLY if accessible:
- CUDA runtime version
- CUDA toolkit version
- nvcc version
- version.json or version.txt under `/usr/local/cuda`
- CUDA version reported by nvidia-smi

Preferred sources:
- `nvcc --version`
- `/usr/local/cuda/version.json`
- `/usr/local/cuda/version.txt`
- `nvidia-smi`

Required fields:
```json
{
  "cuda_detected": true,
  "cuda_runtime_version": "",
  "cuda_toolkit_version": "",
  "cuda_sources": [],
  "confidence": ""
}
```

Important:
Do NOT assume CUDA toolkit is installed just because driver exists.

------------------------------------------------------------------------------
8.11 NCCL COLLECTOR
------------------------------------------------------------------------------

Collect ONLY if accessible:
- NCCL shared library presence/version
- package version if visible
- library paths
- environment variables relevant to NCCL

Preferred sources:
- `ldconfig -p | grep nccl`
- package manager query
- env vars

Required fields:
```json
{
  "nccl_detected": true,
  "nccl_version": "",
  "nccl_lib_paths": [],
  "nccl_env": {},
  "confidence": ""
}
```

Important:
If NCCL is not discoverable, mark unavailable.
Do NOT fabricate version strings.

------------------------------------------------------------------------------
8.12 OS COLLECTOR
------------------------------------------------------------------------------

Collect:
- distro
- distro version
- pretty name
- ID
- VERSION_ID

Preferred sources:
- `/etc/os-release`
- `hostnamectl`

Required fields:
- distro
- version
- pretty_name
- os_release_raw_source
- confidence

------------------------------------------------------------------------------
8.13 KERNEL COLLECTOR
------------------------------------------------------------------------------

Collect:
- kernel version
- kernel architecture
- uname summary
- boot command line
- selected performance-relevant kernel args

Preferred sources:
- `uname -r`
- `uname -a`
- `/proc/cmdline`

Required fields:
- kernel_version
- kernel_arch
- cmdline
- important_kernel_args[]
- confidence

------------------------------------------------------------------------------
8.14 SYSTEM PARAM COLLECTOR
------------------------------------------------------------------------------

Collect a CURATED subset only.

Must inspect where possible:
- `kernel.numa_balancing`
- `vm.nr_hugepages`
- THP status
- `net.core.rmem_max`
- `net.core.wmem_max`
- irqbalance service state if accessible
- CPU scaling governor if accessible
- isolated CPUs / `nohz_full` / `rcu_nocbs` cmdline flags if present

Preferred sources:
- `sysctl`
- `/proc`
- `/sys/devices/system/cpu/`
- `systemctl is-active irqbalance`
- `/proc/cmdline`

Required fields:
```json
{
  "sysctl": {},
  "procfs": {},
  "cmdline_flags": [],
  "irqbalance_status": "",
  "cpu_governor_summary": "",
  "confidence": ""
}
```

------------------------------------------------------------------------------
8.15 TOPOLOGY COLLECTOR
------------------------------------------------------------------------------

GPU topology collection is mandatory if NVIDIA GPUs exist.

Collect:
- raw output of `nvidia-smi topo -m`
- raw output of `nvidia-smi topo -p2p rw`
- parsed topology matrix
- GPU-to-GPU links
- CPU affinity shown in matrix if present
- NIC entries if present

Required fields:
```json
{
  "topo_matrix_raw": "",
  "topo_p2p_rw_raw": "",
  "topo_nodes": [],
  "gpu_to_gpu_links": [],
  "topo_cpu_affinity": [],
  "confidence": ""
}
```

If parsing fails:
- store raw output
- do not crash
- mark parse quality accordingly

------------------------------------------------------------------------------
8.16 GPU/NIC TOPOLOGY RELATIONSHIP COLLECTOR
------------------------------------------------------------------------------

Collect if accessible:
- whether GPU and NIC appear in same topology matrix
- GPU PCI BDF
- NIC PCI BDF
- GPU NUMA node
- NIC NUMA node
- approximate locality relation
- GPUDirect / RDMA signal ONLY if supported by evidence

Preferred sources:
- `nvidia-smi topo -m`
- `nvidia-smi topo -p2p rw`
- `lspci`
- `/sys/class/net`
- `ethtool -i`
- `ibv_devinfo`
- `rdma link`

Required fields:
```json
{
  "gpu_nic_topology_detected": "",
  "gpu_nic_pairs": [
    {
      "gpu_index": 0,
      "gpu_pci_bus_id": "",
      "nic_name": "",
      "nic_pci_bus_id": "",
      "relation": "",
      "shared_numa_node": "",
      "confidence": ""
    }
  ],
  "gpudirect_rdma_signal": "",
  "confidence": ""
}
```

Important:
If exact mapping is weak or partial, say so clearly.

================================================================================
9. VALIDATION / CHECKER REQUIREMENTS
================================================================================

Each checker must consume normalized collector results and produce findings with:

- name
- category
- status: PASS / WARN / FAIL / INFO
- observed_value
- expected_or_recommended_value
- impact
- recommendation
- confidence
- evidence_sources[]

Required checks include at least:

- BIOS metadata visibility
- boot mode visibility
- CPU topology visibility
- NUMA balancing state
- THP state
- GPU inventory visible
- NIC inventory visible
- PCIe inventory visible
- IOMMU visibility
- CUDA visibility
- NCCL visibility
- kernel version visibility
- CPU governor visibility
- GPU topology matrix availability

================================================================================
10. KNOWLEDGE BASE
================================================================================

Create `knowledge/best_practices.yaml` with human-editable recommended values.

Include categories such as:
- bios
- cpu
- numa
- memory
- gpu
- pcie
- nic
- iommu
- kernel
- cuda
- nccl
- topology

Example structure:
```yaml
bios:
  require_boot_mode_detection: true

numa:
  numa_balancing: 0

memory:
  transparent_hugepage_recommended: "madvise"

pcie:
  require_full_link_width_for_gpu: true

kernel:
  preferred_cpu_governor: "performance"

cuda:
  require_driver_visible: true

nccl:
  allow_missing_nccl: true

topology:
  require_gpu_topology_if_nvidia_present: true
```

Keep the file small, readable, and easy to modify.

================================================================================
11. OUTPUT REPORT SCHEMA
================================================================================

The final JSON report MUST follow this structure:

```json
{
  "report_meta": {
    "agent_name": "system-configuration-check-agent",
    "timestamp": "",
    "hostname": "",
    "collection_status": "success|partial|failed",
    "warnings": []
  },
  "system_summary": {
    "os": {},
    "kernel": {},
    "bios": {},
    "cpu": {},
    "numa": {},
    "memory": {},
    "gpu": {},
    "nic": {},
    "pcie": {},
    "iommu": {},
    "driver": {},
    "cuda": {},
    "nccl": {},
    "sysparam": {},
    "topology": {}
  },
  "findings": [],
  "scores": {
    "overall": 0,
    "breakdown": {
      "firmware_bios": 0,
      "cpu_numa": 0,
      "memory": 0,
      "gpu_pcie": 0,
      "nic_network": 0,
      "software_stack": 0,
      "topology": 0
    }
  },
  "tuning_recommendations": [],
  "raw_data_index": {},
  "collection_warnings": []
}
```

Requirements:
- structured objects, not giant text blobs
- use `"unknown"` / `"not_accessible"` where needed
- include traceability where possible
- include partial results even on degraded runs

================================================================================
12. MARKDOWN SUMMARY REQUIREMENT
================================================================================

Generate a concise Markdown summary report with aligned text tables.

It must include these sections:

- `Report Meta`
- `System Summary`
- `NUMA Layout`
- `GPU Inventory`
- `NIC Inventory`
- `Software Stack`
- `PCIe Summary`
- `Topology Summary`
- `NVIDIA SMI Summary`
- `NVIDIA Topology Matrix`
- `NVIDIA P2P RW Matrix`
- `Findings Summary`
- `Unavailable Sections`
- `Score Summary`
- `Tuning Recommendations`
- `Raw Evidence`

The three NVIDIA sections must be rendered from:
- `system_summary.gpu.nvidia_smi_summary_raw`
- `system_summary.topology.topo_matrix_raw`
- `system_summary.topology.topo_p2p_rw_raw`

Render them as aligned tables with:
- `Line`
- `Content`

================================================================================
13. SCORING MODEL
================================================================================

Implement a transparent, explainable score from 0 to 100.

Suggested weighted categories:
- firmware_bios: 10
- cpu_numa: 20
- memory: 10
- gpu_pcie: 25
- nic_network: 10
- software_stack: 10
- topology: 15

Scoring principles:
- actual misconfigurations reduce score
- incomplete observability reduces confidence, not always score directly
- severe GPU PCIe under-negotiation should reduce score significantly
- enabled NUMA balancing should reduce score moderately
- suspicious THP setting may reduce score moderately
- total logic must be easy to understand in code

================================================================================
14. RAW EVIDENCE STORAGE
================================================================================

If `--save-raw` is enabled, store raw outputs here:
- `output/raw/bios_*.txt`
- `output/raw/cpu_*.txt`
- `output/raw/numa_*.txt`
- etc.

Also store:
- command execution metadata
- failed commands
- stderr where useful

The following files must be supported when NVIDIA tools are present:
- `output/raw/gpu_gpu_nvidia_summary.txt`
- `output/raw/topology_topology_nvidia_topo.txt`
- `output/raw/topology_topology_nvidia_p2p_rw.txt`

================================================================================
15. README.MD REQUIREMENTS
================================================================================

README.md must include:
- what this agent does
- what this agent does NOT do
- supported Linux commands and fallback behavior
- dependency list
- installation
- usage examples
- output examples
- limitations
- root vs non-root behavior
- Linux-only BIOS visibility limitation
- CUDA/NCCL optional visibility limitation
- GPU/NIC topology partial visibility limitation
- note that `nvidia-smi`, `nvidia-smi topo -m`, and `nvidia-smi topo -p2p rw` are collected when available

================================================================================
16. AGENT.MD REQUIREMENTS
================================================================================

AGENT.md must describe:
- role of this agent in the larger benchmark suite
- input/output contract
- downstream usage order
- limitations
- BIOS visibility is partial
- topology mappings may be approximate
- CUDA/NCCL may be unavailable
- NVIDIA topology commands are opportunistic and Linux-visible only

================================================================================
17. SKILLS.MD REQUIREMENTS
================================================================================

Define these callable skills:
- collect_all_system_signals
- validate_system_configuration
- build_structured_report
- export_json_report
- export_markdown_summary

For each skill include:
- purpose
- input
- output
- failure behavior
- dependencies

================================================================================
18. TESTING REQUIREMENTS
================================================================================

Add lightweight tests for:
- parser robustness
- model validation
- scoring logic
- partial/missing command cases
- collector behavior for NVIDIA summary / topo / p2p commands

Tests must not require privileged or real hardware execution.

================================================================================
19. IMPLEMENTATION QUALITY REQUIREMENTS
================================================================================

- Python 3.10+
- modular design
- no giant monolithic file
- safe subprocess usage
- robust parsing
- minimal dependencies
- no cloud APIs
- no internet requirement at runtime
- readable code
- comments only where useful
- production-style structure
- all core paths implemented

================================================================================
20. FINAL INSTRUCTION
================================================================================

Generate the COMPLETE project now.

Output all required files with actual code content.

Do not stop at explanation.
Do not produce pseudocode.
Do not leave major modules unimplemented.
Do not fabricate unsupported observability.

Generate REAL runnable code.*** End Patch
