# SKILLS.md

## collect_all_system_signals

- purpose: collect Linux-visible firmware, hardware, OS, driver, and topology signals
- input: command runner, optional category filter
- output: normalized `system_summary` sections plus raw evidence metadata
- failure behavior: continue on missing commands and mark affected fields unavailable
- dependencies: Linux commands, `/proc`, `/sys`, optional NVIDIA tools

## validate_system_configuration

- purpose: evaluate collected signals against best practices
- input: normalized system summary and best-practices YAML
- output: list of findings with severity, confidence, impact, and recommendations
- failure behavior: emit INFO/WARN findings when evidence is partial
- dependencies: collector outputs, checker modules

## build_structured_report

- purpose: build the final machine-readable report object
- input: metadata, normalized sections, findings, scores, recommendations, raw index
- output: validated report model
- failure behavior: fail only on framework-level schema errors
- dependencies: core models, scoring, reporter

## export_json_report

- purpose: write the report as JSON
- input: report object and output path
- output: JSON file
- failure behavior: return non-zero only if filesystem writing fails
- dependencies: reporter

## export_markdown_summary

- purpose: write the report as concise human-readable Markdown
- input: report object and output path
- output: Markdown file
- failure behavior: continue even if some sections are unavailable
- dependencies: reporter
