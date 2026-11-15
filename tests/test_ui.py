"""Headless UI tests: every page renders, filters work, shown numbers equal the locked ones."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")

PAGES = ["Overview", "Mentor Leaderboard", "Mentor Comparison", "Question Scores", "Feedback Themes",
         "Test Platform", "Reports & Downloads", "Method & Data Notes"]


def run(page="Overview", mentors=None, cats=None):
    at = AppTest.from_file(APP, default_timeout=90)
    at.run()
    at.sidebar.radio(key="nav").set_value(page)
    if mentors is not None:
        at.sidebar.multiselect[0].set_value(mentors)
    if cats is not None:
        at.sidebar.multiselect[1].set_value(cats)
    return at.run()


def text(at):
    return " ".join([m.value for m in at.markdown] + [c.value for c in at.caption] + [m.value for m in at.metric])


@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders(page):
    at = run(page)
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders_with_mentor_filter(page):
    at = run(page, mentors=["Mentor H"])
    assert not at.exception, [e.value for e in at.exception]


@pytest.mark.parametrize("page", ["Feedback Themes", "Reports & Downloads"])
def test_category_filter(page):
    at = run(page, cats=["Test platform"])
    assert not at.exception, [e.value for e in at.exception]


def test_overview_numbers_and_low_response_warning():
    t = text(run("Overview"))
    assert ">238<" in t and "of 238 in the file" in t
    assert "Low-response warning" in t and "Mentor H (n=7)" in t
    assert "Mentor E" in t and "4.41" in t


def test_leaderboard_values_shown():
    at = run("Mentor Leaderboard")
    df = at.dataframe[0].value
    assert list(df["Mentor"]) == ["Mentor E", "Mentor H", "Mentor B", "Mentor F", "Mentor C", "Mentor G", "Mentor D", "Mentor A"]
    assert [round(x, 2) for x in df["Overall score"]] == [4.41, 4.11, 4.10, 3.98, 3.95, 3.91, 3.91, 3.77]
    assert "Displayed tie" in text(at)


def test_filter_keeps_locked_rank():
    at = run("Mentor Leaderboard", mentors=["Mentor A", "Mentor E"])
    df = at.dataframe[0].value
    assert list(df["Mentor"]) == ["Mentor E", "Mentor A"] and list(df["Rank"]) == [1, 8]


def test_themes_page_counts():
    t = text(run("Feedback Themes"))
    assert "once per theme" in t


def test_platform_page_counts():
    t = text(run("Test Platform"))
    assert ">33<" in t and ">23<" in t and "38" in t


def test_empty_mentor_selection_falls_back_to_all():
    at = run("Overview", mentors=[])
    assert not at.exception and ">238<" in text(at)


def test_reset_filters_button_restores_everything():
    at = run("Overview", mentors=["Mentor H"], cats=["Test platform"])
    assert at.sidebar.multiselect[0].value == ["Mentor H"]
    at.sidebar.button[0].click().run()
    assert len(at.sidebar.multiselect[0].value) == 8 and len(at.sidebar.multiselect[1].value) == 5
    assert "Filtered view" not in text(at) and not at.exception


def test_tie_notice_only_when_both_mentors_in_view():
    assert "Displayed tie" in text(run("Mentor Leaderboard"))
    assert "Displayed tie" not in text(run("Mentor Leaderboard", mentors=["Mentor H"]))
    assert "Displayed tie" in text(run("Mentor Leaderboard", mentors=["Mentor G", "Mentor D"]))


def test_overview_subtitle_follows_filter():
    assert "238 responses across 8 mentors" in text(run("Overview"))
    assert "7 responses across 1 mentor" in text(run("Overview", mentors=["Mentor H"]))
