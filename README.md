# Student Feedback Analysis Dashboard

Interactive Streamlit dashboard for CipherSchools Operations Intern Assignment 2, Problem 2.
It reads the **original Excel export** (238 responses, 8 mentors) and shows the approved mentor leaderboard,
comparison charts, question scores, qualitative themes, test-platform findings and downloadable reports.

## Run on Windows with VS Code (step by step)

**One-time setup**

1. Install Python 3.11, 3.12 or 3.13 from https://www.python.org/downloads/. On the first installer screen, tick **"Add python.exe to PATH"**, then click Install Now.
2. Install VS Code from https://code.visualstudio.com/ and, inside it, the **Python** extension (Extensions icon on the left, search "Python", Install).
3. Unzip `feedback_dashboard.zip` (right-click, Extract All). Keep the folder somewhere simple, for example `C:\Projects\feedback_dashboard`.
4. In VS Code: **File > Open Folder...** and choose the `feedback_dashboard` folder (the one that contains `app.py`).

**Install and run**

5. Open a terminal in VS Code: **Terminal > New Terminal** (PowerShell is fine).
6. Create a virtual environment and activate it:
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   If PowerShell says scripts are disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, answer **Y**, and activate again. (Or use Command Prompt and run `.venv\Scripts\activate.bat`.)
   You should now see `(.venv)` at the start of the prompt. If VS Code asks "We noticed a new environment", click **Yes**.
7. Install the dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
8. Start the dashboard:
   ```powershell
   python -m streamlit run app.py
   ```
   Your browser opens at http://localhost:8501. If it does not, paste that address into the browser. Streamlit may ask for an email on the very first run: just press Enter.
9. Stop the dashboard with **Ctrl+C** in the terminal. Next time, only steps 5, 6 (the activate line) and 8 are needed.

**Check that everything works (optional but recommended before a demo)**

```powershell
python -m pytest tests -q
```
You should see `43 passed`.

**If something goes wrong**

- `'py' is not recognized`: use `python` instead of `py`, or reinstall Python with "Add python.exe to PATH" ticked.
- `streamlit is not recognized`: always start it with `python -m streamlit run app.py`, with the virtual environment active.
- Port already in use: `python -m streamlit run app.py --server.port 8502`.
- The page looks stale after you edit a file: press **R** in the browser tab or choose "Rerun".

### macOS / Linux

```bash
cd feedback_dashboard
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

## What is inside

| Page | What it shows |
|---|---|
| Overview | Total responses and mentors, headline numbers, low-response warning, overall scores, rating mix |
| Mentor Leaderboard | Final leaderboard: five question averages, overall score, rank, low-response flag |
| Mentor Comparison | Overall dots, heatmap, per-question comparison, score mix, sample size, mentor profile |
| Question Scores | Average and score mix per question; syllabus pace and platform rating as unscored context |
| Feedback Themes | Feedback tone, theme counts (each response once per theme), verbatim quotes, comment browser |
| Test Platform | Platform rating, complaints by type, rating vs written comments, quotes, improvement requests |
| Reports & Downloads | Excel workbook (4 sheets) and CSV files that follow the sidebar filters |
| Method & Data Notes | Score mapping, rounding, data versus interpretation, limits |

Sidebar filters: **Mentors** (scores and counts are recalculated) and **Feedback categories** (themes, comments, exports).
Ranks always stay the locked ranks across all 8 mentors.

## Method (locked)

1. Each of five questions is converted to 1-5 (`config.py`, `SCORED`).
2. A mentor's sections are pooled; each response counts once.
3. Overall score = equal-weight mean of the five question averages.
4. Rank by the unrounded overall score; shown to 2 decimals.
5. Fewer than 10 responses = low-response flag. This is an analytical threshold, not an assignment requirement.

Syllabus pace and test-platform rating are **not** scored.

## Data versus interpretation

Every section carries a badge. **Data** = computed from the Excel file (scores, counts, quotes).
**Interpretation** = analyst judgement (theme coding, feedback tone, suggested follow-ups).
The theme coding is in `data/qualitative_coding.csv` (one row per response Id and theme), so it can be audited or edited.
A response is counted at most once per theme.

## Project structure

```
feedback_dashboard/
  app.py                    entry point, sidebar filters, navigation
  config.py                 paths, approved scales, themes, curated quotes
  requirements.txt
  .streamlit/config.toml    theme
  data/
    student_feedback.xlsx   original dataset, unchanged
    qualitative_coding.csv  manual theme coding by response Id
    usable_comment_ids.csv  responses with real comment content (141)
  src/
    data_loader.py          load + validate Excel, score columns, name redaction
    scoring.py              mentor table, pooling, ranking, distributions
    qualitative.py          theme counts, feedback tone, comment table
    charts.py               Altair charts
    reports.py              Excel / CSV builders
    ui.py                   CSS, KPI cards, badges
  views/                    one module per page
  tests/                    43 tests (locked numbers, report counts, UI, exports)
```

## Tests

```bash
python -m pytest tests -v
```

The tests check that the dashboard reproduces the locked leaderboard exactly, that theme counts equal the report,
that every quote is verbatim, that staff names are removed, that every page renders (also with filters), and that exports are correct.

## Privacy

Mentor first names in comments are replaced by `[mentor]`, and one comment with identifying detail is withheld.
Email and name columns (anonymous / empty in the file) are never read.

## Tested with

| Check | Result |
|---|---|
| Python 3.13, Streamlit 1.67, pandas 3.1 (newest) | 43 tests pass |
| Python 3.11, Streamlit 1.40, pandas 2.0 (oldest allowed by requirements.txt) | 43 tests pass |
| Real browser (Chromium): all 8 pages, filters, Reset, Excel and CSV downloads | 47 checks pass |
| Chart data compared with an independent calculation from the raw Excel | 210 checks pass |
