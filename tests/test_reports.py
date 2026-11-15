"""Exports: correct content, honour filters, contain no staff names."""
import io

import openpyxl
import pandas as pd

import config as cfg
from src import data_loader, qualitative as q, reports, scoring


def _build(mentors=None):
    df = data_loader.load_responses()
    coding = q.load_coding(df)
    lb = scoring.mentor_table(df)
    if mentors:
        lb = lb[lb["mentor"].isin(mentors)]
        df = df[df["mentor"].isin(mentors)]
    ids = set(df["response_id"])
    tc = q.theme_counts(coding, ids, len(df), len(ids & q.load_usable_ids()))
    ct = q.comment_table(df, coding)
    ct = ct[ct["response_id"].isin(ids)]
    sheets = {"Leaderboard": reports.leaderboard_export(lb), "Theme counts": reports.theme_export(tc[tc["responses"] > 0]),
              "Coded comments": reports.comments_export(ct), "Notes": reports.notes_frame("test")}
    return reports.build_excel(sheets), sheets


def test_excel_has_four_sheets_and_locked_values():
    blob, _ = _build()
    wb = openpyxl.load_workbook(io.BytesIO(blob))
    assert wb.sheetnames == ["Leaderboard", "Theme counts", "Coded comments", "Notes"]
    rows = list(wb["Leaderboard"].iter_rows(values_only=True))
    assert rows[0][:3] == ("Rank", "Mentor", "Responses") and len(rows) == 9
    assert rows[1][1] == "Mentor E" and rows[1][-2] == 4.41
    assert rows[2][-1].startswith("Yes")                                    # Mentor H flagged


def test_filtered_export_keeps_locked_rank_and_only_selected_comments():
    _, s = _build(["Mentor A", "Mentor E"])
    assert s["Leaderboard"]["Rank"].tolist() == [1, 8]
    assert set(s["Coded comments"]["Mentor"]) <= {"Mentor A", "Mentor E"}


def test_export_has_no_staff_names_or_withheld_text():
    blob, s = _build()
    text = " ".join(s["Coded comments"].astype(str).stack().tolist()).lower()
    assert not any(n in text for n in cfg.REDACT_NAMES) and "goodies" not in text
