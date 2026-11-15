"""Sentiment (tone) and qualitative themes from the two open-text questions."""
import pandas as pd
import streamlit as st

import config as cfg
from src import charts, qualitative as q, ui


def render(ctx):
    df, coding, tc = ctx["df"], ctx["coding"], ctx["tc"]
    ui.page_header("Feedback Themes & Sentiment", "What students wrote in the two open-text questions")
    n, nu, g = len(df), ctx["n_usable"], ctx["groups"]
    ui.kpi_row([
        ("Respondents", n, "in this view", "#2563EB"),
        ("Usable comments", nu, f"{nu / max(n, 1) * 100:.0f}% wrote real content", "#7C3AED"),
        ("Positive", g["positive"], "praise or general satisfaction", "#16A34A"),
        ("Suggestions", g["suggestion"], "practice or teaching-method ideas", "#2563EB"),
        ("Platform problems", g["platform_problem"], "test-platform issues described", "#DC2626"),
    ])
    st.write("")
    ui.notice("Each response is counted <b>once per theme</b>, even if the student repeats the point in both boxes. A response can sit in several different themes, "
              "so theme counts overlap and must not be added together. Percentages are shares of respondents in this view.", "info")

    ui.section("Feedback tone", "interp", "Each respondent is placed in one group from the themes coded for their comments. This is an analyst classification, not a sentiment model.")
    tone = q.feedback_tone(df, coding, ctx["usable_ids"])
    ui.chart(charts.tone_bar(tone, q.TONE_ORDER))

    ui.section("Themes", "interp", "Manual coding by reading every comment. Counts are data once the coding is accepted; the grouping into themes is judgement.")
    tcc = ctx["tc_cat"]
    tcc = tcc[tcc["responses"] > 0]
    if tcc.empty:
        st.info("No themes for the current mentor and category filters.")
    else:
        ui.chart(charts.theme_bars(tcc))
    if ctx["filtered"]:
        ui.notice("<b>Caution:</b> with a mentor filter the counts are small. One comment is not evidence about a mentor.", "warn")

    st.divider()
    ui.section("Student quotes", "data", "Exact words, spelling as typed. Staff names removed. Quotes are examples, not a count.")
    avail = [(k, cfg.THEME_LABEL[k]) for k in dict.fromkeys(t for t, _, _ in cfg.QUOTES) if cfg.THEME_CAT[k] in ctx["cats"]]
    if avail:
        label = st.selectbox("Theme", [l for _, l in avail], key="quote_theme")
        key = next(k for k, l in avail if l == label)
        shown = [(rid, qt) for t, rid, qt in cfg.QUOTES if t == key and rid in ctx["ids"]]
        if not shown:
            st.caption("No quote for this theme among the selected mentors.")
        for _, qt in shown:
            ui.quote(qt, f"Student comment · {label}")

    with st.expander("Browse all coded comments"):
        ct = q.comment_table(df, coding)
        ct = ct[ct["category"].isin(ctx["cats"]) & ct["response_id"].isin(ctx["ids"])]
        themes_sel = st.multiselect("Theme", sorted(ct["theme"].unique()), key="browse_theme")
        if themes_sel:
            ct = ct[ct["theme"].isin(themes_sel)]
        st.caption(f"{ct['response_id'].nunique()} responses, {len(ct)} response-theme rows.")
        ui.table(ct[["response_id", "mentor", "category", "theme", "improve_text", "else_text"]].rename(
            columns={"response_id": "Id", "mentor": "Mentor", "category": "Category", "theme": "Theme", "improve_text": "Improve-area answer", "else_text": "Anything-else answer"}),
            hide_index=True, height=380)
