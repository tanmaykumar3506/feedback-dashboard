"""Excel / CSV report builders. Exports follow the sidebar filters; ranks always stay the locked all-mentor ranks."""
from __future__ import annotations

import io

import pandas as pd

import config as cfg


def leaderboard_export(lb: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame({"Rank": lb["rank"], "Mentor": lb["mentor"], "Responses": lb["responses"]})
    for k in cfg.QUESTIONS:
        out[k] = lb[k].round(2)
    out["Overall score"] = lb["overall"].round(2)
    out["Low-response flag (<10)"] = lb["low_response"].map({True: "Yes - provisional", False: ""})
    return out


def theme_export(tc: pd.DataFrame) -> pd.DataFrame:
    return tc.rename(columns={"theme": "Theme", "category": "Category", "responses": "Responses (counted once per theme)",
                              "pct_all": "% of all respondents", "pct_usable": "% of respondents with a usable comment"}
                     ).drop(columns="theme_key").round({"% of all respondents": 1, "% of respondents with a usable comment": 1})


def comments_export(ct: pd.DataFrame) -> pd.DataFrame:
    return ct.rename(columns={"response_id": "Response Id", "mentor": "Mentor", "category": "Category", "theme": "Theme",
                              "improve_text": "Improve-area answer (redacted)", "else_text": "Anything-else answer (redacted)"}
                     )[["Response Id", "Mentor", "Category", "Theme", "Improve-area answer (redacted)", "Anything-else answer (redacted)"]]


def notes_frame(filter_text: str) -> pd.DataFrame:
    rows = [
        ("Source", "Original Excel export of student feedback; all 238 responses used, none removed."),
        ("Scoring", "Each of five questions mapped to 1-5; mentor sections pooled; overall = equal-weight mean of the five question averages."),
        ("Ranking", "Rank by unrounded overall score (2-decimal display). Ranks are always the locked ranks across all 8 mentors."),
        ("Low-response flag", f"Mentors with fewer than {cfg.LOW_RESPONSE_THRESHOLD} responses are flagged. This is an analytical threshold, not an assignment requirement."),
        ("Qualitative themes", "Manual coding of the two open-text questions by response Id. A response is counted at most once per theme; themes overlap, so do not add them."),
        ("Interpretation", "Feedback tone and suggested actions are interpretations; scores, counts and quotes are data."),
        ("Privacy", "Staff names replaced by [mentor]; one comment with identifying detail is withheld."),
        ("Filters applied", filter_text),
    ]
    return pd.DataFrame(rows, columns=["Topic", "Note"])


def build_excel(sheets: dict[str, pd.DataFrame]) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter") as xw:
        wb = xw.book
        head = wb.add_format({"bold": True, "bg_color": "#0F172A", "font_color": "#FFFFFF", "border": 1, "text_wrap": True, "valign": "top"})
        wrap = wb.add_format({"text_wrap": True, "valign": "top"})
        for name, df in sheets.items():
            df.to_excel(xw, sheet_name=name, index=False)
            ws = xw.sheets[name]
            for j, col in enumerate(df.columns):
                ws.write(0, j, col, head)
                width = min(70, max(10, int(df[col].astype(str).str.len().quantile(0.9)) + 2, len(col) + 2)) if len(df) else len(col) + 2
                ws.set_column(j, j, width, wrap if width >= 40 else None)
            ws.freeze_panes(1, 0)
    return buf.getvalue()
