"""Central configuration: file paths, approved scoring scales, themes and curated quotes.

Nothing in here is sample data. The scales are the mapping approved and locked for the assignment.
"""
from pathlib import Path

ROOT = Path(__file__).parent
EXCEL_PATH = ROOT / "data" / "student_feedback.xlsx"          # original dataset, untouched
CODING_PATH = ROOT / "data" / "qualitative_coding.csv"        # manual theme coding by response Id
USABLE_PATH = ROOT / "data" / "usable_comment_ids.csv"        # responses with real comment content

LOW_RESPONSE_THRESHOLD = 10   # analytical threshold, NOT an assignment requirement

# ---------------------------------------------------------------- source columns (exact Excel headers)
COL_ID = "Id"
COL_BATCH = "Batch"
COL_IMPROVE = "Which area would you most like us to improve?"
COL_ELSE = "Anything else you would like us to know?"
COL_SYLLABUS = "How is the current syllabus flow for you?"
COL_PLATFORM = "How has your experience been with the Test Platform?"

# ---------------------------------------------------------------- the five scored questions (equal weight)
SCORED = {
    "Satisfaction": ("How satisfied are you with your semester classes so far?",
                     {"Very Dissatisfied": 1, "Dissatisfied": 2, "Satisfied": 3, "Very Satisfied": 4, "Extremely Satisfied": 5}),
    "Clarity": ("How clearly are the topics explained during class?",
                {"Not Clear at All": 1, "Slightly Clear": 2, "Moderately Clear": 3, "Very Clear": 4, "Extremely clear": 5}),
    "Mentor overall": ("How would you rate your mentor overall?",
                       {"Needs Significant Improvement": 1, "Needs Improvement": 2, "Good": 3, "Very Good": 4, "Excellent": 5}),
    "Engagement": ("How engaging and interactive are your classroom sessions?",
                   {"Not Engaging": 1, "Slightly Engaging": 2, "Moderately Engaging": 3, "Very Engaging": 4, "Highly Engaging": 5}),
    "Class quality": ("How would you rate the overall quality of your classes?",
                      {"Needs Significant Improvement": 1, "Needs Improvement": 2, "Good": 3, "Very Good": 4, "Excellent": 5}),
}
QUESTIONS = list(SCORED)

# Questions that are NOT part of the score (shown as context only)
SYLLABUS_ORDER = ["Too Slow", "Slightly Slow", "Just Right", "Slightly Fast", "Too Fast"]
PLATFORM_ORDER = ["Excellent", "Good", "Needs Improvement", "Haven’t used it enough yet"]

# ---------------------------------------------------------------- privacy: staff names removed from comment text
REDACT_NAMES = ["phaham", "sudhanshu"]
WITHHOLD_FIELDS = {(93, "else"): "[withheld: contains identifying detail about a student]"}

# ---------------------------------------------------------------- qualitative themes
CAT_POS, CAT_SUG, CAT_PLAT, CAT_CON, CAT_CTX = (
    "Positive feedback", "Improvement suggestions", "Test platform", "Other concerns", "Context (neutral)")
CATEGORIES = [CAT_POS, CAT_SUG, CAT_PLAT, CAT_CON, CAT_CTX]

