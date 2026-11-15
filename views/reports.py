"""Downloadable reports (Excel / CSV). Exports follow the sidebar filters."""
import streamlit as st

from src import qualitative as q, reports, ui


def render(ctx):
    ui.page_header("Reports & Downloads", "Excel and CSV exports of what you see, following the sidebar filters")
    st.caption(f"Current filters - {ctx['filter_text']}")

    lb_x = reports.leaderboard_export(ctx["lb"])
    tcx = ctx["tc_cat"]
    tc_x = reports.theme_export(tcx[tcx["responses"] > 0])
    ct = q.comment_table(ctx["df"], ctx["coding"])
    ct = ct[ct["category"].isin(ctx["cats"]) & ct["response_id"].isin(ctx["ids"])]
    cm_x = reports.comments_export(ct)
    notes = reports.notes_frame(ctx["filter_text"])

    excel = reports.build_excel({"Leaderboard": lb_x, "Theme counts": tc_x, "Coded comments": cm_x, "Notes": notes})
    st.download_button("Download full report (Excel, 4 sheets)", excel, "student_feedback_report.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
    st.write("")
    c1, c2, c3 = st.columns(3)
    c1.download_button("Leaderboard (CSV)", lb_x.to_csv(index=False).encode("utf-8"), "mentor_leaderboard.csv", "text/csv")
    c2.download_button("Theme counts (CSV)", tc_x.to_csv(index=False).encode("utf-8"), "theme_counts.csv", "text/csv")
    c3.download_button("Coded comments (CSV)", cm_x.to_csv(index=False).encode("utf-8"), "coded_comments.csv", "text/csv")

    with st.expander("Preview: leaderboard"):
        ui.table(lb_x, hide_index=True)
    with st.expander("Preview: theme counts"):
        ui.table(tc_x, hide_index=True)
    with st.expander("Preview: coded comments"):
        ui.table(cm_x, hide_index=True, height=300)
    ui.notice("Exports contain scores, counts and redacted comments only. Staff names are replaced by [mentor] and one comment with identifying detail is withheld.", "info")
