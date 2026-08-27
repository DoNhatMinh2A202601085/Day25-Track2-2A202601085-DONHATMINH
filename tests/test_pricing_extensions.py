"""Unit tests for Lab 25 FinOps Extensions (Your Turn)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from finops import pricing, sustainability
from missions.ext_carbon_scheduling import run_carbon_analysis


def test_cache_is_worth_it_breakeven():
    # Write cost = 3.0, Base price = 3.0, Read discount = 0.10 (90% off)
    # Savings per read = 3.0 * (1 - 0.10) = 2.70
    # Breakeven reads = 3.0 / 2.70 = 1.111...
    assert not pricing.cache_is_worth_it(avg_cache_reads=1.0, write_cost_per_m=3.0, read_discount=0.10, base_input_price_per_m=3.0)
    assert pricing.cache_is_worth_it(avg_cache_reads=1.2, write_cost_per_m=3.0, read_discount=0.10, base_input_price_per_m=3.0)
    assert pricing.cache_is_worth_it(avg_cache_reads=5.0, write_cost_per_m=3.0, read_discount=0.10, base_input_price_per_m=3.0)


def test_cache_is_worth_it_with_storage_cost():
    # With storage cost of $1.0/1M: total cost = 4.0 -> breakeven = 4.0 / 2.70 = 1.48 reads
    assert not pricing.cache_is_worth_it(avg_cache_reads=1.3, write_cost_per_m=3.0, read_discount=0.10, base_input_price_per_m=3.0, storage_cost_per_m=1.0)
    assert pricing.cache_is_worth_it(avg_cache_reads=1.5, write_cost_per_m=3.0, read_discount=0.10, base_input_price_per_m=3.0, storage_cost_per_m=1.0)


def test_recommend_tier_advanced_gpu_interruption():
    # H100 has low interruption risk (0.03) -> spot recommended for interruptible workloads
    assert pricing.recommend_tier(hours_per_day=20, interruptible=True, gpu_type="H100") == "spot"
    # Short duration (<7 days) non-interruptible low duty -> on_demand
    assert pricing.recommend_tier(hours_per_day=10, interruptible=False, gpu_type="H100", job_days=3) == "on_demand"
    # Long duration steady workload -> reserved
    assert pricing.recommend_tier(hours_per_day=24, interruptible=False, gpu_type="H100", job_days=365) == "reserved"


def test_carbon_aware_scheduling_simulation():
    res = run_carbon_analysis(verbose=False)
    assert res["total_kwh_monthly"] > 0
    assert res["cleanest_region"] == "europe-north1"
    assert res["co2_reduction_pct"] > 80.0
