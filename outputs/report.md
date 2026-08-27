# NimbusAI — GPU Cost Optimization & FinOps Audit Report

> **Executive Deliverable · AICB Track 2 (Infrastructure) · Day 25**  
> **Organization:** NimbusAI (LLM Startup)  
> **Prepared by:** FinOps Engineering Lead  
> **As-of Data Snapshot:** June 2026 (Deterministic Seed=25)  

---

## 1. Executive Summary: Baseline vs. Optimized Spend

NimbusAI was facing unsustainable GPU computing expenses due to unoptimized cluster utilization, static on-demand procurement, and naive LLM inference routing. Through an end-to-end GPU FinOps audit, we restructured infrastructure spending across four core optimization pillars.

**Period:** monthly  
**Baseline spend:** $27,133  
**Optimized spend:** $14,550  
**Projected savings:** $12,583  (**46%**)

### Key FinOps Performance Indicators

| Financial / Operational Metric | Baseline (Pre-Audit) | Optimized (Post-FinOps) | Delta / Savings | % Improvement |
|---|:---:|:---:|:---:|:---:|
| **Monthly Total Spend** | **$27,133** | **$14,550** | **$12,583** | **46.4%** |
| **Unit Economics (`$/1M-token`)** | **$6.488 / 1M** | **$1.126 / 1M** | **$5.362 / 1M** | **82.6%** |
| **Daily Inference Run-rate** | $48.87 / day | $8.48 / day | $40.39 / day | 82.6% |
| **Monthly Purchasing Commitments** | $25,667 / mo | $15,551 / mo | $10,116 / mo | 39.4% |
| **Idle GPU Burn (`gpu-h100-5`)** | $600 / mo | $0 / mo | $600 / mo | 100.0% |
| **GPU-Util Lie Mismatch (`gpu-h100-4`)** | $655 / mo | $0 / mo | $655 / mo | 100.0% |
| **FinOps Tag Allocation Coverage** | N/A (Untracked) | 92.0% | +92.0% | Chargeback Ready |

---

## 2. Savings Breakdown by FinOps Lever

The total projected savings of **$12,583/month (46%)** is broken down across four distinct, non-overlapping architectural levers:

| Lever | Source Mission | Savings (USD / Month) | Share of Total Savings (%) | Technical Complexity | Payback Velocity |
|---|:---:|:---:|:---:|:---:|:---:|
| **Inference (cascade/cache/batch)** | M2 | **$1,212** | **9.6%** | Medium | < 2 weeks |
| **Purchasing (spot/reserved)** | M3 | **$10,116** | **80.4%** | Low-Med | Immediate (<1 mo) |
| **Right-size util-lies** | M1 | **$655** | **5.2%** | Low | < 2 weeks |
| **Kill idle GPUs** | M1 | **$600** | **4.8%** | Low | Immediate (<1 mo) |

---

## 3. Technical Deep-Dive: Root Cause Analysis of the 'GPU-Util Lie'

### Hardware Mechanism: Why `nvidia-smi` Reads 98% While MFU is Only 19.4%

A critical vulnerability identified during the Mission 1 audit was that traditional DevOps dashboards relied on `nvidia-smi` `GPU-Util %`. In production:
- Node `gpu-h100-4` (H100 PCIe/SXM) exhibited **98.2% GPU-Util**, yet achieved an **MFU of only 0.194 (19.4%)** and **MBU of 0.207**.
- Node `gpu-a10g-1` (A10G) exhibited **96.9% GPU-Util**, yet achieved an **MFU of only 0.268 (26.8%)** and **MBU of 0.302**.

#### The Underlying Hardware Mechanisms:
1. **Sampling Artifact of SM Active Clocks:**  
   `nvidia-smi` reports the percentage of time during a sampling interval where at least one warp is resident or scheduled on a Streaming Multiprocessor (SM). It measures *clock time occupation*, **NOT** compute throughput or Tensor Core utilization.

