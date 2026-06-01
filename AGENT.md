# AGENT.md

## Role In The Larger Suite

`system-configuration-check-agent` is the first agent in the broader benchmark suite.

Its responsibility is to:

- inspect system configuration
- normalize Linux-visible signals
- validate configuration against best practices
- produce structured reports
- emit tuning recommendations

It should run before any benchmark or workload agent.

## Input Contract

Inputs:

- local Linux host
- optional CLI category filter
- optional best-practices YAML
- optional raw output directory

## Output Contract

Primary output:

- JSON report matching the structured schema in this project

Optional output:

- Markdown summary report
- raw collector outputs saved under `output/raw/`

## Downstream Consumption

Downstream agents should consume:

- `collection_status`
- normalized system summary fields
- findings
- scores
- tuning recommendations
- raw evidence references

Typical sequence:

1. run `system-configuration-check-agent`
2. review JSON findings and recommendations
3. run a basic benchmark agent
4. run workload benchmark agents

## Explicit Limitations

- Linux only
- BIOS visibility is partial
- some GPU/NIC topology mappings are approximate
- CUDA/NCCL may be unavailable
- absence of evidence is represented as `unknown` or `not_accessible`
