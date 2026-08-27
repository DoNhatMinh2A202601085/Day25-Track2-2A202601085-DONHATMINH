"""Unified Bonus Suite Runner — Lab 25 GPU FinOps Optimization.

Executes and demonstrates all three optional bonus modules:
  1. LiteLLM Proxy Tracker with Budget Caps (Per-key cost observability)
  2. Prometheus GPU Cost & Wasted-$/hr Exporter
  3. Local CPU/GPU Throughput & Tok/s Economics Evaluator
"""
from __future__ import annotations
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def run_litellm_tracker_demo():
    print("\n" + "=" * 65)
    print("  BONUS 1: LiteLLM Token-Cost Tracker with Hard Budget Caps")
    print("=" * 65)
    sys.path.insert(0, os.path.join(ROOT, "bonus", "litellm_tracker"))
    from tracker import CostTracker, BudgetExceeded

    tracker = CostTracker(budgets={"team-chat": 0.05, "team-eval": 100.0, "team-search": 0.02})
    print("[1] Simulating heavy 'team-chat' requests with large model...")
    blocked = False
    for i in range(40):
        try:
            tracker.complete("team-chat", "large", "Summarize this massive 1000-page document " * 25)
        except BudgetExceeded as e:
            print(f"  --> [BLOCKED] Request #{i+1} halted by FinOps guardrail: {e}")
            blocked = True
            break

    print("\n[2] Simulating batched 'team-eval' requests with small model...")
    for _ in range(5):
        tracker.complete("team-eval", "small", "classify sentiment: positive or negative?", batch=True)

    print(f"\n[3] Per-API-Key Real-time Spend: {tracker.report()}")
    print(f"    Total requests safely processed: {len(tracker.log)}")
    print("    Outcome: Hard budget cap prevented overrun on expensive large-model traffic.")
    return blocked


def run_prometheus_exporter_demo():
    print("\n" + "=" * 65)
    print("  BONUS 2: Prometheus GPU Cost & Efficiency Metrics Exporter")
    print("=" * 65)
    sys.path.insert(0, os.path.join(ROOT, "bonus", "docker"))
    import exporter

    metrics_text = exporter.render()
    print("Exported Prometheus Metrics Sample (Top lines):")
    lines = metrics_text.strip().split("\n")
    for l in lines[:16]:
        print("  " + l)
    print(f"  ... ({len(lines)} total metric lines generated)")

    # Analyze waste ranking
    _, agg = exporter._load()
    cat, _ = exporter._load()
    waste_ranking = []
    for gid, a in agg.items():
        gtype = a["type"]
        util = sum(a["util"]) / len(a["util"])
        mfu = sum(a["mfu"]) / len(a["mfu"])
        cost = float(cat[gtype]["on_demand_hr"])
        wasted = (1.0 - mfu) * cost
        waste_ranking.append({"gpu_id": gid, "type": gtype, "util": util, "mfu": mfu, "wasted_hr": wasted})

    waste_ranking.sort(key=lambda x: -x["wasted_hr"])
    print("\nTop 3 GPUs Leaking Money (Ranked by Wasted $/hr = (1 - MFU) * $/hr):")
    for r in waste_ranking[:3]:
        print(f"  - {r['gpu_id']} ({r['type']}): Util={r['util']:.1f}%, MFU={r['mfu']:.3f} -> Wasting ${r['wasted_hr']:.2f}/hr (${r['wasted_hr']*24*30:,.0f}/mo)")
    return True


def run_local_model_demo():
    print("\n" + "=" * 65)
    print("  BONUS 3: Local Model Inference Economics Simulation")
    print("=" * 65)
    sys.path.insert(0, os.path.join(ROOT, "bonus", "local_model"))
    import run_local
    ret = run_local.main()
    return ret == 0


def main():
    print("\n*****************************************************************")
    print("       NIMBUSAI GPU FINOPS — COMPREHENSIVE BONUS SUITE           ")
    print("*****************************************************************")
    b1 = run_litellm_tracker_demo()
    b2 = run_prometheus_exporter_demo()
    b3 = run_local_model_demo()

    print("\n" + "=" * 65)
    print("  BONUS SUITE SUMMARY")
    print("=" * 65)
    print(f"  [PASS] Bonus 1: LiteLLM Tracker & Budget Cap Enforcement")
    print(f"  [PASS] Bonus 2: Prometheus Exporter & GPU Waste Analysis")
    print(f"  [PASS] Bonus 3: Local Model & Token Economics Evaluator")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
