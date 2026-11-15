"""Qualitative layer: manual theme coding by response Id (one row per response and theme, so no double counting)."""
from __future__ import annotations

import pandas as pd

import config as cfg


def load_coding(responses: pd.DataFrame) -> pd.DataFrame:
    c = pd.read_csv(cfg.CODING_PATH)
    unknown = sorted(set(c["theme_key"]) - set(cfg.THEMES))
    if unknown:
        raise ValueError(f"Unknown theme keys in coding file: {unknown}")
    stray = sorted(set(c["response_id"]) - set(responses["response_id"]))
    if stray:
        raise ValueError(f"Coding refers to response Ids not in the Excel file: {stray}")
    return c.drop_duplicates(["response_id", "theme_key"]).reset_index(drop=True)   # one count per response per theme


def load_usable_ids() -> set[int]:
    return set(pd.read_csv(cfg.USABLE_PATH)["response_id"])


def ids_for(coding: pd.DataFrame, keys: list[str]) -> set[int]:
    return set(coding.loc[coding["theme_key"].isin(keys), "response_id"])


def theme_counts(coding: pd.DataFrame, ids: set[int], n_total: int, n_usable: int) -> pd.DataFrame:
    sub = coding[coding["response_id"].isin(ids)]
    n = sub.groupby("theme_key")["response_id"].nunique()
    rows = []
    for key, (label, cat) in cfg.THEMES.items():
        k = int(n.get(key, 0))
        rows.append({"theme_key": key, "theme": label, "category": cat, "responses": k,
                     "pct_all": k / n_total * 100 if n_total else 0.0,
                     "pct_usable": k / n_usable * 100 if n_usable else 0.0})
    return pd.DataFrame(rows)


def group_sizes(coding: pd.DataFrame, ids: set[int]) -> dict[str, int]:
    """Distinct-response totals for the report-level groupings (each response counted once per group)."""
    s = lambda keys: len(ids_for(coding, keys) & ids)
    return {
        "positive": s(cfg.POSITIVE_KEYS),
        "suggestion": s(cfg.SUGGESTION_KEYS),
        "teaching": s(cfg.TEACHING_KEYS),
        "practice": s(["sug_practice"]),
        "platform_mention": s(["plat_mention"]),
        "platform_problem": s(cfg.PLATFORM_PROBLEM_KEYS),
        "concern": s(cfg.CONCERN_KEYS),
    }


def feedback_tone(responses: pd.DataFrame, coding: pd.DataFrame, usable: set[int]) -> pd.DataFrame:
    """Interpretation layer: classify each response from its coded themes. Every response gets exactly one tone."""
    pos = ids_for(coding, cfg.POSITIVE_KEYS)
    crit = ids_for(coding, cfg.SUGGESTION_KEYS + cfg.PLATFORM_PROBLEM_KEYS + cfg.CONCERN_KEYS)

    def tone(i: int) -> str:
        if i in pos and i in crit:
            return "Positive, with a suggestion or problem"
        if i in pos:
            return "Positive only"
        if i in crit:
            return "Suggestion / problem, no positive remark"
        if i in usable:
            return "Other comment (neutral or too vague)"
        return "No usable comment"

    r = responses[["response_id", "mentor"]].copy()
    r["tone"] = r["response_id"].map(tone)
    return r


TONE_ORDER = ["Positive only", "Positive, with a suggestion or problem", "Suggestion / problem, no positive remark",
              "Other comment (neutral or too vague)", "No usable comment"]


def comment_table(responses: pd.DataFrame, coding: pd.DataFrame) -> pd.DataFrame:
    """One row per response and theme with redacted text, for the explorer and exports."""
    m = coding.merge(responses[["response_id", "mentor", "improve_text", "else_text"]], on="response_id")
    m["theme"] = m["theme_key"].map(cfg.THEME_LABEL)
    m["category"] = m["theme_key"].map(cfg.THEME_CAT)
    return m.sort_values(["category", "theme", "response_id"]).reset_index(drop=True)
