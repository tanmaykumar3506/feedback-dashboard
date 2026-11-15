"""Test platform: ratings, complaints and improvement suggestions."""
import altair as alt
import pandas as pd
import streamlit as st

import config as cfg
from src import charts, qualitative as q, scoring, ui

PROBLEM_KEYS = ["plat_lag", "plat_login", "plat_screen", "plat_noattempt", "plat_bugs", "plat_improve"]


def render(ctx):
    df, coding, tc = ctx["df"], ctx["coding"], ctx["tc"]
    ui.page_header("Test Platform", "Ratings, complaints and improvement suggestions about the online test platform (CodeFri)")
    g = ctx["groups"]
    prob_ids = q.ids_for(coding, cfg.PLATFORM_PROBLEM_KEYS) & ctx["ids"]
    needs = df[df["platform"] == "Needs Improvement"]
    ui.kpi_row([
        ("Mention the platform", g["platform_mention"], "in the open-text answers", "#2563EB"),
        ("Describe a problem", g["platform_problem"], "named a specific problem or asked for fixes", "#DC2626"),
        ("Could not complete a test", int(tc.set_index("theme_key").loc["plat_noattempt", "responses"]), "most serious reports", "#7C3AED"),
        ("Rated “Needs Improvement”", len(needs), f"{len(needs) / max(len(df), 1) * 100:.0f}% on the platform rating question", "#F59E0B"),
    ])
    st.write("")

    c1, c2 = st.columns(2, gap="large")
    with c1:
        ui.section("Platform rating (not part of score)", "data", "Answers to “How has your experience been with the Test Platform?”")
        d = scoring.answer_distribution(df, "platform", cfg.PLATFORM_ORDER)
        d["m"] = "All selected"
        ui.chart(charts.category_stack(d, "m", ["All selected"], cfg.PLATFORM_ORDER))
        dm = scoring.answer_distribution(df, "platform", cfg.PLATFORM_ORDER, by="mentor")
        ui.chart(charts.category_stack(dm, "mentor", ctx["lb"]["mentor"].tolist(), cfg.PLATFORM_ORDER))
    with c2:
        ui.section("What students complained about", "data", "Responses per problem type, each counted once per type. Types overlap.")
        keys = ["plat_lag", "plat_freeze", "plat_login", "plat_screen", "plat_noattempt", "plat_bugs", "plat_improve"]
        t = tc[tc["theme_key"].isin(keys)].copy()
        t = t[t["responses"] > 0]
        if t.empty:
            st.info("No platform complaints for the selected mentors.")
        else:
            ui.chart(charts.theme_bars(t))
        st.caption(f"Plus {int(tc.set_index('theme_key').loc['plat_vague', 'responses'])} answers such as “Browser” or “speed” that are too vague to classify, "
                   f"and {g['platform_mention'] - g['platform_problem']} that only name the platform.")

    ui.section("Does the rating match what students wrote?", "data")
    rated_needs_wrote = int(needs["response_id"].isin(prob_ids).sum())
    prob_df = df[df["response_id"].isin(prob_ids)]
    mix = prob_df["platform"].value_counts()
    st.markdown(
        f"- Of the **{len(needs)}** students who rated the platform “Needs Improvement”, **{rated_needs_wrote}** also described a problem in writing; the rest gave no written detail.\n"
        f"- Of the **{len(prob_df)}** students who described a problem in writing, "
        + ", ".join(f"**{int(v)}** rated it “{k}”" for k, v in mix.items()) + ".")

    ui.section("Problems by mentor group", "data", "Number of problem responses and share of that mentor's respondents. Small groups: read with care.")
    byg = prob_df.groupby("mentor").size().rename("problems")
    tab = ctx["lb"][["mentor", "responses"]].merge(byg, on="mentor", how="left").fillna({"problems": 0})
    tab["share"] = tab["problems"] / tab["responses"]
    ch = alt.Chart(tab).mark_bar(color=charts.RED).encode(
        y=alt.Y("mentor:N", sort="-x", title=None), x=alt.X("share:Q", axis=alt.Axis(format="%"), title="Share of the mentor's respondents describing a platform problem"),
        tooltip=["mentor", "problems", "responses", alt.Tooltip("share:Q", format=".0%")]).properties(height=max(160, 30 * len(tab)))
    ui.chart(ch)
    st.caption(f"Problems appear among students of {int((tab['problems'] > 0).sum())} of the {len(tab)} selected mentors, so this looks platform-wide rather than tied to one class.")

    ui.section("Student quotes on the platform", "data", "Exact words, spelling as typed.")
    shown = [(rid, qt, t) for t, rid, qt in cfg.QUOTES if t.startswith("plat_") and rid in ctx["ids"]]
    for _, qt, t in shown:
        ui.quote(qt, f"Student comment · {cfg.THEME_LABEL[t]}")

    ui.section("Improvement suggestions", "data", "What students asked for, from the comments.")
    asks = [("plat_improve", "Platform / interface improvement (no detail)"), ("plat_screen", "Fix screen sharing during tests"),
            ("plat_login", "Fix login and access problems"), ("plat_lag", "Reduce lag and hanging"), ("con_course", "Change course name from DAA to DSA on the platform")]
    for k, label in asks:
        n = int(tc.set_index("theme_key").loc[k, "responses"])
        if n:
            st.markdown(f"- {label}: **{n}** response(s)")
    ui.notice("<b>Interpretation - suggested follow-ups (not student statements):</b> ask the platform provider to investigate lag, login and screen-sharing failures and which laptops are affected; "
              "offer a re-attempt to students whose test could not be completed; correct the course name display.", "interp")
