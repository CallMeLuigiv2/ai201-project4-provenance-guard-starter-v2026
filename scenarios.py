"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

A scenario carries **one** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
              It can also carry "raw_bodies": strings sent byte for byte,
              claiming to be JSON, for a body that isn't JSON at all.

    "appeals" a list of strings. Each is submitted, then appealed with the
              content_id that came back, and the log is checked for the
              `under_review` entry. One appeal on a made-up content_id is
              added at the end of each trial. (I added this to run_eval.py,
              because the appeal path can't be tested by sending text alone.)

Where every text came from, and how it was chosen: samples/SOURCES.md.
"""

import json
from pathlib import Path

SAMPLES = Path(__file__).parent / "samples"


def _paragraphs(name: str) -> list[str]:
    text = (SAMPLES / name).read_text(encoding="utf-8")
    return [p.strip() for p in text.split("\n\n") if p.strip()]


HEALTHCARE = _paragraphs("my_writing/healthcare_2019.txt")
FLOODING = _paragraphs("my_writing/flooding_2019.txt")
ATTENTION = _paragraphs("human_attention_is_all_you_need_2017.txt")
_HC3 = json.loads((SAMPLES / "ai_hc3_chatgpt.json").read_text(encoding="utf-8"))
HC3_CHATGPT = _HC3["chatgpt"]
HC3_SPLICES = _HC3["splices"]

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # Every paragraph of both of my 2019 essays. 0 of 11 may be labelled AI.
        "texts": HEALTHCARE + FLOODING,
    },
    {
        "name": "spread AI (HC3)",
        "criterion": 2,
        # Confirmed ChatGPT text, never used to tune anything.
        "texts": HC3_CHATGPT,
    },
    {
        "name": "spread human (Attention)",
        "criterion": 2,
        # Confirmed human text from 2017. The AI average must beat this by 0.30.
        "texts": ATTENTION,
    },
    {
        "name": "label coverage",
        "criterion": 3,
        # Three human, three half-and-half, three AI. All 3 labels must appear.
        "texts": FLOODING[:3] + HC3_SPLICES + HC3_CHATGPT[:3],
    },
    {
        "name": "appeals",
        "criterion": 4,
        # 5 of 5 must succeed and log under_review; the made-up id must 404.
        "appeals": HEALTHCARE,
    },
    {
        "name": "bad input",
        "criterion": 5,
        # Every one must get a 400 with a message, and be logged as a rejection.
        "bodies": [
            {"creator_id": "eval_bad_missing"},
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": None, "creator_id": "eval_bad_null"},
            {"text": 12345, "creator_id": "eval_bad_number"},
            {"text": "Only a few words here, nowhere near enough to judge.",
             "creator_id": "eval_bad_short"},
            {"text": "word " * 5000, "creator_id": "eval_bad_huge"},
        ],
        "raw_bodies": ['{"text": "this body never closes'],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        kinds = [k for k in ("texts", "bodies", "appeals") if scenario.get(k)]
        if len(kinds) > 1:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has {' and '.join(kinds)} "
                f"— pick one"
            )
            continue

        if scenario.get("bodies"):
            for j, body in enumerate(scenario["bodies"], 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            for j, raw in enumerate(scenario.get("raw_bodies", []), 1):
                if not isinstance(raw, str):
                    problems.append(f"scenario {i}, raw body {j} is not a string")
            continue

        texts = scenario.get("texts") or scenario.get("appeals")
        if not texts:
            problems.append(f"scenario {i} has no texts, bodies or appeals")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
