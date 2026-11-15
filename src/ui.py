"""Small UI helpers: CSS, KPI cards, badges, notices."""
from __future__ import annotations

import streamlit as st

CSS = """
<style>
.block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1400px;}
h1, h2, h3 {letter-spacing: -0.01em;}
.page-title {font-size: 1.9rem; font-weight: 700; margin-bottom: 0.1rem; color: #0F172A;}
.page-sub {color: #64748B; margin-bottom: 1.1rem; font-size: 0.95rem;}
.kpi {background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 14px 16px;
      box-shadow: 0 1px 2px rgba(15,23,42,0.04); height: 100%; min-height: 128px; border-top: 4px solid var(--accent);}
.kpi .label {font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748B; font-weight: 600;}
.kpi .value {font-size: 1.9rem; font-weight: 700; color: #0F172A; line-height: 1.25;}
.kpi .sub {font-size: 0.8rem; color: #64748B;}
.badge {display:inline-block; font-size: 0.66rem; font-weight: 700; padding: 2px 9px; border-radius: 999px;
        letter-spacing: 0.05em; vertical-align: middle; margin-left: 8px; text-transform: uppercase;}
.badge.data {background:#DCFCE7; color:#166534;}
.badge.interp {background:#EDE9FE; color:#5B21B6;}
.badge.warn {background:#FEF3C7; color:#92400E;}
.note {border-left: 4px solid var(--c); background: var(--bg); border-radius: 8px; padding: 10px 14px; margin: 6px 0 12px 0;
       font-size: 0.9rem; color: #334155;}
.quote {border-left: 3px solid #94A3B8; padding: 4px 12px; margin: 6px 0; color: #1E293B; background: #F8FAFC; border-radius: 4px;}
.quote .meta {color: #64748B; font-size: 0.78rem;}
section[data-testid="stSidebar"] {background: #0F172A;}
section[data-testid="stSidebar"] * {color: #E2E8F0;}
section[data-testid="stSidebar"] [data-baseweb="select"] * {color: #0F172A;}
section[data-testid="stSidebar"] .stButton button {background: #1E293B; border: 1px solid #64748B; color: #F8FAFC;}
section[data-testid="stSidebar"] .stButton button:hover {background: #334155; border-color: #94A3B8; color: #FFFFFF;}
section[data-testid="stSidebar"] .stButton button p {color: #F8FAFC;}
</style>
"""

KINDS = {"data": ("data", "Data"), "interp": ("interp", "Interpretation"), "warn": ("warn", "Caution")}


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="page-title">{title}</div><div class="page-sub">{subtitle}</div>', unsafe_allow_html=True)


def section(title: str, kind: str | None = None, caption: str = "") -> None:
    """Section heading with a Data / Interpretation badge so the reader always knows which one they are looking at."""
    b = ""
    if kind:
        cls, txt = KINDS[kind]
        b = f'<span class="badge {cls}">{txt}</span>'
    st.markdown(f"### {title}{b}", unsafe_allow_html=True)
    if caption:
        st.caption(caption)


def kpi_row(items: list[tuple]) -> None:
    cols = st.columns(len(items))
    for col, it in zip(cols, items):
        label, value, sub = it[0], it[1], it[2]
        accent = it[3] if len(it) > 3 else "#2563EB"
        col.markdown(
            f'<div class="kpi" style="--accent:{accent}"><div class="label">{label}</div>'
            f'<div class="value">{value}</div><div class="sub">{sub}</div></div>', unsafe_allow_html=True)


def notice(text: str, kind: str = "info") -> None:
    c, bg = {"info": ("#2563EB", "#EFF6FF"), "warn": ("#D97706", "#FFFBEB"), "interp": ("#7C3AED", "#F5F3FF")}[kind]
    st.markdown(f'<div class="note" style="--c:{c};--bg:{bg}">{text}</div>', unsafe_allow_html=True)


def quote(text: str, meta: str) -> None:
    safe = text.replace("<", "&lt;").replace(">", "&gt;")
    st.markdown(f'<div class="quote">“{safe}”<div class="meta">{meta}</div></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- Streamlit version compatibility
# Newer Streamlit uses width="stretch"; older releases only know use_container_width=True.
import inspect as _inspect

_NEW_WIDTH = "width" in _inspect.signature(st.altair_chart).parameters


def chart(c) -> None:
    """Draw an Altair chart at full container width on any supported Streamlit version."""
    if _NEW_WIDTH:
        st.altair_chart(c, width="stretch")
    else:
        st.altair_chart(c, use_container_width=True)


def table(df, **kwargs) -> None:
    """Draw a dataframe at full container width on any supported Streamlit version."""
    if _NEW_WIDTH:
        st.dataframe(df, width="stretch", **kwargs)
    else:
        st.dataframe(df, use_container_width=True, **kwargs)
