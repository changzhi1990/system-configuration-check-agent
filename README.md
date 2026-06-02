# system-configuration-check-agent

Linux-only system configuration inspection agent for GPU servers. This is the first agent in a larger Agentic-AI-Benchmark-Agent suite.

## What This Agent Does

- collects Linux-visible hardware, firmware, OS, driver, and topology signals
- normalizes raw signals into a structured machine-readable report
- validates configuration against editable best practices
- scores configuration health
- generates JSON and Markdown reports
- degrades gracefully when commands are missing or permissions are limited

## What This Agent Does NOT Do

- does not run heavy performance benchmarks
- does not run NCCL bandwidth tests
- does not simulate agentic workloads
- does not fabricate BIOS, CUDA, NCCL, or topology data
- does not require external network access

## Supported Commands And Fallback Behavior

The agent attempts to use Linux-native commands and files such as:

- `lscpu`
- `numactl --hardware`
- `free -m`
- `nvidia-smi`
- `nvidia-smi topo -m`
- `nvidia-smi topo -p2p rw`
- `ip -br link`
- `ethtool`
- `lspci`
- `ldconfig -p`
- `uname -a`
- `sysctl`
- `dmidecode`
- `/proc/*`
- `/sys/*`

If a command is missing or permission is insufficient:

- collection continues
- affected fields are set to `unknown` or `not_accessible`
- warnings are recorded
- JSON and Markdown reports are still generated

## Dependencies

- Python 3.10+
- `pydantic`
- `PyYAML`

No cloud APIs and no internet are required at runtime.

## Installation

```bash
cd system-configuration-check-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If `python3-venv` is unavailable:

```bash
pip3 install --user -r requirements.txt
```

## Usage

```bash
python agent.py --output output/report.json
python agent.py --output output/report.json --format json
python agent.py --output output/report.md --format markdown
python agent.py --verbose
python agent.py --save-raw
python agent.py --category gpu
python agent.py --category topology
python agent.py --raw-dir output/raw
python agent.py --best-practices knowledge/best_practices.yaml
```

## Output

The JSON report contains:

- `report_meta`
- `system_summary`
- `findings`
- `scores`
- `tuning_recommendations`
- `raw_data_index`
- `collection_warnings`

The Markdown summary contains:

- summary tables for firmware, CPU, NUMA, memory, GPU, NIC, PCIe, software, and topology
- top findings and recommendations
- unavailable sections
- score summary

## Root vs Non-Root Behavior

- non-root mode works and is supported
- privileged commands such as `dmidecode` may fail
- failures are converted into warnings and reduced observability, not fatal errors

## Limitations

- BIOS visibility is partial on Linux; hidden firmware menu toggles are not observable
- CUDA toolkit visibility is optional; driver visibility does not imply toolkit install
- NCCL visibility is optional; missing NCCL is reported, not invented
- GPU/NIC topology may be partial or approximate when the platform does not expose exact mapping
- memory channels are only reported when directly inferable; otherwise `unknown`
- NVIDIA topology commands are collected and persisted when available:
  - `nvidia-smi`
  - `nvidia-smi topo -m`
  - `nvidia-smi topo -p2p rw`
