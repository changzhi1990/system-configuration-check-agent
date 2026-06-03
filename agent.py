from __future__ import annotations

import argparse
import sys
from pathlib import Path

from checkers import build_checkers
from collectors import build_collectors
from core.logging_utils import configure_logging, get_logger
from core.models import AgentReport, ReportMeta
from core.normalizer import normalize_report_sections
from core.reporter import build_markdown_summary, build_tuning_recommendations, write_json_report, write_markdown_report
from core.scoring import score_report
from core.utils import ensure_directory, hostname, load_yaml_file, utc_timestamp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Linux system configuration inspection agent")
    parser.add_argument("--output", default="output/report.json", help="Output report path")
    parser.add_argument("--format", choices=["json", "markdown"], default="json", help="Primary output format")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--save-raw", action="store_true", help="Save raw collector outputs")
    parser.add_argument("--category", help="Run only a single collector/checker category")
    parser.add_argument("--raw-dir", default="output/raw", help="Directory for raw collector outputs")
    parser.add_argument("--best-practices", default="knowledge/best_practices.yaml", help="Best practices YAML")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    logger = configure_logging(args.verbose)
    project_root = Path(__file__).resolve().parent
    output_path = (project_root / args.output).resolve()
    raw_dir = (project_root / args.raw_dir).resolve()
    best_practices_path = (project_root / args.best_practices).resolve()

    ensure_directory(output_path.parent)
    if args.save_raw:
        ensure_directory(raw_dir)

    try:
        best_practices = load_yaml_file(best_practices_path)
        collectors = build_collectors(project_root)
        checkers = build_checkers(best_practices)

        selected = args.category
        if selected and selected not in collectors:
            logger.error("Unknown category: %s", selected)
            return 2

        raw_data_index: dict[str, dict] = {}
        collection_warnings: list[str] = []
        collected_sections: dict[str, dict] = {}

        collector_names = [selected] if selected else list(collectors)
        for name in collector_names:
            logger.info("Collecting %s", name)
            result = collectors[name](save_raw=args.save_raw, raw_dir=raw_dir)
            collected_sections[name] = result["data"]
            raw_data_index[name] = result["raw_data_index"]
            collection_warnings.extend(result["warnings"])

        normalized = normalize_report_sections(collected_sections)

        findings = []
        checker_names = [selected] if selected and selected in checkers else list(checkers) if not selected else []
        for name in checker_names:
            logger.info("Checking %s", name)
            findings.extend(checkers[name](normalized))

        scores = score_report(findings)
        recommendations = build_tuning_recommendations(findings)
        collection_status = "success"
        if collection_warnings:
            collection_status = "partial"
        if not normalized:
            collection_status = "failed"

        report = AgentReport(
            report_meta=ReportMeta(
                agent_name="system-configuration-check-agent",
                timestamp=utc_timestamp(),
                hostname=hostname(),
                collection_status=collection_status,
                warnings=sorted(set(collection_warnings)),
            ),
            system_summary=normalized,
            findings=findings,
            scores=scores,
            tuning_recommendations=recommendations,
            raw_data_index=raw_data_index,
            collection_warnings=sorted(set(collection_warnings)),
        )

        json_path = output_path if args.format == "json" else output_path.with_suffix(".json")
        md_path = output_path if args.format == "markdown" else output_path.with_suffix(".md")
        write_json_report(report, json_path)
        write_markdown_report(report, md_path)

        logger.info("JSON report: %s", json_path)
        logger.info("Markdown report: %s", md_path)
        print(f"REPORT_JSON={json_path}")
        print(f"REPORT_MD={md_path}")
        print(md_path.read_text(encoding="utf-8"))
        return 0
    except Exception as exc:  # pragma: no cover - framework fatal path
        get_logger().exception("Unrecoverable framework error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
