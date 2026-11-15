"""Question-wise visualisation, plus the two non-scored questions as context."""
import streamlit as st

import config as cfg
from src import charts, scoring, ui


def render(ctx):
    df, lb = ctx["df"], ctx["lb"]
    ui.page_header("Question-wise Scores", "The five scored questions, equally weighted, and two unscored context questions")

    qm = scoring.question_means(df)
    ui.section("Average score per question", "data", "All selected responses pooled; scale 1-5.")
    cols = st.columns(len(cfg.QUESTIONS))
    for c, r in zip(cols, qm.itertuples()):
        c.metric(r.question, f"{r.average:.2f}")
    import altair as alt
    d = qm.copy()
    d["disp"] = charts.two_dp(d["average"])
    ch = alt.Chart(d).mark_bar(color=charts.BLUE).encode(
        y=alt.Y("question:N", sort="-x", title=None), x=alt.X("average:Q", scale=alt.Scale(domain=[0, 5]), title="Average score (axis 0-5)"),
        tooltip=["question", alt.Tooltip("disp:N", title="Average")])
    txt = alt.Chart(d).mark_text(align="left", dx=4).encode(y=alt.Y("question:N", sort="-x"), x="average:Q", text="disp:N")
    ui.chart((ch + txt).properties(height=220))

    ui.section("Score mix per question", "data")
    ui.chart(charts.stacked_scores(scoring.score_distribution(df), "question", cfg.QUESTIONS))

    ui.section("Best and lowest mentor on each question", "data", "Among the selected mentors; low-response mentors are marked.")
    for k in cfg.QUESTIONS:
        hi, lo = lb.loc[lb[k].idxmax()], lb.loc[lb[k].idxmin()]
        mark = lambda r: " ⚠" if r["low_response"] else ""
        st.markdown(f"- **{k}:** highest {hi['mentor']}{mark(hi)} ({hi[k]:.2f}), lowest {lo['mentor']}{mark(lo)} ({lo[k]:.2f})")

    st.divider()
    ui.section("Context questions (not part of the score)", "data", "These two questions are shown for information only and are excluded from every score.")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("**Syllabus pace**")
        d1 = scoring.answer_distribution(df, "syllabus", cfg.SYLLABUS_ORDER)
        d1["m"] = "All selected"
        ui.chart(_pace(d1))
    with c2:
        st.markdown("**Test platform rating**")
        d2 = scoring.answer_distribution(df, "platform", cfg.PLATFORM_ORDER)
        d2["m"] = "All selected"
        ui.chart(charts.category_stack(d2, "m", ["All selected"], cfg.PLATFORM_ORDER))


def _pace(d):
    import altair as alt
    colors = {"Too Slow": "#B91C1C", "Slightly Slow": "#F59E0B", "Just Right": "#16A34A", "Slightly Fast": "#F59E0B", "Too Fast": "#B91C1C"}
    return alt.Chart(d).mark_bar().encode(
        y=alt.Y("m:N", title=None), x=alt.X("share:Q", stack="normalize", axis=alt.Axis(format="%"), title="Share of responses"),
        color=alt.Color("answer:N", title=None, sort=cfg.SYLLABUS_ORDER, scale=alt.Scale(domain=cfg.SYLLABUS_ORDER, range=[colors[k] for k in cfg.SYLLABUS_ORDER]),
                        legend=alt.Legend(orient="bottom")),
        order=alt.Order("order:Q"), tooltip=["answer", "responses", alt.Tooltip("share:Q", format=".0%")]).properties(height=110 + charts.LEG)
