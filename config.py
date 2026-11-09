"""
Settings for Provenance Guard.

Everything you're likely to change lives here, at the top, on purpose.

You'll edit the thresholds in Milestone 5 and the rate limits in unit 8.
"""

import os
from pathlib import Path

ROOT = Path(__file__).parent


# ─── The service ─────────────────────────────────────────────────────────────

# `127.0.0.1` is loopback — only your own machine can reach it, which is what
# you want all through units 7 and 8. A host somewhere else has to accept
# traffic from outside the box, and that means `0.0.0.0`. Setting the env var
# is how you get it; the default keeps your local `curl` commands unchanged.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Flask's debug mode gives anyone who can reach the service an interactive
# Python prompt inside your process. Fine on loopback, a gift to strangers
# anywhere else — so it turns itself off the moment HOST isn't loopback.
DEBUG = os.getenv("AI201_DEBUG", "1") == "1" and HOST in ("127.0.0.1", "localhost")


# ─── The local model ─────────────────────────────────────────────────────────
# Your first signal runs a language model ON YOUR OWN MACHINE. No account, no
# key, no card. It downloads about 550 MB the first time — do that before
# class, not during it.
#
# What it measures: how *predictable* your text is to a language model. Text a
# model finds easy to predict tends to be text a model wrote.
#
# The first call is the slow one — ten to twenty seconds while the model loads,
# longer on an older laptop. After that it stays in memory and a submission
# takes a second or two. That cost is part of what you're learning: this is
# what running a model inline in a request actually looks like.

DETECTOR_MODEL = os.getenv("AI201_DETECTOR_MODEL", "gpt2")

# Longer text gives a steadier reading but takes longer. 400 tokens is roughly
# 300 words, which is enough for the signal to mean something.
DETECTOR_MAX_TOKENS = 400


# ─── Input limits (Milestone 3) ──────────────────────────────────────────────
# Below the minimum, neither signal has enough to go on, so the route says
# "too short to determine" instead of guessing. Above the maximum it says "too
# long to determine". Signal one only reads the first DETECTOR_MAX_TOKENS
# anyway, so a huge text would mostly go unread.

MIN_WORDS = 40
MAX_CHARS = 20_000


# ─── Scoring (Milestone 4) ───────────────────────────────────────────────────
# How much each signal counts toward the combined score.
#
# ⚠️ These are placeholders. Milestone 4 asks you to write your combining rule
# down BEFORE you code it, and to put the numbers in your README. Whatever you
# decide, it goes here.

WEIGHT_MODEL_SIGNAL = 0.5
WEIGHT_STYLE_SIGNAL = 0.5

# My rule is "agree, or say unsure". A signal at or above this point says AI,
# below it says human. When the two signals say different things, the combined
# score is held inside the unsure band. See scoring.combine_signals.
SIGNAL_MIDPOINT = 0.5


# ─── Thresholds (Milestone 5) ────────────────────────────────────────────────
# Where one label becomes another. Scores run 0.0 (confidently human) to 1.0
# (confidently AI).
#
#   score < HUMAN_THRESHOLD          -> high-confidence human
#   between the two                  -> unsure
#   score > AI_THRESHOLD             -> high-confidence AI
#
# ⚠️ This is where your false-positive decision from Milestone 1 actually gets
# made. Widening the unsure band means fewer wrong accusations and more AI text
# getting through. There is no setting that avoids the trade — only settings
# that decide who pays for it.

HUMAN_THRESHOLD = 0.35

# 0.65 in unit 7. Lowered to 0.62 in unit 8, together with dropping the
# vocabulary measure from the style signal. Every line from 0.62 down to 0.56
# caught the same attacks; at 0.55 a human paragraph (from "Attention Is All
# You Need") was accused. 0.62 is the top of that range, so it leaves the
# widest margin before anyone is accused. See README, The Improvement.
AI_THRESHOLD = 0.62

# ⚠️ One thing that catches people out in Milestone 5. A weighted average can
# only land between its two inputs — so while `style_signal` is still the stub
# returning 0.5, the combined score can never leave 0.25–0.75 no matter what
# the model signal says, and the human label needs a model score below 0.20 to
# be reachable at all.
#
# If a label you can't reach is the problem, the fix is upstream of the
# thresholds: a style signal that actually varies. `scoring.label_ranges()`
# prints the bands; the reachable range is a different question.


# ─── Rate limiting (UNIT 8) ──────────────────────────────────────────────────
# Off in unit 7. You turn it on and choose the numbers in unit 8, Milestone 1.
#
# Think about two people: a real writer submitting their own work a few times
# an hour, and a script sending a thousand variations to map your thresholds.
# Your README has to say why your numbers and not others.

# On by default from unit 8. AI201_RATE_LIMITS=0 turns it off.
RATE_LIMITING_ENABLED = os.getenv("AI201_RATE_LIMITS", "1") == "1"

# Counted per creator_id (see rate_limit_key in app.py).
#
# 5 a minute: a writer who just got "unsure" may edit and resubmit 3-4 times
# in a few minutes, and 5 covers that. Going lower barely slows a script,
# which can just space its requests out. It would also break run_eval.py,
# which sends each creator_id once per trial, three times within a minute.
#
# 50 a day: a heavy day of real use is 20-30 submissions. A script mapping the
# thresholds needs hundreds. The daily cap is what actually stops that.
RATE_LIMIT_PER_MINUTE = 5
RATE_LIMIT_PER_DAY = 50

# Flask-Limiter warns loudly without this. In-memory is right for one laptop
# and wrong for anything real — a restart forgets every count, and two copies
# of the service wouldn't share limits.
RATE_LIMIT_STORAGE = "memory://"


# ─── Paths ───────────────────────────────────────────────────────────────────

LOG_DIR = ROOT / "logs"
AUDIT_LOG = LOG_DIR / "audit.jsonl"
RESULTS_DIR = ROOT / "results"
