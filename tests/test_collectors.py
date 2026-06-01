from pathlib import Path

from collectors.gpu_collector import collect_gpu
from collectors.topology_collector import collect_topology


class FakeRunner:
    class Result:
        def __init__(self, command, args, stdout):
            self.command = command
            self.args = args
            self.stdout = stdout
            self.stderr = ""
            self.returncode = 0
            self.timed_out = False
            self.command_found = True
            self.duration_seconds = 0.001

        def model_dump(self, mode="json"):
            return {
                "command": self.command,
                "args": self.args,
                "stdout": self.stdout,
                "stderr": self.stderr,
                "returncode": self.returncode,
                "timed_out": self.timed_out,
                "command_found": self.command_found,
                "duration_seconds": self.duration_seconds,
            }

    def run(self, command, timeout=None):
        key = " ".join(command)
        outputs = {
            "nvidia-smi --query-gpu=index,name,uuid,pci.bus_id,driver_version,memory.total --format=csv,noheader,nounits": (
                "0, NVIDIA H100, GPU-123, 0000:01:00.0, 550.54.15, 81559"
            ),
            "nvidia-smi -q": "Minor Number : 0\nVBIOS Version : 98.02.2E.80.10\nCUDA Compute Capability : 9.0",
            "nvidia-smi": "GPU 0: NVIDIA H100 (UUID: GPU-123)",
            "nvidia-smi topo -m": "\tGPU0\tNIC0\tCPU Affinity\nGPU0\tX\tPIX\t0-63\nNIC0\tPIX\tX\t",
            "nvidia-smi topo -p2p rw": "GPU0\tGPU1\nGPU0\tX\tOK\nGPU1\tOK\tX",
        }
        stdout = outputs.get(key, "")
        return self.Result(key, command, stdout)


def test_gpu_collector_includes_plain_nvidia_smi_raw(tmp_path: Path) -> None:
    runner = FakeRunner()
    result = collect_gpu(runner, tmp_path, save_raw=True, raw_dir=tmp_path / "raw")
    assert result["data"]["nvidia_smi_summary_raw"].startswith("GPU 0:")
    assert any("gpu_gpu_nvidia_summary" in raw_file for raw_file in result["raw_data_index"]["raw_files"])


def test_topology_collector_includes_p2p_raw(tmp_path: Path) -> None:
    runner = FakeRunner()
    result = collect_topology(runner, tmp_path, save_raw=True, raw_dir=tmp_path / "raw")
    assert result["data"]["topo_p2p_rw_raw"].startswith("GPU0")
    assert any("topology_topology_nvidia_p2p_rw" in raw_file for raw_file in result["raw_data_index"]["raw_files"])
