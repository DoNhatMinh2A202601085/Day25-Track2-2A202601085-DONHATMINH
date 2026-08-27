"""Unit tests for Lab 25 Bonus Modules."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bonus", "litellm_tracker"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bonus", "docker"))

from tracker import CostTracker, BudgetExceeded
import exporter


def test_litellm_tracker_budget_cap():
    tracker = CostTracker(budgets={"team-test": 0.002})
    # Small request should pass
    res1 = tracker.complete("team-test", "small", "Hello world")
    assert res1["cost"] > 0
    # Over-budget request should raise BudgetExceeded
    exceeded = False
    for _ in range(10):
        try:
            tracker.complete("team-test", "large", "Very long prompt text here " * 50)
        except BudgetExceeded:
            exceeded = True
            break
    assert exceeded, "Should have raised BudgetExceeded when cap is hit"


def test_prometheus_cost_exporter_render():
    metrics = exporter.render()
    assert "gpu_util_pct" in metrics
    assert "gpu_mfu" in metrics
    assert "gpu_wasted_cost_usd_per_hr" in metrics
    assert "gpu-h100-4" in metrics
