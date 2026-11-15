"""Altair chart builders. One palette: blue for data, amber for low-response, a 5-step scale for score distributions."""
from __future__ import annotations

import altair as alt
import pandas as pd

import config as cfg

BLUE, AMBER, GREY, RED = "#2563EB", "#F59E0B", "#94A3B8", "#DC2626"
SCORE_COLORS = {1: "#B91C1C", 2: "#F59E0B", 3: "#CBD5E1", 4: "#60A5FA", 5: "#1D4ED8"}
CAT_COLORS = {cfg.CAT_POS: "#16A34A", cfg.CAT_SUG: BLUE, cfg.CAT_PLAT: "#DC2626", cfg.CAT_CON: "#7C3AED", cfg.CAT_CTX: GREY}


COUNT_AXIS = alt.Axis(tickMinStep=1, format="d")   # whole numbers only on count axes
LEG = 100   # Streamlit fits the chart (axis + bottom legend included) into `height`, so reserve room for the legend


def two_dp(series: pd.Series) -> pd.Series:
    """Format to 2 dp in Python (round-half-even, same as the approved leaderboard). Vega's own formatter would show 4.125 as 4.13."""
    return series.map(lambda v: f"{v:.2f}")


def _pad(lo: float, hi: float, pad: float = 0.15) -> list[float]:
    return [max(1.0, lo - pad), min(5.0, hi + pad)]


def overall_dots(lb: pd.DataFrame, class_avg: float) -> alt.Chart:
    d = lb.copy()
    d["label"] = d["mentor"] + "  (n=" + d["responses"].astype(str) + ")"
    d["status"] = d["low_response"].map({True: f"Low response (<{cfg.LOW_RESPONSE_THRESHOLD})", False: "Adequate responses"})
    d["disp"] = two_dp(d["overall"])
    order = d["label"].tolist()
    scale = alt.Scale(domain=_pad(d["overall"].min(), max(d["overall"].max(), class_avg)))
    base = alt.Chart(d).encode(y=alt.Y("label:N", sort=order, title=None))
    rule = base.mark_rule(color="#CBD5E1").encode(x=alt.X("overall:Q", scale=scale, title="Overall score (1-5, axis does not start at zero)"), x2=alt.value(0))
    pts = base.mark_circle(size=230).encode(
        x=alt.X("overall:Q", scale=scale),
        color=alt.Color("status:N", title=None, scale=alt.Scale(domain=[f"Adequate responses", f"Low response (<{cfg.LOW_RESPONSE_THRESHOLD})"], range=[BLUE, AMBER]),
                        legend=alt.Legend(orient="bottom")),
        tooltip=["mentor", alt.Tooltip("disp:N", title="Overall"), "responses", "rank"])
    txt = base.mark_text(align="left", dx=12, fontSize=12, fontWeight="bold").encode(x="overall:Q", text="disp:N")
    avg = alt.Chart(pd.DataFrame({"v": [class_avg]})).mark_rule(strokeDash=[5, 4], color="#64748B").encode(x=alt.X("v:Q", scale=scale))
    return (rule + pts + txt + avg).properties(height=max(220, 38 * len(d)) + LEG)


def heatmap(lb: pd.DataFrame, questions: list[str]) -> alt.Chart:
    d = lb.melt(id_vars=["mentor", "rank", "responses"], value_vars=questions, var_name="question", value_name="avg")
    d["disp"] = two_dp(d["avg"])
    order = lb["mentor"].tolist()
    lo, hi = float(d["avg"].min()), float(d["avg"].max())
    base = alt.Chart(d).encode(x=alt.X("question:N", sort=questions, title=None, axis=alt.Axis(labelAngle=0)),
                               y=alt.Y("mentor:N", sort=order, title=None))
    rect = base.mark_rect(stroke="white", strokeWidth=2).encode(
        color=alt.Color("avg:Q", title="Average", scale=alt.Scale(domain=[lo, hi], range=["#DBEAFE", "#1E3A8A"]), legend=alt.Legend(orient="bottom")),
        tooltip=["mentor", "question", alt.Tooltip("disp:N", title="Average"), "responses"])
    txt = base.mark_text(fontSize=13, fontWeight="bold").encode(
        text="disp:N",
        color=alt.condition(alt.datum.avg > (lo + hi) / 2, alt.value("white"), alt.value("#0F172A")))
    return (rect + txt).properties(height=max(200, 44 * len(order)) + LEG)


def question_dots(lb: pd.DataFrame, questions: list[str]) -> alt.Chart:
    d = lb.melt(id_vars=["mentor", "responses"], value_vars=questions, var_name="question", value_name="avg")
    d["disp"] = two_dp(d["avg"])
    scale = alt.Scale(domain=_pad(d["avg"].min(), d["avg"].max(), 0.1))
    return alt.Chart(d).mark_circle(size=140).encode(
        x=alt.X("avg:Q", scale=scale, title="Average score (axis does not start at zero)"),
        y=alt.Y("question:N", sort=questions, title=None),
        color=alt.Color("mentor:N", title=None, legend=alt.Legend(orient="bottom")),
        tooltip=["mentor", "question", alt.Tooltip("disp:N", title="Average"), "responses"]).properties(height=60 * len(questions) + 40 + LEG + 40)


