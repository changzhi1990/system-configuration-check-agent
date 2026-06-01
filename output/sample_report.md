# system-configuration-check-agent

## Report Meta

```text
Field             | Value
------------------+-------------------------------
hostname          | sample-host
timestamp         | 2026-06-01T00:00:00+00:00
collection_status | partial
overall_score     | 92
```

## Major System Traits

### bios

```text
Field                | Value                 | Confidence
---------------------+-----------------------+-----------
bios_vendor          | unknown               | none
bios_version         | unknown               | none
boot_mode            | UEFI                  | medium
smt_enabled          | enabled               | medium
numa_enabled_signal  | enabled               | medium
bios_observable_signals | []                 | none
bios_unavailable_items  | ['bios_vendor', 'bios_version'] | none
```

### cpu

```text
Field              | Value            | Confidence
-------------------+------------------+-----------
model              | AMD EPYC Sample  | high
vendor             | AuthenticAMD     | high
architecture       | x86_64           | high
logical_cpus       | 128              | high
threads_per_core   | 1                | high
virtualization_support | AMD-V        | high
```

## Top Risks

```text
Category | Status | Name                   | Impact                                                   | Recommendation
---------+--------+------------------------+----------------------------------------------------------+-------------------------------------------------------------
gpu      | FAIL   | gpu_inventory_detected | No GPU inventory means GPU benchmark pipeline cannot proceed | Verify nvidia-smi, driver installation, and device visibility
```

## Unavailable Sections

```text
Section
-------
gpu
driver
cuda
nccl
topology
```

## Score Summary

```text
Bucket         | Score
---------------+------
firmware_bios  | 10
cpu_numa       | 20
memory         | 10
gpu_pcie       | 17
nic_network    | 10
software_stack | 10
topology       | 15
```

## Tuning Recommendations

```text
Recommendation
-------------------------------------------------------------
[gpu] Verify nvidia-smi, driver installation, and device visibility
```
