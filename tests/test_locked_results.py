"""Guards the approved numbers: the dashboard must reproduce the locked leaderboard and report counts exactly."""
import pandas as pd
import pytest

import config as cfg
from src import data_loader, qualitative as q, scoring

# Locked leaderboard: mentor -> (responses, five averages, overall) rounded to 2 dp
LOCKED = {
    "Mentor E": (1, 30, [4.43, 4.30, 4.60, 4.23, 4.47], 4.41),
    "Mentor H": (2, 7, [4.29, 4.00, 4.00, 4.29, 4.00], 4.11),
    "Mentor B": (3, 50, [4.16, 3.92, 4.16, 4.14, 4.10], 4.10),
    "Mentor F": (4, 19, [3.95, 3.89, 4.11, 3.84, 4.11], 3.98),
    "Mentor C": (5, 33, [4.00, 3.76, 4.09, 3.91, 4.00], 3.95),
    "Mentor G": (6, 11, [4.00, 3.82, 4.09, 3.82, 3.82], 3.91),
    "Mentor D": (7, 32, [3.91, 3.69, 4.12, 3.97, 3.84], 3.91),
    "Mentor A": (8, 56, [3.82, 3.66, 3.88, 3.73, 3.77], 3.77),
}


@pytest.fixture(scope="module")
def df():
    return data_loader.load_responses()


@pytest.fixture(scope="module")
def coding(df):
    return q.load_coding(df)


def test_all_238_responses_kept(df):
    assert len(df) == 238 and df["response_id"].is_unique


def test_five_questions_present_and_in_range(df):
    assert cfg.QUESTIONS == ["Satisfaction", "Clarity", "Mentor overall", "Engagement", "Class quality"]
    assert df[cfg.QUESTIONS].isna().sum().sum() == 0
    assert df[cfg.QUESTIONS].stack().between(1, 5).all()


def test_sections_are_pooled_per_mentor(df):
    lb = scoring.mentor_table(df)
    assert len(lb) == 8 and lb["responses"].sum() == 238
    assert df.groupby(["mentor", "section"]).ngroups == 11          # 11 mentor-section groups -> 8 mentors


def test_leaderboard_matches_locked(df):
    lb = scoring.mentor_table(df).set_index("mentor")
    for mentor, (rank, n, avgs, overall) in LOCKED.items():
        r = lb.loc[mentor]
        assert int(r["rank"]) == rank, mentor
        assert int(r["responses"]) == n, mentor
        assert [round(float(r[k]), 2) for k in cfg.QUESTIONS] == avgs, mentor
        assert round(float(r["overall"]), 2) == overall, mentor


def test_equal_weighting_and_unrounded_ranking(df):
    lb = scoring.mentor_table(df)
    assert (lb["overall"] - lb[cfg.QUESTIONS].mean(axis=1)).abs().max() < 1e-12
    assert lb["overall"].is_monotonic_decreasing
    g, d = lb.set_index("mentor").loc["Mentor G", "overall"], lb.set_index("mentor").loc["Mentor D", "overall"]
    assert round(g, 2) == round(d, 2) == 3.91 and g > d             # displayed tie, unrounded order G > D


def test_low_response_flag_is_only_mentor_h(df):
    lb = scoring.mentor_table(df)
    assert lb.loc[lb["low_response"], "mentor"].tolist() == ["Mentor H"]


# ------------------------------------------------------------ qualitative (must equal Section 8 of the report)
def test_comment_volume(df):
    assert int((df["improve_raw"] != "").sum()) == 213 and int((df["else_raw"] != "").sum()) == 210
    assert len(q.load_usable_ids()) == 141


def test_no_duplicate_response_theme_pairs():
    raw = pd.read_csv(cfg.CODING_PATH)
    assert not raw.duplicated(["response_id", "theme_key"]).any()


def test_theme_counts_match_report(df, coding):
    ids = set(df["response_id"])
    tc = q.theme_counts(coding, ids, 238, 141).set_index("theme_key")["responses"].to_dict()
    expect = {"pos_praise": 13, "pos_general": 45, "pos_problem_solving": 3, "pos_platform": 2,
              "sug_practice": 15, "sug_examformat": 4, "sug_explain": 4, "sug_examples": 4, "sug_engage": 3,
              "sug_basics": 2, "sug_notes": 2, "sug_discipline": 2, "sug_doubt": 1, "sug_audio": 1,
              "plat_mention": 33, "plat_lag": 6, "plat_freeze": 3, "plat_login": 4, "plat_screen": 3,
              "plat_noattempt": 4, "plat_bugs": 6, "plat_improve": 4, "plat_vague": 9,
              "con_cipher": 2, "con_faculty": 1, "con_boring": 1, "con_prize": 1, "con_course": 1,
              "ctx_neo": 9, "ctx_topic_only": 9}
    assert tc == expect


def test_group_totals_match_report(df, coding):
    g = q.group_sizes(coding, set(df["response_id"]))
    assert g["positive"] == 58 and g["suggestion"] == 32 and g["teaching"] == 18 and g["practice"] == 15
    assert g["platform_mention"] == 33 and g["platform_problem"] == 23
    tone = q.feedback_tone(df, coding, q.load_usable_ids())
    assert len(tone) == 238
    assert (tone["tone"] == "Positive, with a suggestion or problem").sum() == 13


def test_platform_problems_span_seven_mentors(df, coding):
    ids = q.ids_for(coding, cfg.PLATFORM_PROBLEM_KEYS)
    assert df[df["response_id"].isin(ids)]["mentor"].nunique() == 7


# ------------------------------------------------------------ privacy and quotes
def test_every_quote_is_verbatim_and_names_redacted(df):
    by_id = df.set_index("response_id")
    for theme, rid, quote in cfg.QUOTES:
        text = by_id.loc[rid, "improve_text"] + " || " + by_id.loc[rid, "else_text"]
        assert quote in text, (rid, quote)
        assert theme in cfg.THEMES
    everything = (by_id["improve_text"] + " " + by_id["else_text"]).str.lower().str.cat(sep=" ")
    assert not any(n in everything for n in cfg.REDACT_NAMES)
    assert "syngnry" not in everything and "goodies" not in everything


def test_chart_labels_use_same_rounding_as_leaderboard(df):
    """Vega's formatter would show Mentor D 'Mentor overall' (exactly 4.125) as 4.13; charts must show the locked 4.12."""
    from src import charts
    lb = scoring.mentor_table(df)
    spec = charts.heatmap(lb, cfg.QUESTIONS).to_dict()
    rows = [r for ds in spec["datasets"].values() for r in ds]
    d = next(r for r in rows if r["mentor"] == "Mentor D" and r["question"] == "Mentor overall")
    a = next(r for r in rows if r["mentor"] == "Mentor A" and r["question"] == "Mentor overall")
    assert d["disp"] == "4.12" and a["disp"] == "3.88"
