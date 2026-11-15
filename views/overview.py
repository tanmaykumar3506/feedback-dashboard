"""Overview: headline numbers, low-response warning, overall scores and rating mix."""
import streamlit as st

import config as cfg
from src import charts, scoring, ui


def render(ctx):
    df, lb, df_all = ctx["df"], ctx["lb"], ctx["df_all"]
    n_m = df["mentor"].nunique()
    ui.page_header("Student Feedback Overview", f"Semester feedback on mentors and classes - {len(df)} responses across {n_m} mentor{'s' if n_m != 1 else ''}")
    if ctx["filtered"]:
        ui.notice(f"Filtered view: {len(ctx['sel'])} of 8 mentors, {len(df)} of {len(df_all)} responses. Ranks shown elsewhere remain the locked ranks across all mentors.", "info")

    qm = scoring.question_means(df)
    avg = float(qm["average"].mean())
    low = lb[lb["low_response"]]
    ui.kpi_row([
        ("Total responses", len(df), f"of {len(df_all)} in the file", "#2563EB"),
        ("Mentors", len(lb), f"{df.groupby(['mentor', 'section']).ngroups} mentor-section groups pooled", "#0EA5E9"),
        ("All-response average", f"{avg:.2f}", "mean of 5 question averages", "#16A34A"),
        ("Usable comments", ctx["n_usable"], f"{ctx['n_usable'] / max(len(df), 1) * 100:.0f}% of respondents wrote real content", "#7C3AED"),
        ("Platform problems", ctx["groups"]["platform_problem"], "responses describing a test-platform issue", "#DC2626"),
        ("Low-response mentors", len(low), f"fewer than {cfg.LOW_RESPONSE_THRESHOLD} responses", "#F59E0B"),
    ])
    st.write("")

    if len(low):
        names = ", ".join(f"{r.mentor} (n={r.responses})" for r in low.itertuples())
        ui.notice(f"<b>Low-response warning:</b> {names}. Scores for these mentors are provisional because very few students answered. "
                  f"The {cfg.LOW_RESPONSE_THRESHOLD}-response limit is an analytical threshold chosen for this analysis, not an assignment requirement.", "warn")

    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        ui.section("Overall score by mentor", "data", "Mean of the five question averages. Dashed line = all-response average.")
        ui.chart(charts.overall_dots(lb, avg))
    with c2:
        ui.section("How students rated the five questions", "data", "Share of answers at each score, all selected responses pooled.")
        dist = scoring.score_distribution(df)
        ui.chart(charts.stacked_scores(dist, "question", cfg.QUESTIONS))

    ui.section("Headline facts")
    top, bottom = lb.iloc[0], lb.iloc[-1]
    items = [
        f"Highest overall score in this view: **{top['mentor']}** at **{top['overall']:.2f}** ({int(top['responses'])} responses).",
        f"Lowest overall score in this view: **{bottom['mentor']}** at **{bottom['overall']:.2f}** ({int(bottom['responses'])} responses). The spread between first and last is {top['overall'] - bottom['overall']:.2f} points on a 1-5 scale.",
        f"Highest-rated question overall: **{qm.loc[qm['average'].idxmax(), 'question']}** ({qm['average'].max():.2f}); lowest: **{qm.loc[qm['average'].idxmin(), 'question']}** ({qm['average'].min():.2f}).",
        f"{ctx['groups']['positive']} respondents gave positive comments, {ctx['groups']['suggestion']} made improvement suggestions and {ctx['groups']['platform_problem']} described test-platform problems (themes overlap).",
    ]
    for t in items:
        st.markdown(f"- {t}")
    ui.notice("<b>Interpretation:</b> the gaps between neighbouring mentors are small and the number of responses differs a lot (7 to 56). "
              "Treat the ranking as a summary of this survey, not as a final judgement of any mentor.", "interp")

    with st.expander("How to read this dashboard"):
        st.markdown(
            "- <span class='badge data'>Data</span> numbers computed directly from the original Excel file: scores, response counts, rating shares, quotes.\n"
            "- <span class='badge interp'>Interpretation</span> classifications and suggestions made by the analyst, for example the manual theme coding, the feedback tone and suggested actions.\n"
            "- <span class='badge warn'>Caution</span> limits of the data, such as small samples.", unsafe_allow_html=True)
