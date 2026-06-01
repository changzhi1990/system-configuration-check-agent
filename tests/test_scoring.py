from core.models import Finding
from core.scoring import score_report


def test_scoring_penalizes_warn_and_fail() -> None:
    findings = [
        Finding(
            name="gpu_inventory_detected",
            category="gpu",
            status="FAIL",
            observed_value=0,
            expected_or_recommended_value=1,
            impact="bad",
            recommendation="fix",
            confidence="high",
            evidence_sources=["nvidia-smi"],
        ),
        Finding(
            name="numa_balancing_state",
            category="numa",
            status="WARN",
            observed_value="1",
            expected_or_recommended_value="0",
            impact="moderate",
            recommendation="disable",
            confidence="high",
            evidence_sources=["/proc/sys/kernel/numa_balancing"],
        ),
    ]
    scores = score_report(findings)
    assert scores.overall < 100
    assert scores.breakdown.gpu_pcie < 25
    assert scores.breakdown.cpu_numa < 20