2. **Roofline Model & Arithmetic Intensity Disparity:**  
   The NVIDIA H100 (BF16 Tensor Core) has an operational Ridge Point of **~295 FLOP/Byte** ($990 \text{ TFLOPs} / 3.35 \text{ TB/s}$).
   - **LLM Prefill Phase:** Operates as a GEMM (Matrix-Matrix multiplication) over all prompt tokens ($N$). Arithmetic intensity is high (~455 FLOP/Byte > 295), placing execution in the **Compute-Bound** regime where Tensor Cores are saturated (MFU ~40-45%).
   - **LLM Decode Phase:** Operates as a GEMV (Matrix-Vector multiplication) generating one token at a time per request (Batch size = 1). Arithmetic intensity plummets to **1–2 FLOP/Byte** ($\ll 295$). Execution is severely **Memory-Bound**.

3. **Memory Bandwidth Stalls:**  
   During decode, the entire 80GB model weight tensor must be retrieved from HBM3 memory across the memory bus for every single generated token. The SMs spend >80% of clock cycles stalled waiting for DRAM line fills (**Memory Stalls**). While `nvidia-smi` flags the clock as '100% active', Tensor Cores sit completely idle.

4. **Kernel Launch Overheads & Inter-GPU Synchronization:**  
   Unbatched small requests introduce host-to-device launch latency, and Tensor Parallelism (TP) AllReduce barriers over NVLink force warps into lock-step wait states.

### Financial Impact:
NimbusAI was paying premium H100 On-Demand rates (**$2.50/hour**) for workloads performing compute equivalent to an entry-level GPU ($0.80/hour). Right-sizing `gpu-h100-4` to an A100/L4 memory-matched node recovers **$655/month** with zero degradation in user-facing token latency.

---

## 4. Prioritized Strategic Action Plan (Ranked by ROI)

To maximize financial return with minimal operational friction, the FinOps remediation actions are prioritized as follows:

### Priority 1: Purchasing Strategy Modernization (Immediate ROI — $10,116 / mo, 80.4% Share)
- **Actions:**
  1. Migrate all 5 interruptible workloads (`job-train-llm`, `job-train-embed`, `job-finetune`, `job-dev-sandbox`, `job-batch-eval`) to **Spot Instances** with automated persistent state checkpointing (saving 40–60% per GPU-hour).
  2. Commit to **3-Year Reserved Instances** (45% discount) for continuous 24/7 inference workloads (`job-infer-chat`, `job-infer-rag`, `job-infer-search`), where duty cycle (75–100%) substantially exceeds the 55% break-even threshold (1 - 0.45 = 55%).
- **Rationale:** Requires zero application code refactoring; captures 80.4% of all potential savings starting on the next billing invoice.

### Priority 2: Inference Pipeline Modernization (High Volume ROI — $1,212 / mo, 82.6% Unit Cost Drop)
- **Actions:**
  1. **Cascade Routing:** Implement proxy-level complexity classification. Route 70% of standard user traffic to the small model tier ($0.20/1M in, $0.40/1M out), escalating only complex reasoning tasks to the large model ($3.00/1M in, $15.00/1M out).
  2. **Prompt Prefix Caching:** Cache repetitive system instructions, formatting schemas, and RAG document contexts, slashing input token fees by 90% (0.10x multiplier).
  3. **Batch API:** Process asynchronous evaluation and indexing traffic with a 50% discount via offline batch queues.
- **Rationale:** Decreases unit cost from **$6.488 to $1.126 / 1M-token**. As NimbusAI scales from 7.5M to 100M+ tokens/day, this lever becomes the dominant source of margin expansion.

### Priority 3: Fleet Right-Sizing & De-provisioning (Low Effort — $1,255 / mo, 10.0% Share)
- **Actions:**
  1. **Right-size Util-Lies:** Demote memory-bound decode instances (`gpu-h100-4` -> A100/L4), saving $655/month.
  2. **Auto-terminate Idle Nodes:** Deploy a cluster-wide automated reaper daemon to shut down unallocated GPUs (e.g., `gpu-h100-5` idle 8h/day) after 15 minutes of inactivity, reclaiming $600/month.

---

## 5. Sustainability & Regional Carbon Governance

FinOps and GreenOps converge: intelligent region selection reduces electricity expense and carbon emissions simultaneously.

