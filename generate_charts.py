#!/usr/bin/env python3
"""
generate_charts.py

Connects to Supabase, fetches all quiz_responses rows, then:
  - Generates 3 standalone chart HTML files into charts/  (used as iframes)
  - Writes charts/population_data.json                    (used by results.html inline charts)

Run locally (needs .env with SUPABASE_URL and SUPABASE_KEY) or via GitHub Actions.
"""

import os
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError(
        "SUPABASE_URL and SUPABASE_KEY must be set as environment variables or in a .env file."
    )

client = create_client(SUPABASE_URL, SUPABASE_KEY)
result = client.table("quiz_responses").select("*").execute()
df = pd.DataFrame(result.data)
print(f"Fetched {len(df)} rows from quiz_responses.")

os.makedirs("charts", exist_ok=True)

# ── Colour palette (matches site's dark navy/teal theme) ──────────────────────
C_BASE   = "#3f6653"   # muted teal  — population bars / dots
C_CORRECT = "#2b694d"  # secondary green — correct answer
C_WRONG  = "#c47a7a"   # muted red       — wrong answers
C_PAPER  = "#ffffff"
C_BG     = "#f8f9fa"
C_TEXT   = "#191c1d"
C_GRID   = "#e1e3e4"

BASE_LAYOUT = dict(
    paper_bgcolor=C_PAPER,
    plot_bgcolor=C_BG,
    font=dict(family="Work Sans, sans-serif", color=C_TEXT, size=13),
    margin=dict(l=60, r=100, t=80, b=60),
)


def _pct_stats(series: pd.Series) -> dict:
    """Return {value: percentage} dict for a categorical series."""
    series = series.dropna()
    total = len(series)
    if total == 0:
        return {}
    return {str(k): round(float(v / total * 100), 1) for k, v in series.value_counts().items()}


# ── Chart 3 — News Source Distribution ────────────────────────────────────────
if "q1_news_source" in df.columns and df["q1_news_source"].notna().any():
    counts = df["q1_news_source"].dropna().value_counts()
    pct = (counts / counts.sum() * 100).round(1).sort_values()

    fig = go.Figure(go.Bar(
        x=pct.values,
        y=pct.index,
        orientation="h",
        marker_color=C_BASE,
        text=[f"{v}%" for v in pct.values],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="Where do people get their climate news?", x=0),
        xaxis=dict(
            title="% of respondents",
            showgrid=True, gridcolor=C_GRID,
            range=[0, pct.max() * 1.3],
        ),
        yaxis=dict(showgrid=False),
        **BASE_LAYOUT,
    )
    with open("charts/chart_news_source.html", "w", encoding="utf-8") as f:
        f.write(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))
    print("✓ chart_news_source.html")
else:
    print("⚠  Skipping chart_news_source.html — q1_news_source column empty or missing")


# ── Chart 4 — The Fact Check ──────────────────────────────────────────────────
CORRECT_ANSWER = "Ocean Heat"

if "q9_fact_check" in df.columns and df["q9_fact_check"].notna().any():
    counts = df["q9_fact_check"].dropna().value_counts()
    pct = (counts / counts.sum() * 100).round(1).sort_values()
    correct_pct = float(pct.get(CORRECT_ANSWER, 0.0))

    colors = [C_CORRECT if ans == CORRECT_ANSWER else C_WRONG for ans in pct.index]
    texts  = [f"{v}%  ✔" if ans == CORRECT_ANSWER else f"{v}%"
              for ans, v in zip(pct.index, pct.values)]

    fig = go.Figure(go.Bar(
        x=pct.values,
        y=pct.index,
        orientation="h",
        marker_color=colors,
        text=texts,
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(
            text=(
                "Which climate statement did people identify as accurate?"
                f"<br><sup>{correct_pct:.0f}% of respondents answered correctly</sup>"
            ),
            x=0,
        ),
        xaxis=dict(
            title="% of respondents",
            showgrid=True, gridcolor=C_GRID,
            range=[0, pct.max() * 1.35],
        ),
        yaxis=dict(showgrid=False),
        **BASE_LAYOUT,
    )
    with open("charts/chart_fact_check.html", "w", encoding="utf-8") as f:
        f.write(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))
    print("✓ chart_fact_check.html")
