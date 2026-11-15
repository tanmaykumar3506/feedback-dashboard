"""Approved scoring methodology (locked).

* Each of the five questions is mapped to 1-5 (see config.SCORED).
* A mentor's sections are pooled: every response of that mentor counts once, whatever the section.
* Question average = mean of that question over all the mentor's responses.
* Overall = simple mean of the five question averages (equal weighting).
* Rank = overall score at full precision (display rounded to 2 decimals); tie-break: mentor-overall, then responses.
"""
from __future__ import annotations

import pandas as pd

import config as cfg


def mentor_table(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("mentor")
    t = g[cfg.QUESTIONS].mean()
    t.insert(0, "responses", g.size())
    t["overall"] = t[cfg.QUESTIONS].mean(axis=1)
    t = t.sort_values(["overall", "Mentor overall", "responses"], ascending=False)
    t.insert(0, "rank", range(1, len(t) + 1))
    t["low_response"] = t["responses"] < cfg.LOW_RESPONSE_THRESHOLD
    return t.reset_index()


def question_means(df: pd.DataFrame) -> pd.DataFrame:
    s = df[cfg.QUESTIONS].mean()
    return pd.DataFrame({"question": s.index, "average": s.values})


def score_distribution(df: pd.DataFrame, by: str | None = None) -> pd.DataFrame:
    """Long table: [by,] question, score, responses, share (share is within each group+question)."""
    long = df.melt(id_vars=["mentor"], value_vars=cfg.QUESTIONS, var_name="question", value_name="score")
    keys = ([by] if by else []) + ["question", "score"]
    d = long.groupby(keys).size().rename("responses").reset_index()
    grp = ([by] if by else []) + ["question"]
    d["share"] = d["responses"] / d.groupby(grp)["responses"].transform("sum")
    return d


def section_table(df: pd.DataFrame) -> pd.DataFrame:
    """Section-level response counts, only to show how sections were pooled."""
    return df.groupby(["mentor", "section"]).size().rename("responses").reset_index()


def answer_distribution(df: pd.DataFrame, col: str, order: list[str], by: str | None = None) -> pd.DataFrame:
    """Share of each answer option (used for the NON-scored syllabus and platform questions)."""
    keys = ([by] if by else []) + [col]
    d = df.groupby(keys).size().rename("responses").reset_index().rename(columns={col: "answer"})
    grp = [by] if by else []
    d["share"] = d["responses"] / (d.groupby(grp)["responses"].transform("sum") if grp else d["responses"].sum())
    d["order"] = d["answer"].map({a: i for i, a in enumerate(order)})
    return d