### Regional Grid Carbon & Electricity Comparison

| Cloud Region | Primary Energy Source | Grid Carbon Intensity (`gCO2/kWh`) | Industrial Power Tariff (`$/kWh`) | 30-Day Carbon for Flexible Jobs (4,227 kWh) | Monthly Power Bill |
|---|---|:---:|:---:|:---:|:---:|
| **europe-north1** (Norway) | 100% Hydroelectric | **30** (Cleanest) | $0.090 | **126.8 kg CO2e** | $380.43 |
| **us-east-wa** (Washington State) | Hydroelectric | 90 | **$0.055** (Cheapest) | 380.4 kg CO2e | **$232.49** |
| **us-west-2** (Oregon) | Hydro + Wind Mix | 120 | $0.070 | 507.2 kg CO2e | $295.89 |
| **us-east-1** (Virginia — Baseline) | Mixed Grid (Gas/Coal) | 380 | $0.120 | 1,606.3 kg CO2e | $507.24 |
| **europe-central2** (Poland) | Coal Dominant | 660 (Dirtiest) | $0.180 | 2,789.8 kg CO2e | $760.86 |

### Carbon Reduction & Cost Arbitrage:
- **Shifting Flexible Training Workloads to `europe-north1`:**
  - Carbon emissions drop from 1,606.3 kg to 126.8 kg CO2e/month $\rightarrow$ **1,479.5 kg CO2e saved (92.1% reduction)**.
  - Electricity costs drop by **$126.81/month** (and drop by **$274.75/month** if routed to `us-east-wa`).
- **Operational Latency Trade-offs:**
  - Training, fine-tuning, and batch evaluation jobs are **latency-insensitive**; their execution should be hard-pinned to `europe-north1` or `us-east-wa`.
  - Interactive user chat inference is **latency-sensitive**; it must remain deployed at regional edge hubs (e.g., `us-east-1`, `us-west-2`) to guarantee Time-to-First-Token (TTFT) < 200ms.

### Per-Query Environmental Footprint:
- **Energy per query (800 tokens median):** 0.24 Wh
- **Carbon per query (us-east-1 grid):** 0.091 gCO2e
- **Optimal deployment region:** europe-north1 (Lowest carbon intensity)

---

## 6. Cost Allocation & Chargeback Readiness (Mission 4 / FOCUS Standard)

- **Tag Coverage Achieved:** **92.0%** across `team` and `project` tags (clears the 80% threshold required for chargeback enforcement).
- **Cost Attribution by Engineering Team:**
  - `assistant`: $2.59 / day (30.5% of inference spend)
  - `search`: $2.49 / day (29.4% of inference spend)
  - `eval`: $1.79 / day (21.1% of inference spend)
  - `rag`: $1.60 / day (18.9% of inference spend)
- **Interoperability:** Multi-cloud cost logs exported to `outputs/focus_export.csv` under the **FinOps Open Cost & Usage Specification (FOCUS 1.x)**.

---

## 7. Extensions & Advanced Econometric Findings (Your Turn)

1. **Prompt Caching Economics (`cache_is_worth_it`):**
   - Theoretical break-even reuse threshold: $N_{\text{breakeven}} = \frac{\$3.00}{\$3.00 \times 0.90} = 1.11 \text{ reads}$.
   - Actual workload access frequency: $N_{\text{actual}} = 480.0 \text{ reads} \gg 1.11$, confirming caching delivers massive positive ROI.
2. **Reasoning Token Governance:**
   - Reasoning queries (`is_reasoning=1`) represent only **8.4% of requests** (201/2,400) and **16.5% of cost**, but consume **94.04% of total inference energy** (29,787.7 Wh) due to an 80x energy multiplier. Restricting reasoning via confidence-based semantic routing protects margins and power caps.
3. **Purchasing Preemption Matrix:**
   - Incorporating GPU-specific interruption risk (H100: 3%, A10G: 8%) into checkpoint simulations yields an audited net savings of **39.4% ($10,116/mo)**.

---
_Figures represent June-2026 audited baseline telemetry; re-baseline dynamically before operational deployment._