# key: (label, category)
THEMES = {
    "pos_praise": ("Praise for mentor / teaching", CAT_POS),
    "pos_general": ("General satisfaction (no specifics)", CAT_POS),
    "pos_problem_solving": ("Live problem-solving in class appreciated", CAT_POS),
    "pos_platform": ("Platform called useful (also reports issues)", CAT_POS),
    "sug_practice": ("More coding practice", CAT_SUG),
    "sug_examformat": ("Practice in university exam (Neo) format", CAT_SUG),
    "sug_explain": ("Clearer / deeper explanation", CAT_SUG),
    "sug_examples": ("More examples / visuals", CAT_SUG),
    "sug_engage": ("More engaging / interactive classes", CAT_SUG),
    "sug_basics": ("More time on basics / syllabus too hard", CAT_SUG),
    "sug_notes": ("Lecture notes / reading resources", CAT_SUG),
    "sug_discipline": ("Class discipline", CAT_SUG),
    "sug_doubt": ("Doubt-solving sessions", CAT_SUG),
    "sug_audio": ("Speaker audibility (voice too low)", CAT_SUG),
    "plat_mention": ("Any mention of the test platform", CAT_PLAT),
    "plat_lag": ("Lag / slow / hanging", CAT_PLAT),
    "plat_freeze": ("Laptop froze, forced shutdown", CAT_PLAT),
    "plat_login": ("Login problems", CAT_PLAT),
    "plat_screen": ("Screen-sharing failures in tests", CAT_PLAT),
    "plat_noattempt": ("Could not attempt / complete a test", CAT_PLAT),
    "plat_bugs": ("Not working properly / bugs", CAT_PLAT),
    "plat_improve": ("“Needs improvement” (no detail)", CAT_PLAT),
    "plat_vague": ("Test/browser wording too vague to classify", CAT_PLAT),
    "con_cipher": ("Does not want CipherSchools activities", CAT_CON),
    "con_faculty": ("Cannot follow / uncomfortable with a faculty member", CAT_CON),
    "con_boring": ("Class described as boring", CAT_CON),
    "con_prize": ("Contest reward not received", CAT_CON),
    "con_course": ("Course name shown as DAA instead of DSA", CAT_CON),
    "ctx_neo": ("University Neo platform mentioned", CAT_CTX),
    "ctx_topic_only": ("Area named, no detail", CAT_CTX),
}
THEME_LABEL = {k: v[0] for k, v in THEMES.items()}
THEME_CAT = {k: v[1] for k, v in THEMES.items()}

# Platform sub-themes that describe an actual problem (the “23 responses” in the report)
PLATFORM_PROBLEM_KEYS = ["plat_lag", "plat_freeze", "plat_login", "plat_screen", "plat_noattempt", "plat_bugs", "plat_improve"]
TEACHING_KEYS = ["sug_explain", "sug_examples", "sug_basics", "sug_engage", "sug_notes", "sug_discipline", "sug_audio", "sug_doubt"]
SUGGESTION_KEYS = ["sug_practice", "sug_examformat"] + TEACHING_KEYS
POSITIVE_KEYS = ["pos_praise", "pos_general"]
CONCERN_KEYS = ["con_cipher", "con_faculty", "con_boring", "con_prize", "con_course"]

# ---------------------------------------------------------------- curated verbatim quotes (verified by tests)
# (theme_key, response_id, exact text as it appears after name redaction)
QUOTES = [
    ("pos_praise", 78, "Sir teaches in a great way."),
    ("pos_praise", 108, "The mentors are supportive, and the topics are explained clearly."),
    ("pos_praise", 192, "teaches very well and interacts nicely with us"),
    ("pos_problem_solving", 25, "he even helps us to work on leet code problems"),
    ("sug_practice", 82, "more practice questions would be better"),
    ("sug_practice", 138, "If we could squeeze in a few more practice questions it would be great."),
    ("sug_practice", 196, "Giving us a time to code in our laptops"),
    ("sug_examformat", 164, "sir should give a little bit focus on neo collab practice during exam time as LPU give questions directly as neo format"),
    ("sug_doubt", 115, "More practical examples and doubt-solving sessions."),
    ("sug_explain", 212, "Deep Explanation of topics"),
    ("sug_explain", 43, "More focus on logic building and explaining code briefly"),
    ("sug_basics", 203, "Not able to understand all as bcz it is so hard syllabus"),
    ("sug_notes", 93, "Please provide the notes of the lecture"),
    ("sug_audio", 2, "Sir is good but voice is very low"),
    ("plat_lag", 53, "the codefri browser, it lags everytime and hangs the laptop"),
    ("plat_freeze", 90, "it doesnt even let me abort and close the browser if it is lagging i have to force shut down and restart."),
    ("plat_noattempt", 192, "the screen sharing failed and I was unable to join the session, so the test could not be completed within the entry time"),
    ("plat_noattempt", 86, "unable to give the test because the codefri does not work properly in my laptop"),
    ("plat_screen", 78, "I was not able to share the screen while the test and could not attempt it."),
    ("plat_login", 32, "Codedri is not working, it always says wrong email password"),
    ("plat_login", 211, "Sometimes technical issues make it difficult to access or attempt tests smoothly."),
    ("plat_bugs", 235, "The test platform is not working well"),
    ("con_cipher", 42, "We don't want cipher school or anything like that we have enough work to do"),
    ("con_faculty", 36, "I think I am not comfortable to this faculty"),
    ("con_boring", 191, "The class is very boring"),
]