else:
    print("⚠  Skipping chart_fact_check.html — q9_fact_check column empty or missing")


# ── Chart 5 — Perceived Tone ──────────────────────────────────────────────────
if "q7_tone" in df.columns and df["q7_tone"].notna().any():
    counts = df["q7_tone"].dropna().value_counts()
    pct = (counts / counts.sum() * 100).round(1).sort_values()

    fig = go.Figure(go.Bar(
        x=pct.values,
        y=pct.index,
        orientation="h",
        marker_color=C_BASE,
        text=[f"{v}%" for v in pct.values],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="How do people experience climate news coverage?", x=0),
        xaxis=dict(
            title="% of respondents",
            showgrid=True, gridcolor=C_GRID,
            range=[0, pct.max() * 1.3],
        ),
        yaxis=dict(showgrid=False),
        **BASE_LAYOUT,
    )
    with open("charts/chart_tone_perception.html", "w", encoding="utf-8") as f:
        f.write(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))
    print("✓ chart_tone_perception.html")
else:
    print("⚠  Skipping chart_tone_perception.html — q7_tone column empty or missing (new column)")


# ── population_data.json — feeds inline Charts 1 & 2 in results.html ─────────
EXPOSURE_MAP = {
    "Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Very often": 4,
}
CONFIDENCE_MAP = {
    "Not confident at all": 1, "Not very confident": 2, "Neutral": 3,
    "Somewhat confident": 4, "Very confident": 5,
}

# Scatter points (Chart 1)
scatter_points = []
needed_cols = {"q3_climate_frequency", "q5_confidence", "q9_correct"}
if needed_cols.issubset(df.columns):
    rng = np.random.default_rng(seed=42)  # fixed seed → deterministic jitter
    for _, row in df.iterrows():
        exp_raw  = row.get("q3_climate_frequency")
        conf_raw = row.get("q5_confidence")
        corr_raw = row.get("q9_correct")
        q1_val   = row.get("q1_news_source", "")

        if pd.isna(exp_raw) or pd.isna(conf_raw):
            continue

        exposure   = EXPOSURE_MAP.get(str(exp_raw))
        confidence = CONFIDENCE_MAP.get(str(conf_raw))
        if exposure is None or confidence is None:
            continue

        correct         = 1 if corr_raw is True else 0
        calibration_gap = confidence - (correct * 5)

        scatter_points.append({
            "exposure":        round(float(exposure)        + float(rng.uniform(-0.15, 0.15)), 3),
            "calibration_gap": round(float(calibration_gap) + float(rng.uniform(-0.15, 0.15)), 3),
            "q1": str(q1_val) if not pd.isna(q1_val) else "",
        })
    print(f"  {len(scatter_points)} scatter points computed")
else:
    missing = needed_cols - set(df.columns)
    print(f"⚠  Scatter points skipped — missing columns: {missing}")

# Trust averages (Chart 2)
TRUST_COLS = {
    "newspapers": "q4_trust_newspapers",
    "talkshows":  "q4_trust_talkshows",
    "radio":      "q4_trust_radio",
    "podcasts":   "q4_trust_podcasts",
    "social":     "q4_trust_social",
    "friends":    "q4_trust_friends",
    "onlinenews": "q4_trust_onlinenews",
    "academic":   "q4_trust_academic",
}
trust_averages = {}
for key, col in TRUST_COLS.items():
    if col in df.columns:
        vals = df[col].dropna().astype(float)
        trust_averages[key] = round(float(vals.mean()), 2) if len(vals) > 0 else 3.0
    else:
        trust_averages[key] = 3.0

population_data = {
    "scatter_points":    scatter_points,
    "trust_averages":    trust_averages,
    "fact_check_stats":  _pct_stats(df["q9_fact_check"])  if "q9_fact_check"  in df.columns else {},
    "news_source_stats": _pct_stats(df["q1_news_source"]) if "q1_news_source" in df.columns else {},
    "tone_stats":        _pct_stats(df["q7_tone"])        if "q7_tone"        in df.columns else {},
    "total_respondents": int(len(df)),
}

with open("charts/population_data.json", "w", encoding="utf-8") as f:
    json.dump(population_data, f, indent=2, ensure_ascii=False)
print("✓ population_data.json")

print(f"\nDone. {len(df)} respondents in dataset.")
