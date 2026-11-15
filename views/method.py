"""Method and data notes: scales, verification facts, limits."""
import pandas as pd
import streamlit as st

import config as cfg
from src import ui


def render(ctx):
    ui.page_header("Method & Data Notes", "How the numbers were produced and what they can and cannot say")
    df = ctx["df_all"]
    ui.section("Data source", "data")
    st.markdown(
        f"- Original Excel export, **{len(df)} responses**, none removed or edited.\n"
        f"- {df['mentor'].nunique()} mentors in {df.groupby(['mentor', 'section']).ngroups} mentor-section groups; sections of the same mentor are pooled.\n"
        f"- Open-text answers: {int((df['improve_raw'] != '').sum())} in “improve” and {int((df['else_raw'] != '').sum())} in “anything else”; "
        f"{len(ctx['usable_ids'])} respondents wrote something with real content.\n"
        "- The email and name columns are empty or “anonymous” on every row; they are not read by this app.")

    ui.section("Score conversion (approved mapping)", "data")
    rows = []
    for k, (col, mp) in cfg.SCORED.items():
        rows.append({"Question": k, **{str(v): lab for lab, v in mp.items()}})
    ui.table(pd.DataFrame(rows)[["Question", "1", "2", "3", "4", "5"]], hide_index=True)
    st.caption("Syllabus pace and test-platform rating are not scored. Overall = equal-weight mean of the five question averages.")

    ui.section("Rounding", "data")
    st.markdown("- Scores are shown to 2 decimals; ranking uses the unrounded values.\n"
                "- Two question averages fall exactly on a rounding tie: Mentor D, Mentor overall = 4.125 and Mentor A, Mentor overall = 3.875. "
                "They are shown as 4.12 and 3.88 (round half to even), exactly as in the approved leaderboard. Neither affects any overall score or rank.")

    ui.section("Data versus interpretation", None)
    st.markdown(
        "- **Data:** scores, ranks, response counts, answer shares, exact quotes.\n"
        "- **Interpretation:** which theme a comment belongs to (manual coding), the feedback-tone groups, and suggested follow-ups.\n"
        "- The coding lives in `data/qualitative_coding.csv` (response Id and theme key, one row per pair), so anyone can audit or change it.")

    ui.section("Limits", "warn")
    st.markdown(
        f"- Fewer than {cfg.LOW_RESPONSE_THRESHOLD} responses is flagged as low-response. That threshold is an analytical choice, not an assignment requirement.\n"
        "- Response counts differ a lot between mentors (7 to 56), and the gaps between neighbouring mentors are small.\n"
        "- Comments were optional; no comment does not mean no issue. 3 pairs of identical-answer responses and 95 straight-liners exist in the file and were kept.\n"
        "- A comment is one student's view. Counts of 1 to 3 describe individual experiences, not patterns.")
