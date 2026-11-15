"""Load the original Excel file, validate it and attach numeric scores. No rows are dropped."""
from __future__ import annotations

import re

import pandas as pd

import config as cfg


def _label(value) -> str:
    """'Very Good - The mentor explains…' -> 'Very Good' (non-breaking spaces normalised)."""
    return str(value).split(" -")[0].replace("\xa0", " ").strip()


def redact(text: str) -> str:
    """Replace staff first names with [mentor]. Applied to every comment that is shown or exported."""
    if not text:
        return ""
    for name in cfg.REDACT_NAMES:
        text = re.sub(rf"\b{name}\b(\s+sir)?", "[mentor]", text, flags=re.I)
    return text


def load_responses(path=cfg.EXCEL_PATH) -> pd.DataFrame:
    df = pd.read_excel(path)
    needed = [cfg.COL_ID, cfg.COL_BATCH, cfg.COL_IMPROVE, cfg.COL_ELSE, cfg.COL_SYLLABUS, cfg.COL_PLATFORM] + [c for c, _ in cfg.SCORED.values()]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"Excel file is missing expected columns: {missing}")

    out = pd.DataFrame({"response_id": df[cfg.COL_ID].astype(int)})
    parts = df[cfg.COL_BATCH].astype(str).str.split("|", n=1, expand=True)
    out["mentor"] = parts[0].str.strip()
    out["section"] = parts[1].str.strip() if parts.shape[1] > 1 else ""

    for key, (col, mapping) in cfg.SCORED.items():
        labels = df[col].map(_label)
        out[f"label_{key}"] = labels
        out[key] = labels.map(mapping)
        bad = labels[out[key].isna()].unique().tolist()
        if bad:
            raise ValueError(f"Unmapped answer option(s) for '{key}': {bad}")
    out["syllabus"] = df[cfg.COL_SYLLABUS].map(_label)
    out["platform"] = df[cfg.COL_PLATFORM].map(_label)

    clean = lambda s: s.fillna("").astype(str).str.strip()
    out["improve_raw"] = clean(df[cfg.COL_IMPROVE])
    out["else_raw"] = clean(df[cfg.COL_ELSE])
    out["improve_text"] = [cfg.WITHHOLD_FIELDS.get((i, "improve"), redact(t)) for i, t in zip(out["response_id"], out["improve_raw"])]
    out["else_text"] = [cfg.WITHHOLD_FIELDS.get((i, "else"), redact(t)) for i, t in zip(out["response_id"], out["else_raw"])]
    if out["response_id"].duplicated().any():
        raise ValueError("Duplicate response Ids in the Excel file")
    return out.sort_values("response_id").reset_index(drop=True)
