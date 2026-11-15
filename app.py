"""Student Feedback Analysis Dashboard - Streamlit entry point.

Run with:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

import config as cfg
from src import data_loader, qualitative as q, scoring, ui
from views import comparison, leaderboard, method, overview, platform, questions, reports, themes

st.set_page_config(page_title="Student Feedback Dashboard", page_icon=":material/insights:", layout="wide")
ui.inject_css()


@st.cache_data(show_spinner=False)
def load():
    df = data_loader.load_responses()
    coding = q.load_coding(df)
    return df, coding, q.load_usable_ids()


df_all, coding, usable_ids = load()
lb_all = scoring.mentor_table(df_all)            # locked scoring and ranks, always across all mentors
ALL_MENTORS = lb_all.sort_values("mentor")["mentor"].tolist()

PAGES = {
    "Overview": overview,
    "Mentor Leaderboard": leaderboard,
    "Mentor Comparison": comparison,
    "Question Scores": questions,
    "Feedback Themes": themes,
    "Test Platform": platform,
    "Reports & Downloads": reports,
    "Method & Data Notes": method,
}

# Filter widgets get a versioned key. "Reset filters" bumps the version, which recreates both widgets with their
# defaults; changing the value of a still-focused multiselect in a callback is not reliable in the browser.
st.session_state.setdefault("filter_ver", 0)


def _reset():
    st.session_state["filter_ver"] += 1


ver = st.session_state["filter_ver"]
KEY_M, KEY_C = f"sel_mentors_{ver}", f"sel_cats_{ver}"


with st.sidebar:
    st.markdown("### Student Feedback Dashboard")
    st.caption("Operations Intern Assignment 2 - Problem 2")
    page = st.radio("Navigate", list(PAGES), label_visibility="collapsed", key="nav")
    st.divider()
    st.markdown("**Filters**")
    st.multiselect("Mentors", ALL_MENTORS, default=ALL_MENTORS, key=KEY_M, help="Scores and counts are recalculated for the selected mentors. Ranks stay the locked ranks across all 8 mentors.")
    st.multiselect("Feedback categories", cfg.CATEGORIES, default=cfg.CATEGORIES, key=KEY_C, help="Applies to the qualitative themes, comment browser and exports.")
    st.button("Reset filters", on_click=_reset)
    st.divider()
    st.caption("Source: original Excel export, 238 responses. Scores are the approved, locked methodology.")

sel = st.session_state[KEY_M] or ALL_MENTORS
cats = st.session_state[KEY_C] or cfg.CATEGORIES
df = df_all[df_all["mentor"].isin(sel)].reset_index(drop=True)
ids = set(df["response_id"])
n_usable = len(ids & usable_ids)
lb = lb_all[lb_all["mentor"].isin(sel)].reset_index(drop=True)
tc = q.theme_counts(coding, ids, len(df), n_usable)

ctx = {
    "df_all": df_all, "df": df, "coding": coding, "usable_ids": usable_ids,
    "lb_all": lb_all, "lb": lb, "sel": sel, "cats": cats, "ids": ids, "n_usable": n_usable,
    "tc": tc, "tc_cat": tc[tc["category"].isin(cats)], "groups": q.group_sizes(coding, ids),
    "filtered": len(sel) < len(ALL_MENTORS),
    "filter_text": f"Mentors: {', '.join(sel) if len(sel) < len(ALL_MENTORS) else 'all 8'}; categories: {', '.join(cats) if len(cats) < len(cfg.CATEGORIES) else 'all'}",
}
if not st.session_state[KEY_M]:
    st.sidebar.warning("No mentor selected: showing all mentors.")

PAGES[page].render(ctx)
