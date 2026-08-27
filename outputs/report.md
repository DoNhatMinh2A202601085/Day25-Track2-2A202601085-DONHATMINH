# NimbusAI — GPU Cost Optimization Report

**Period:** monthly  
**Baseline spend:** $27,133  
**Optimized spend:** $14,550  
**Projected savings:** $12,583  (**46%**)

## Savings by lever

| Lever | Savings (USD) | Share of Savings (%) |
|---|---|---|
| Inference (cascade/cache/batch) | $1,212 | 9.6% |
| Purchasing (spot/reserved) | $10,116 | 80.4% |
| Right-size util-lies | $655 | 5.2% |
| Kill idle GPUs | $600 | 4.8% |

## Sustainability

- Energy per query: 0.24 Wh
- Carbon per query (us-east-1): 0.091 gCO2e
- Cheapest+cleanest region: europe-north1

## Strategic Action Items (Priority Order)

1. **Purchasing Migration (Immediate ROI):** Shift interruptible training to Spot instances with automated checkpointing; reserve 3-year commitments for steady-state 24/7 inference workloads.
2. **Inference Pipeline Modernization:** Enforce cascade routing to small models, prompt prefix caching for recurring context, and asynchronous batching for offline tasks.
3. **Fleet Right-Sizing & Idle Governance:** Demote memory-bound decode instances (e.g. H100 -> A100/L4) to eliminate 'GPU-Util lies' and enforce aggressive idle-shutdown timeouts (<15 min).

_Figures are June-2026 as-of snapshots; re-baseline before acting._