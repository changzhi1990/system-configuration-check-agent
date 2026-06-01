from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


Confidence = Literal["high", "medium", "low", "none"]
FindingStatus = Literal["PASS", "WARN", "FAIL", "INFO"]
CollectionStatus = Literal["success", "partial", "failed"]


class CommandExecution(BaseModel):
    command: str
    args: list[str] = Field(default_factory=list)
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    timed_out: bool = False
    command_found: bool = True
    duration_seconds: float = 0.0


class Finding(BaseModel):
    name: str
    category: str
    status: FindingStatus
    observed_value: Any
    expected_or_recommended_value: Any
    impact: str
    recommendation: str
    confidence: Confidence
    evidence_sources: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    firmware_bios: int = 0
    cpu_numa: int = 0
    memory: int = 0
    gpu_pcie: int = 0
    nic_network: int = 0
    software_stack: int = 0
    topology: int = 0


class Scores(BaseModel):
    overall: int = 0
    breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)


class ReportMeta(BaseModel):
    agent_name: str
    timestamp: str
    hostname: str
    collection_status: CollectionStatus
    warnings: list[str] = Field(default_factory=list)


class AgentReport(BaseModel):
    report_meta: ReportMeta
    system_summary: dict[str, Any]
    findings: list[Finding]
    scores: Scores
    tuning_recommendations: list[str]
    raw_data_index: dict[str, Any]
    collection_warnings: list[str]
