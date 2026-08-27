"""Report assembly — the lab's deliverable: baseline vs optimized + savings chart."""
from __future__ import annotations


def build_report(baseline_usd: float, optimized_usd: float, levers: dict,
                 sustainability: dict | None = None, period: str = "monthly") -> str:
    """Return a markdown cost-optimization report."""
    savings = baseline_usd - optimized_usd
    pct = (savings / baseline_usd * 100.0) if baseline_usd > 0 else 0.0
    lines = [
        "# NimbusAI — GPU Cost Optimization Report",
        "",
        f"**Period:** {period}  ",
        f"**Baseline spend:** ${baseline_usd:,.0f}  ",
        f"**Optimized spend:** ${optimized_usd:,.0f}  ",
        f"**Projected savings:** ${savings:,.0f}  (**{pct:.0f}%**)",
        "",
        "## Savings by lever",
        "",
        "| Lever | Savings (USD) | Share of Savings (%) |",
        "|---|---|---|",
    ]
    total_savings = sum(levers.values()) if sum(levers.values()) > 0 else 1.0
    for name, amount in levers.items():
        share = (amount / total_savings) * 100.0
        lines.append(f"| {name} | ${amount:,.0f} | {share:.1f}% |")

    if sustainability:
        lines += [
            "",
            "## Sustainability",
            "",
            f"- Energy per query: {sustainability.get('wh_per_query', 0):.2f} Wh",
            f"- Carbon per query (us-east-1): {sustainability.get('carbon_g', 0):.3f} gCO2e",
            f"- Cheapest+cleanest region: {sustainability.get('best_region', 'n/a')}",
        ]

    lines += [
        "",
        "## Strategic Action Items (Priority Order)",
        "",
        "1. **Purchasing Migration (Immediate ROI):** Shift interruptible training to Spot instances with automated checkpointing; reserve 3-year commitments for steady-state 24/7 inference workloads.",
        "2. **Inference Pipeline Modernization:** Enforce cascade routing to small models, prompt prefix caching for recurring context, and asynchronous batching for offline tasks.",
        "3. **Fleet Right-Sizing & Idle Governance:** Demote memory-bound decode instances (e.g. H100 -> A100/L4) to eliminate 'GPU-Util lies' and enforce aggressive idle-shutdown timeouts (<15 min).",
        "",
        "_Figures are June-2026 as-of snapshots; re-baseline before acting._",
    ]
    return "\n".join(lines)


def savings_waterfall(levers: dict, path: str) -> str:
    """Write a high-quality savings bar chart PNG. Returns the path."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return ""
    names = list(levers.keys())
    vals = [levers[n] for n in names]
    
    # Modern color palette for levers
    colors = ["#2563eb", "#059669", "#d97706", "#dc2626"]
    
    fig, ax = plt.subplots(figsize=(9, 5), dpi=120)
    bars = ax.bar(names, vals, color=colors[:len(names)], edgecolor="#1e293b", linewidth=1.2, alpha=0.9)
    
    # Value annotations on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"${height:,.0f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),  # 4 points vertical offset
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold", color="#1e293b")
                    
    ax.set_ylabel("Monthly Savings (USD)", fontsize=11, fontweight="bold")
    ax.set_title("NimbusAI: GPU Cost Savings by FinOps Lever ($/month)", fontsize=13, fontweight="bold", pad=15)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.set_ylim(0, max(vals) * 1.18)
    plt.xticks(rotation=15, ha="right", fontsize=10, fontweight="bold")
    plt.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path
