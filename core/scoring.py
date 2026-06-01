from __future__ import annotations

from core.models import Finding, ScoreBreakdown, Scores


WEIGHTS = {
    "firmware_bios": 10,
    "cpu_numa": 20,
    "memory": 10,
    "gpu_pcie": 25,
    "nic_network": 10,
    "software_stack": 10,
    "topology": 15,
}

CATEGORY_TO_BUCKET = {
    "bios": "firmware_bios",
    "cpu": "cpu_numa",
    "numa": "cpu_numa",
    "memory": "memory",
    "gpu": "gpu_pcie",
    "pcie": "gpu_pcie",
    "nic": "nic_network",
    "iommu": "software_stack",
    "cuda": "software_stack",
    "nccl": "software_stack",
    "kernel": "software_stack",
    "sysparam": "software_stack",
    "topology": "topology",
}

PENALTIES = {
    "FAIL": 8,
    "WARN": 4,
    "INFO": 0,
    "PASS": 0,
}


def score_report(findings: list[Finding]) -> Scores:
    bucket_scores = {bucket: weight for bucket, weight in WEIGHTS.items()}
    for finding in findings:
        bucket = CATEGORY_TO_BUCKET.get(finding.category)
        if not bucket:
            continue
        bucket_scores[bucket] = max(0, bucket_scores[bucket] - PENALTIES[finding.status])

    breakdown = ScoreBreakdown(**bucket_scores)
    overall = sum(bucket_scores.values())
    return Scores(overall=overall, breakdown=breakdown)
