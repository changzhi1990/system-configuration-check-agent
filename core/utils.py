from __future__ import annotations

import json
import os
import platform
import re
from pathlib import Path
from typing import Any

import yaml

from core.command_runner import CommandRunner


ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def utc_timestamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def hostname() -> str:
    return platform.node()


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def observed(value: Any, confidence: str, sources: list[str]) -> tuple[Any, str, list[str]]:
    return value, confidence, sources


def unknown(sources: list[str] | None = None, value: str = "unknown") -> tuple[Any, str, list[str]]:
    return value, "none", list(sources or [])


def set_field(section: dict, field: str, value: Any, confidence: str, sources: list[str]) -> None:
    section[field] = value
    section.setdefault("field_confidence", {})[field] = confidence
    section.setdefault("field_sources", {})[field] = sources


def new_section(name: str) -> dict:
    return {
        "section": name,
        "status": "ok",
        "confidence": "none",
        "field_confidence": {},
        "field_sources": {},
        "notes": [],
    }


def finalize_section(section: dict) -> dict:
    confidences = list(section.get("field_confidence", {}).values())
    if "high" in confidences:
        section["confidence"] = "high"
    elif "medium" in confidences:
        section["confidence"] = "medium"
    elif "low" in confidences:
        section["confidence"] = "low"
    else:
        section["confidence"] = "none"
        section["status"] = "unknown"
    return section


def save_raw_output(raw_dir: Path, name: str, text: str) -> str:
    ensure_directory(raw_dir)
    target = raw_dir / f"{name}.txt"
    target.write_text(text, encoding="utf-8")
    return str(target)


def sanitize_output(text: str) -> str:
    return ANSI_ESCAPE_PATTERN.sub("", text or "").strip()


def parse_key_value_lines(text: str, separator: str = ":") -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if separator not in line:
            continue
        key, value = line.split(separator, 1)
        values[key.strip()] = value.strip()
    return values


def parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    digits = re.sub(r"[^0-9]", "", value)
    return int(digits) if digits else None


def parse_lscpu(text: str) -> dict[str, Any]:
    mapping = parse_key_value_lines(text)
    return {
        "model": mapping.get("Model name", "unknown"),
        "vendor": mapping.get("Vendor ID", "unknown"),
        "architecture": mapping.get("Architecture", "unknown"),
        "sockets": parse_int(mapping.get("Socket(s)")) or 0,
        "physical_cores": (parse_int(mapping.get("Core(s) per socket")) or 0) * (parse_int(mapping.get("Socket(s)")) or 0),
        "logical_cpus": parse_int(mapping.get("CPU(s)")) or 0,
        "threads_per_core": parse_int(mapping.get("Thread(s) per core")) or 0,
        "cpu_mhz_info": {
            "min_mhz": mapping.get("CPU min MHz", "unknown"),
            "max_mhz": mapping.get("CPU max MHz", "unknown"),
        },
        "cache_summary": {
            "l1d": mapping.get("L1d cache", "unknown"),
            "l1i": mapping.get("L1i cache", "unknown"),
            "l2": mapping.get("L2 cache", "unknown"),
            "l3": mapping.get("L3 cache", "unknown"),
        },
        "important_flags": mapping.get("Flags", "").split()[:20],
        "virtualization_support": mapping.get("Virtualization", "unknown"),
    }


def parse_numactl(text: str) -> dict[str, Any]:
    node_count = 0
    nodes: list[dict[str, Any]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("available:"):
            match = re.search(r"available:\s+(\d+)\s+nodes", stripped)
            if match:
                node_count = int(match.group(1))
        elif stripped.startswith("node ") and " cpus:" in stripped:
            match = re.match(r"node\s+(\d+)\s+cpus:\s*(.*)", stripped)
            if match:
                node_id = int(match.group(1))
                cpus = [int(token) for token in match.group(2).split()] if match.group(2) else []
                nodes.append({"node_id": node_id, "cpus": cpus, "memory_mb": None})
        elif stripped.startswith("node ") and " size:" in stripped:
            match = re.match(r"node\s+(\d+)\s+size:\s*(\d+)", stripped)
            if match:
                for node in nodes:
                    if node["node_id"] == int(match.group(1)):
                        node["memory_mb"] = int(match.group(2))
                        break
    return {"numa_node_count": node_count, "nodes": nodes}


def parse_meminfo(text: str) -> dict[str, int]:
    parsed = parse_key_value_lines(text)
    return {
        "total_memory_mb": (parse_int(parsed.get("MemTotal")) or 0) // 1024,
        "available_memory_mb": (parse_int(parsed.get("MemAvailable")) or 0) // 1024,
        "free_memory_mb": (parse_int(parsed.get("MemFree")) or 0) // 1024,
        "hugepages_total": parse_int(parsed.get("HugePages_Total")) or 0,
        "hugepages_free": parse_int(parsed.get("HugePages_Free")) or 0,
    }


def parse_nvidia_query(text: str) -> list[dict[str, Any]]:
    rows = []
    for line in text.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 6:
            continue
        rows.append(
            {
                "index": parse_int(parts[0]),
                "vendor": "NVIDIA",
                "name": parts[1],
                "pci_bus_id": parts[3],
                "uuid": parts[2],
                "memory_total_mb": parse_int(parts[5]),
                "driver_version": parts[4],
            }
        )
    return rows


def parse_os_release(text: str) -> dict[str, str]:
    values = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key] = value.strip().strip('"')
    return values


