"""Extension 5: Carbon-aware Regional Scheduling Simulator.

Analyzes shifting interruptible training/batch workloads from dirty grids to clean grids.
"""
from __future__ import annotations
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from missions._common import load_csv, num, catalog_by_type
from finops import sustainability

DAYS = 30


def run_carbon_analysis(verbose: bool = True) -> dict:
    jobs = load_csv("workloads.csv")
    cat = catalog_by_type()

    # Filter interruptible jobs that can be scheduled flexibly
    interruptible_jobs = [j for j in jobs if bool(int(num(j["interruptible"])))]

    total_kwh_monthly = 0.0
    for j in interruptible_jobs:
        gtype = j["gpu_type"]
        ngpu = int(num(j["num_gpus"]))
        hpd = num(j["hours_per_day"])
        watts = num(cat[gtype]["watts"])
        # Total energy = watts * hours * num_gpus * 30 days
        kwh = (watts * hpd * ngpu * DAYS) / 1000.0
        total_kwh_monthly += kwh

    region_stats = {}
    for region, gco2_kwh in sustainability.REGION_CARBON.items():
        price_kwh = sustainability.REGION_PRICE_KWH.get(region, 0.12)
        co2_kg = (total_kwh_monthly * gco2_kwh) / 1000.0
        elec_cost = total_kwh_monthly * price_kwh
        region_stats[region] = {
            "gco2_per_kwh": gco2_kwh,
            "price_per_kwh": price_kwh,
            "monthly_kwh": round(total_kwh_monthly, 1),
            "monthly_co2_kg": round(co2_kg, 2),
            "monthly_elec_cost": round(elec_cost, 2),
        }

    baseline_region = "us-east-1"
    cleanest_region = min(region_stats, key=lambda r: region_stats[r]["gco2_per_kwh"])
    cheapest_elec_region = min(region_stats, key=lambda r: region_stats[r]["price_per_kwh"])

    co2_reduction_kg = region_stats[baseline_region]["monthly_co2_kg"] - region_stats[cleanest_region]["monthly_co2_kg"]
    co2_reduction_pct = (co2_reduction_kg / region_stats[baseline_region]["monthly_co2_kg"]) * 100.0

    if verbose:
        print("== Extension 5: Carbon-Aware Regional Scheduling ==")
        print(f"Flexible Workloads Total Energy: {total_kwh_monthly:,.1f} kWh/month\n")
        print(f"{'Region':18}{'gCO2/kWh':>10}{'$/kWh':>8}{'CO2 (kg/mo)':>14}{'Elec Cost':>12}")
        for r, s in sorted(region_stats.items(), key=lambda x: x[1]["gco2_per_kwh"]):
            print(f"{r:18}{s['gco2_per_kwh']:>10}{s['price_per_kwh']:>8.3f}${s['monthly_co2_kg']:>13,.1f}${s['monthly_elec_cost']:>11,.2f}")
        print(f"\nMoving flexible jobs from {baseline_region} -> {cleanest_region}:")
        print(f"  CO2 Savings: {co2_reduction_kg:,.1f} kg CO2e/month ({co2_reduction_pct:.1f}% reduction)")
        print(f"  Electricity Cost Delta: ${region_stats[cleanest_region]['monthly_elec_cost'] - region_stats[baseline_region]['monthly_elec_cost']:+,.2f}/month")

    return {
        "total_kwh_monthly": round(total_kwh_monthly, 1),
        "region_stats": region_stats,
        "cleanest_region": cleanest_region,
        "co2_reduction_kg": round(co2_reduction_kg, 2),
        "co2_reduction_pct": round(co2_reduction_pct, 1),
    }


if __name__ == "__main__":
    run_carbon_analysis()
