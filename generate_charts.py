#!/usr/bin/env python3
"""
generate_charts.py

Connects to Supabase, fetches all quiz responses, then:
  - Generates 3 chart HTML files into charts/  (embedded as iframes in results.html)
  - Writes charts/population_data.json         (used by results.html for inline charts)

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

# Load credentials from .env file
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError(
        "SUPABASE_URL and SUPABASE_KEY must be set as environment variables or in a .env file."
    )

# Connect to Supabase and download all quiz responses into a table (df)
client = create_client(SUPABASE_URL, SUPABASE_KEY)
result = client.table("quiz_responses").select("*").execute()
df = pd.DataFrame(result.data)
print(f"Fetched {len(df)} rows from quiz_responses.")

# Create the charts/ output folder if it doesn't exist
os.makedirs("charts", exist_ok=True)

# Chart colors — match the site's green/teal theme
C_BASE    = "#3f6653"   # teal — used for most bars
C_CORRECT = "#2b694d"   # green — correct answer bar
C_WRONG   = "#c47a7a"   # red   — wrong answer bars
C_GRID    = "#e1e3e4"   # light grey grid lines


# ── Chart 1: Where do people get their climate news? ──────────────────────────
# Uses quiz question q1_news_source
if "q1_news_source" in df.columns and df["q1_news_source"].notna().any():

    # Count each answer and convert to percentages
    counts = df["q1_news_source"].dropna().value_counts()
    pct = (counts / counts.sum() * 100).round(1).sort_values()

    # Build a horizontal bar chart
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
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8f9fa",
        font=dict(family="Work Sans, sans-serif", color="#191c1d", size=13),
        margin=dict(l=60, r=100, t=80, b=60),
    )

    # Save as a standalone HTML file
    with open("charts/chart_news_source.html", "w", encoding="utf-8") as f:
        f.write(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))
    print("✓ chart_news_source.html")
else:
    print("⚠  Skipping chart_news_source.html — q1_news_source column empty or missing")


# ── Chart 2: Fact check — which climate statement is accurate? ────────────────
# Uses quiz question q9_fact_check. The correct answer is "Ocean Heat".
CORRECT_ANSWER = "Ocean Heat"

if "q9_fact_check" in df.columns and df["q9_fact_check"].notna().any():

    # Count each answer and convert to percentages
    counts = df["q9_fact_check"].dropna().value_counts()
    pct = (counts / counts.sum() * 100).round(1).sort_values()
    correct_pct = float(pct.get(CORRECT_ANSWER, 0.0))

    # Color correct answer green, wrong answers red
    colors = [C_CORRECT if ans == CORRECT_ANSWER else C_WRONG for ans in pct.index]
    # Add a checkmark next to the correct answer label
    texts = [f"{v}%  ✔" if ans == CORRECT_ANSWER else f"{v}%"
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
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8f9fa",
        font=dict(family="Work Sans, sans-serif", color="#191c1d", size=13),
        margin=dict(l=60, r=100, t=80, b=60),
    )

    with open("charts/chart_fact_check.html", "w", encoding="utf-8") as f:
        f.write(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))
    print("✓ chart_fact_check.html")
else:
    print("⚠  Skipping chart_fact_check.html — q9_fact_check column empty or missing")


# ── Chart 3: How do people experience climate news coverage? ──────────────────
# Uses quiz question q7_tone
if "q7_tone" in df.columns and df["q7_tone"].notna().any():

    # Count each answer and convert to percentages
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
        paper_bgcolor="#ffffff",
        plot_bgcolor="#f8f9fa",
        font=dict(family="Work Sans, sans-serif", color="#191c1d", size=13),
        margin=dict(l=60, r=100, t=80, b=60),
    )

    with open("charts/chart_tone_perception.html", "w", encoding="utf-8") as f:
        f.write(pio.to_html(fig, full_html=True, include_plotlyjs="cdn"))
    print("✓ chart_tone_perception.html")
else:
    print("⚠  Skipping chart_tone_perception.html — q7_tone column empty or missing")


# ── Build population_data.json ────────────────────────────────────────────────
# This JSON file is loaded by results.html to draw two inline charts:
#   - A scatter plot of media exposure vs. confidence calibration (one dot per respondent)
#   - A bar chart of average trust scores per media type

# Maps text answers to numbers for the scatter plot
EXPOSURE_MAP = {
    "Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Very often": 4,
}
CONFIDENCE_MAP = {
    "Not confident at all": 1, "Not very confident": 2, "Neutral": 3,
    "Somewhat confident": 4, "Very confident": 5,
}

# Build one scatter point per respondent
scatter_points = []
needed_cols = {"q3_climate_frequency", "q5_confidence", "q9_correct"}
if needed_cols.issubset(df.columns):
    rng = np.random.default_rng(seed=42)  # fixed seed so dots don't move on each run
    for _, row in df.iterrows():
        exp_raw  = row.get("q3_climate_frequency")
        conf_raw = row.get("q5_confidence")
        corr_raw = row.get("q9_correct")
        q1_val   = row.get("q1_news_source", "")

        # Skip rows with missing exposure or confidence data
        if pd.isna(exp_raw) or pd.isna(conf_raw):
            continue

        exposure   = EXPOSURE_MAP.get(str(exp_raw))
        confidence = CONFIDENCE_MAP.get(str(conf_raw))
        if exposure is None or confidence is None:
            continue

        # calibration_gap: how overconfident the respondent is
        # (high confidence but wrong answer = large gap)
        correct         = 1 if corr_raw is True else 0
        calibration_gap = confidence - (correct * 5)

        # Add a tiny random offset so overlapping dots are visible
        scatter_points.append({
            "exposure":        round(float(exposure)        + float(rng.uniform(-0.15, 0.15)), 3),
            "calibration_gap": round(float(calibration_gap) + float(rng.uniform(-0.15, 0.15)), 3),
            "q1": str(q1_val) if not pd.isna(q1_val) else "",
        })
    print(f"  {len(scatter_points)} scatter points computed")
else:
    missing = needed_cols - set(df.columns)
    print(f"⚠  Scatter points skipped — missing columns: {missing}")

# Calculate average trust score (1–5) for each media type
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
        trust_averages[key] = 3.0  # default to neutral if column is missing

# Calculate percentage breakdown for each answer option (used by results.html)
# Fact check percentages
if "q9_fact_check" in df.columns:
    col = df["q9_fact_check"].dropna()
    total = len(col)
    fact_check_stats = {str(k): round(float(v / total * 100), 1) for k, v in col.value_counts().items()}
else:
    fact_check_stats = {}

# News source percentages
if "q1_news_source" in df.columns:
    col = df["q1_news_source"].dropna()
    total = len(col)
    news_source_stats = {str(k): round(float(v / total * 100), 1) for k, v in col.value_counts().items()}
else:
    news_source_stats = {}

# Tone percentages
if "q7_tone" in df.columns:
    col = df["q7_tone"].dropna()
    total = len(col)
    tone_stats = {str(k): round(float(v / total * 100), 1) for k, v in col.value_counts().items()}
else:
    tone_stats = {}

# Bundle everything into one JSON file
population_data = {
    "scatter_points":    scatter_points,
    "trust_averages":    trust_averages,
    "fact_check_stats":  fact_check_stats,
    "news_source_stats": news_source_stats,
    "tone_stats":        tone_stats,
    "total_respondents": int(len(df)),
}

with open("charts/population_data.json", "w", encoding="utf-8") as f:
    json.dump(population_data, f, indent=2, ensure_ascii=False)
print("population_data.json")

print(f"\nDone. {len(df)} respondents in dataset.")