def parse_topology_matrix(raw_text: str) -> dict[str, Any]:
    text = sanitize_output(raw_text)
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    matrix_lines: list[list[str]] = []
    legend: list[str] = []
    for line in lines:
        if line.startswith("Legend:") or legend:
            legend.append(line)
            continue
        stripped_line = line.strip("\t")
        parts = re.split(r"\s{2,}|\t", stripped_line)
        if line.startswith("\t") and parts and parts[0]:
            parts.insert(0, "")
        matrix_lines.append([part.strip() for part in parts if part.strip()])

    if not matrix_lines:
        return {"topo_matrix_raw": text, "topo_nodes": [], "gpu_to_gpu_links": [], "topo_cpu_affinity": [], "gpu_nic_pairs": []}

    headers = matrix_lines[0]
    peer_headers = [header for header in headers if header.startswith(("GPU", "NIC"))]
    topo_nodes = []
    gpu_to_gpu = []
    cpu_affinity = []
    gpu_nic_pairs = []
    for row in matrix_lines[1:]:
        row_name = row[0]
        values = row[1:]
        topo_nodes.append({"node": row_name, "values": values})
        if row_name.startswith("GPU"):
            peer_values = values[: len(peer_headers)]
            for header, relation in zip(peer_headers, peer_values, strict=False):
                if header.startswith("GPU") and relation not in {"X", "N/A"}:
                    gpu_to_gpu.append({"from": row_name, "to": header, "relation": relation})
                if header.startswith("NIC") and relation not in {"X", "N/A"}:
                    gpu_nic_pairs.append(
                        {
                            "gpu_index": parse_int(row_name.replace("GPU", "")) or 0,
                            "gpu_pci_bus_id": "",
                            "nic_name": header,
                            "nic_pci_bus_id": "",
                            "relation": relation,
                            "shared_numa_node": "unknown",
                            "confidence": "medium",
                        }
                    )
            if len(values) >= len(peer_headers) + 1:
                cpu_affinity.append({"node": row_name, "cpu_affinity": values[-2] if len(values) >= 2 else "unknown"})

    return {
        "topo_matrix_raw": text,
        "topo_nodes": topo_nodes,
        "gpu_to_gpu_links": gpu_to_gpu,
        "topo_cpu_affinity": cpu_affinity,
        "gpu_nic_pairs": gpu_nic_pairs,
    }


def command_result_to_warning(label: str, result_stdout: str, result_stderr: str, returncode: int) -> str:
    reason = result_stderr or result_stdout or f"return code {returncode}"
    return f"{label}: {reason}".strip()


def file_value(path: Path) -> str | None:
    try:
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace").strip()
    except PermissionError:
        return None
    return None


def summarize_raw_index(commands: list[dict[str, Any]], raw_files: list[str]) -> dict[str, Any]:
    return {"commands": commands, "raw_files": raw_files}


def environment_subset(keys: list[str]) -> dict[str, str]:
    return {key: os.environ[key] for key in keys if key in os.environ}


def parse_json_if_possible(text: str) -> dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def run_command_store(
    runner: CommandRunner,
    label: str,
    command: list[str],
    raw_outputs: dict[str, str],
    command_meta: list[dict[str, Any]],
    warnings: list[str],
) -> str:
    result = runner.run(command)
    output = sanitize_output(result.stdout or result.stderr)
    raw_outputs[label] = output or "unknown"
    command_meta.append(result.model_dump(mode="json"))
    if result.returncode != 0:
        warnings.append(command_result_to_warning(label, result.stdout, result.stderr, result.returncode))
    return result.stdout