def stacked_scores(dist: pd.DataFrame, y: str, y_order: list[str], row: str | None = None) -> alt.Chart:
    d = dist.copy()
    d["score"] = d["score"].astype(int)
    d["pct"] = d["share"]
    ch = alt.Chart(d).mark_bar().encode(
        y=alt.Y(f"{y}:N", sort=y_order, title=None),
        x=alt.X("pct:Q", stack="normalize", title="Share of responses", axis=alt.Axis(format="%")),
        color=alt.Color("score:O", title="Score (1=lowest, 5=highest)",
                        scale=alt.Scale(domain=[1, 2, 3, 4, 5], range=[SCORE_COLORS[i] for i in range(1, 6)]), legend=alt.Legend(orient="bottom")),
        order=alt.Order("score:O"),
        tooltip=[y, "score", "responses", alt.Tooltip("share:Q", format=".0%")])
    return ch.properties(height=max(120, 36 * len(y_order)) + LEG)


def response_counts(lb: pd.DataFrame) -> alt.Chart:
    d = lb.copy()
    d["status"] = d["low_response"].map({True: "Low response", False: "Adequate"})
    base = alt.Chart(d).encode(y=alt.Y("mentor:N", sort="-x", title=None))
    bars = base.mark_bar().encode(x=alt.X("responses:Q", title="Responses", axis=COUNT_AXIS),
                                  color=alt.Color("status:N", title=None, scale=alt.Scale(domain=["Adequate", "Low response"], range=[BLUE, AMBER]), legend=alt.Legend(orient="bottom")),
                                  tooltip=["mentor", "responses"])
    txt = base.mark_text(align="left", dx=4).encode(x="responses:Q", text="responses:Q")
    thr = alt.Chart(pd.DataFrame({"t": [cfg.LOW_RESPONSE_THRESHOLD]})).mark_rule(strokeDash=[5, 4], color="#64748B").encode(x="t:Q")
    return (bars + txt + thr).properties(height=max(200, 34 * len(d)) + LEG)


def theme_bars(tc: pd.DataFrame, value: str = "responses", height: int | None = None) -> alt.Chart:
    d = tc.sort_values(value, ascending=False)
    order = d["theme"].tolist()
    multi = d["category"].nunique() > 1
    base = alt.Chart(d).encode(y=alt.Y("theme:N", sort=order, title=None, axis=alt.Axis(labelLimit=330)))
    bars = base.mark_bar().encode(
        x=alt.X(f"{value}:Q", title="Responses (once per theme)", axis=COUNT_AXIS),
        color=alt.Color("category:N", title=None, scale=alt.Scale(domain=list(CAT_COLORS), range=list(CAT_COLORS.values())),
                        legend=alt.Legend(orient="bottom") if multi else None),
        tooltip=["theme", "category", "responses", alt.Tooltip("pct_all:Q", format=".1f", title="% of all respondents")])
    txt = base.mark_text(align="left", dx=4).encode(x=f"{value}:Q", text=f"{value}:Q")
    return (bars + txt).properties(height=(height or max(160, 28 * len(d))) + (LEG if multi else 60))


def tone_bar(tone: pd.DataFrame, order: list[str]) -> alt.Chart:
    d = tone.groupby("tone").size().rename("responses").reset_index()
    colors = {"Positive only": "#16A34A", "Positive, with a suggestion or problem": "#86EFAC", "Suggestion / problem, no positive remark": "#F59E0B",
              "Other comment (neutral or too vague)": "#CBD5E1", "No usable comment": "#E2E8F0"}
    base = alt.Chart(d).encode(y=alt.Y("tone:N", sort=order, title=None, axis=alt.Axis(labelLimit=330)))
    bars = base.mark_bar().encode(x=alt.X("responses:Q", title="Respondents", axis=COUNT_AXIS),
                                  color=alt.Color("tone:N", legend=None, scale=alt.Scale(domain=list(colors), range=list(colors.values()))),
                                  tooltip=["tone", "responses"])
    txt = base.mark_text(align="left", dx=4).encode(x="responses:Q", text="responses:Q")
    return (bars + txt).properties(height=210)


def category_stack(d: pd.DataFrame, y: str, order: list[str], order_x: list[str]) -> alt.Chart:
    colors = {"Excellent": "#1D4ED8", "Good": "#60A5FA", "Needs Improvement": "#DC2626", "Haven’t used it enough yet": "#CBD5E1"}
    return alt.Chart(d).mark_bar().encode(
        y=alt.Y(f"{y}:N", sort=order, title=None),
        x=alt.X("share:Q", stack="normalize", title="Share of responses", axis=alt.Axis(format="%")),
        color=alt.Color("answer:N", title=None, sort=order_x, scale=alt.Scale(domain=order_x, range=[colors[k] for k in order_x]), legend=alt.Legend(orient="bottom")),
        order=alt.Order("order:Q"),
        tooltip=[y, "answer", "responses", alt.Tooltip("share:Q", format=".0%")]).properties(height=max(120, 36 * len(order)) + LEG)
