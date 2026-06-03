from checkers.gpu_checker import check_gpu
from core.scoring import score_report


def test_gpu_checker_warns_when_nvidia_smi_summary_count_exceeds_gpu_count() -> None:
    section = {
        "gpu_count": 7,
        "nvidia_smi_summary_raw": "\n".join(
            [
                "|   0  NVIDIA GeForce RTX 5090        Off |",
                "|   1  NVIDIA GeForce RTX 5090        Off |",
                "|   2  NVIDIA GeForce RTX 5090        Off |",
                "|   3  NVIDIA GeForce RTX 5090        Off |",
                "|   4  NVIDIA GeForce RTX 5090        Off |",
                "|   5  NVIDIA GeForce RTX 5090        Off |",
                "|   6  NVIDIA GeForce RTX 5090        Off |",
                "|   7  NVIDIA GeForce RTX 5090        Off |",
            ]
        ),
        "field_confidence": {"gpu_count": "high", "nvidia_smi_summary_raw": "high"},
        "field_sources": {"gpu_count": ["nvidia-smi --query-gpu"], "nvidia_smi_summary_raw": ["nvidia-smi"]},
    }
    findings = check_gpu(section, {"warn_on_gpu_count_inconsistency": True})
    mismatch = [finding for finding in findings if finding.name == "gpu_inventory_consistency"]

    assert mismatch
    assert mismatch[0].status == "WARN"
    assert "summary_count=8" in str(mismatch[0].observed_value)


def test_scoring_drops_when_gpu_inventory_is_inconsistent() -> None:
    section = {
        "gpu_count": 7,
        "nvidia_smi_summary_raw": "GPU 0:\nGPU 1:\nGPU 2:\nGPU 3:\nGPU 4:\nGPU 5:\nGPU 6:\nGPU 7:",
        "field_confidence": {"gpu_count": "high", "nvidia_smi_summary_raw": "high"},
        "field_sources": {"gpu_count": ["nvidia-smi --query-gpu"], "nvidia_smi_summary_raw": ["nvidia-smi"]},
    }
    findings = check_gpu(section, {"warn_on_gpu_count_inconsistency": True, "expected_gpu_count": 8})
    scores = score_report(findings)

    assert scores.overall == 50
    assert scores.breakdown.gpu_pcie == 0


def test_gpu_checker_fails_when_expected_gpu_count_is_missing() -> None:
    section = {
        "gpu_count": 7,
        "nvidia_smi_summary_raw": "GPU 0:\nGPU 1:\nGPU 2:\nGPU 3:\nGPU 4:\nGPU 5:\nGPU 6:\nGPU 7:",
        "field_confidence": {"gpu_count": "high", "nvidia_smi_summary_raw": "high"},
        "field_sources": {"gpu_count": ["nvidia-smi --query-gpu"], "nvidia_smi_summary_raw": ["nvidia-smi"]},
    }
    findings = check_gpu(section, {"expected_gpu_count": 8, "warn_on_gpu_count_inconsistency": True})
    expected = [finding for finding in findings if finding.name == "gpu_inventory_expected_count"]

    assert expected
    assert expected[0].status == "FAIL"
