"""Mentor-wise performance comparison charts."""
import pandas as pd
import streamlit as st

import config as cfg
from src import charts, scoring, ui


def render(ctx):
    lb, df = ctx["lb"], ctx["df"]
    ui.page_header("Mentor Comparison", "Compare mentors on the five scored questions")
    low = lb[lb["low_response"]]
    if len(low):
        ui.notice("<b>Low-response warning:</b> " + ", ".join(f"{r.mentor} (n={r.responses})" for r in low.itertuples())
                  + " - amber marks mean fewer than 10 responses; compare with care.", "warn")
    if len(lb) < 2:
        st.info("Select two or more mentors in the sidebar to compare them.")

    qs = st.multiselect("Questions to include", cfg.QUESTIONS, default=cfg.QUESTIONS, key="cmp_q")
    qs = qs or cfg.QUESTIONS
    t1, t2, t3, t4, t5 = st.tabs(["Overall", "Heatmap", "By question", "Score mix", "Sample size"])

    avg = float(scoring.question_means(df)["average"].mean())
    with t1:
        ui.section("Overall score", "data", "Dots are mentors; labels show n. Axis does not start at zero because all scores sit between 3.5 and 4.6.")
        ui.chart(charts.overall_dots(lb, avg))
    with t2:
        ui.section("Question averages by mentor", "data", "Darker = higher average. Rows follow the locked rank order.")
        ui.chart(charts.heatmap(lb, qs))
    with t3:
        ui.section("Each question, all mentors", "data")
        ui.chart(charts.question_dots(lb, qs))
    with t4:
        ui.section("How each mentor's students answered", "data", "Share of responses at each score for one question.")
        q1 = st.selectbox("Question", qs, key="mix_q")
        dist = scoring.score_distribution(df, by="mentor")
        dist = dist[dist["question"] == q1]
        order = [m for m in lb["mentor"] if m in set(dist["mentor"])]
        ui.chart(charts.stacked_scores(dist, "mentor", order))
    with t5:
        ui.section("Responses per mentor", "data", f"Dashed line = {cfg.LOW_RESPONSE_THRESHOLD}-response threshold (analytical, not an assignment rule).")
        ui.chart(charts.response_counts(lb))
        sec = scoring.section_table(df)
        st.caption("Sections pooled: " + "; ".join(f"{m}: " + " + ".join(f"{r.responses} ({r.section})" for r in g.itertuples()) for m, g in sec.groupby("mentor")))

    st.divider()
    ui.section("Mentor profile: gap to the all-response average", "data", "Positive = above the average of all selected responses on that question.")
    m = st.selectbox("Mentor", lb["mentor"].tolist(), key="profile_m")
    row = lb[lb["mentor"] == m].iloc[0]
    base = scoring.question_means(df).set_index("question")["average"]
    gap = pd.DataFrame({"question": qs, "gap": [row[k] - base[k] for k in qs]})
    gap["disp"] = gap["gap"].map(lambda v: f"{v:+.2f}")
    import altair as alt
    ch = alt.Chart(gap).mark_bar().encode(
        y=alt.Y("question:N", sort=qs, title=None), x=alt.X("gap:Q", title="Difference from the all-response average (points)"),
        color=alt.condition(alt.datum.gap >= 0, alt.value(charts.BLUE), alt.value(charts.RED)),
        tooltip=["question", alt.Tooltip("disp:N", title="Gap")]).properties(height=40 * len(qs) + 40)
    ui.chart(ch)
    st.caption(f"{m}: rank {int(row['rank'])} of 8, overall {row['overall']:.2f}, {int(row['responses'])} responses."
               + (" Low-response: read with caution." if row["low_response"] else ""))
