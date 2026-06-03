from __future__ import annotations

from pathlib import Path

import agent


def test_main_prints_markdown_report(monkeypatch, tmp_path: Path, capsys) -> None:
    class DummyCollector:
        def __call__(self, save_raw=False, raw_dir=None):
            return {
                "data": {
                    "section": "os",
                    "status": "ok",
                    "confidence": "high",
                    "field_confidence": {},
                    "field_sources": {},
                    "notes": [],
                    "distro": "ubuntu",
                    "version": "24.04",
                    "pretty_name": "Ubuntu 24.04.4 LTS",
                    "os_release_raw_source": "/etc/os-release",
                },
                "raw_data_index": {"commands": [], "raw_files": []},
                "warnings": [],
            }

    monkeypatch.setattr(agent, "build_collectors", lambda project_root: {"os": DummyCollector()})
    monkeypatch.setattr(agent, "build_checkers", lambda best_practices: {})
    monkeypatch.setattr(agent, "load_yaml_file", lambda path: {})
    monkeypatch.setattr(agent, "hostname", lambda: "test-host")
    monkeypatch.setattr(agent, "utc_timestamp", lambda: "2026-06-03T00:00:00+00:00")
    monkeypatch.setattr(
        agent,
        "parse_args",
        lambda: type(
            "Args",
            (),
            {
                "output": str(tmp_path / "report.json"),
                "format": "json",
                "verbose": False,
                "save_raw": False,
                "category": "os",
                "raw_dir": str(tmp_path / "raw"),
                "best_practices": str(tmp_path / "best_practices.yaml"),
            },
        )(),
    )

    rc = agent.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert "# system-configuration-check-agent" in captured.out
    assert "## System Summary" in captured.out
    assert "report.json" in captured.out
