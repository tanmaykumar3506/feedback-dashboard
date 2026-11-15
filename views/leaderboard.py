"""Final mentor leaderboard (locked scoring)."""
import streamlit as st

import config as cfg
from src import reports, ui


def render(ctx):
    lb, lb_all = ctx["lb"], ctx["lb_all"]
    ui.page_header("Final Mentor Leaderboard", "Approved scoring: five questions, equal weight, mentor sections pooled")
    if ctx["filtered"]:
        ui.notice("Showing selected mentors only. Rank numbers are the locked ranks among all 8 mentors.", "info")

    low = lb[lb["low_response"]]
    if len(low):
        ui.notice("<b>Low-response warning:</b> " + ", ".join(f"{r.mentor} has only {r.responses} responses" for r in low.itertuples())
                  + f". Flagged because fewer than {cfg.LOW_RESPONSE_THRESHOLD} students answered; the score is provisional. This is an analytical threshold, not an assignment requirement.", "warn")

    ui.section("Leaderboard", "data", "Scores shown to 2 decimals; ranking uses the unrounded overall score.")
    t = reports.leaderboard_export(lb).copy()
    t["Low-response flag (<10)"] = t["Low-response flag (<10)"].replace({"Yes - provisional": "⚠ Low response"})
    t = t.rename(columns={"Low-response flag (<10)": "Flag"})

    def hl(row):
        return ["background-color:#FEF3C7" if row["Flag"] else "" for _ in row]

    fmt = {k: "{:.2f}" for k in cfg.QUESTIONS + ["Overall score"]}
    styled = t.style.apply(hl, axis=1).format(fmt).set_properties(subset=["Overall score"], **{"font-weight": "700"})
    ui.table(styled, hide_index=True, height=min(60 + 36 * len(t), 460))

    notes = []
    srt = lb_all.reset_index(drop=True)
    for a, b in zip(srt.itertuples(), srt.iloc[1:].itertuples()):
        if round(a.overall, 2) == round(b.overall, 2) and {a.mentor, b.mentor} <= set(lb["mentor"]):
            notes.append(f"{a.mentor} and {b.mentor} both display {a.overall:.2f}; {a.mentor} ranks higher on the unrounded score ({a.overall:.4f} vs {b.overall:.4f}).")
    for n in notes:
        ui.notice("<b>Displayed tie:</b> " + n, "info")

    d1, d2 = st.columns(2)
    d1.download_button("Download leaderboard (CSV)", reports.leaderboard_export(lb).to_csv(index=False).encode("utf-8"), "mentor_leaderboard.csv", "text/csv")
    d2.caption("More downloads, including a full Excel workbook, are on the Reports & Downloads page.")

    with st.expander("How the score is calculated"):
        st.markdown(
            "1. Each answer is converted to 1-5 (for example Very Good = 4, Excellent = 5).\n"
            "2. All of a mentor's responses are pooled across sections, so each response counts once.\n"
            "3. Each question's average is the mean of that question over the mentor's responses.\n"
            "4. Overall score = simple mean of the five question averages (equal weights).\n"
            "5. Rank = overall score at full precision; ties would be broken by Mentor-overall average, then number of responses (not needed in this data).")
