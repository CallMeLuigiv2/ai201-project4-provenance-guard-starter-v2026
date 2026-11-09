#!/usr/bin/env python3
"""
Run your five criteria three times each.  <- UNIT 8, MILESTONE 3

    python app.py                              # in one terminal
    python run_eval.py --label before          # in another
    python run_eval.py --label after

The attack set tests what staff thought to test. This tests what *you* thought
to test, and the two rarely overlap much. Both count.

Fill in `scenarios.py` first — that's where you say what each criterion needs
run against it. A criterion about false positives needs your own writing. One
about label coverage needs inputs across the score range.

!! Three trials, and **your first signal runs a model, so identical input can
score differently twice.** That's exactly why repeats matter here.

This does the sending and the recording. It does not decide whether a trial
passed — that depends on the criterion you wrote, so the Verdict column comes
back blank.
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import config

# Windows consoles often run a codepage that can't print every character in
# this file's help text. Without this, `--help` ends in a UnicodeEncodeError
# traceback instead of the help — which is a miserable first thing to hit.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):  # not a normal text stream
        pass


DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"


class RawBody(str):
    """A body sent byte for byte while claiming to be JSON — for one that isn't."""


def bodies_for(scenario):
    """
    The request bodies one scenario sends.

    A "texts" or "appeals" scenario gets a creator_id made up for it. A
    "bodies" scenario is sent exactly as written, which is how a bad-input
    criterion says things a string can't — no `text` field, a null, something
    enormous — and its "raw_bodies" go out byte for byte.
    """
    if scenario.get("bodies"):
        return list(scenario["bodies"]) + [RawBody(r) for r in scenario.get("raw_bodies", [])]
    texts = scenario.get("texts") or scenario.get("appeals")
    return [
        {"text": text, "creator_id": f"eval_{scenario['name'][:12]}_{i}"}
        for i, text in enumerate(texts, 1)
    ]


def describe(body):
    """A short, readable note of what was sent — for the report."""
    if isinstance(body, RawBody):
        return f"raw body: {body[:60]}"
    if set(body) == {"text", "creator_id"} and isinstance(body.get("text"), str):
        text = body["text"]
        return text[:70] if text else "(empty text)"
    return json.dumps(body)[:120]


def post_submit(requests, args, body):
    if isinstance(body, RawBody):
        return requests.post(f"{args.url}/submit", data=body.encode("utf-8"),
                             headers={"Content-Type": "application/json"},
                             timeout=args.timeout)
    return requests.post(f"{args.url}/submit", json=body, timeout=args.timeout)


def log_size(requests, args):
    return requests.get(f"{args.url}/health", timeout=args.timeout).json()["log_entries"]


def appeal(requests, args, content_id, creator_id):
    """
    Appeal one content_id. Returns (status, whether the log now shows it
    under_review) — the second half is the part a 200 alone can't prove.
    """
    response = requests.post(f"{args.url}/appeal", timeout=args.timeout, json={
        "content_id": content_id,
        "creator_id": creator_id,
        "reasoning": "Eval run: checking the appeal path end to end.",
    })
    entries = requests.get(f"{args.url}/log", params={"limit": 20},
                           timeout=args.timeout).json()["entries"]
    logged = any(e.get("content_id") == content_id and e.get("event") == "appeal"
                 and e.get("status") == "under_review" for e in entries)
    return response.status_code, logged


def short(result):
    """One word per request for the console line."""
    if "appeal_status" in result:
        return f"{result.get('guess') or ''} appeal {result['appeal_status']}".strip()
    return result.get("guess") or str(result.get("status"))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print("The `requests` package isn't installed.\n"
              "Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    try:
        import scenarios
    except ImportError:
        print("No scenarios.py found. Milestone 3 starts by filling it in.",
              file=sys.stderr)
        sys.exit(1)

    problems = scenarios.validate()
    if problems:
        print("scenarios.py has problems:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    try:
        requests.get(f"{args.url}/health", timeout=5)
    except Exception:  # noqa: BLE001
        print(f"Nothing answering at {args.url}. Start it:  python app.py",
              file=sys.stderr)
        sys.exit(1)

    if args.trials < 3:
        print(f"!! {args.trials} trial(s). The submission asks for three.\n")

    rows = []
    for scenario in scenarios.SCENARIOS:
        print(f"\n{scenario['name']}  (criterion {scenario.get('criterion') or '—'})")

        trials = []
        for trial in range(1, args.trials + 1):
            results = []
            for i, body in enumerate(bodies_for(scenario), 1):
                preview = describe(body)
                try:
                    before = log_size(requests, args) if scenario.get("bodies") else None
                    response = post_submit(requests, args, body)
                    try:
                        payload = response.json() if response.content else {}
                    except ValueError:
                        payload = {"reason": f"not JSON: {response.text[:80]}"}
                    result = {
                        "status": response.status_code,
                        "guess": payload.get("guess"),
                        "confidence": payload.get("confidence"),
                        "model_score": payload.get("model_score"),
                        "style_score": payload.get("style_score"),
                        "combined_score": payload.get("combined_score"),
                        "label": payload.get("label"),
                        "reason": payload.get("error"),
                        "message": payload.get("message"),
                        "sent": preview,
                    }
                    # A bad-input criterion also says every refusal is logged.
                    if before is not None:
                        last = requests.get(f"{args.url}/log", params={"limit": 1},
                                            timeout=args.timeout).json()["entries"]
                        result["logged_as_rejection"] = (
                            log_size(requests, args) == before + 1
                            and bool(last) and last[-1].get("status") == "rejected"
                        )
                    if scenario.get("appeals") and payload.get("content_id"):
                        result["appeal_status"], result["appeal_logged"] = appeal(
                            requests, args, payload["content_id"], body["creator_id"])
                    results.append(result)
                except Exception as exc:  # noqa: BLE001
                    results.append({"status": None, "error": f"{type(exc).__name__}: {exc}",
                                    "sent": preview})

            # And one appeal that must fail: a content_id that was never issued.
            if scenario.get("appeals"):
                status, _ = appeal(requests, args, f"made-up-content-id-{trial}",
                                   "eval_appeals_fake")
                results.append({"sent": "appeal on a made-up content_id",
                                "appeal_status": status})

            trials.append(results)
            print(f"  trial {trial}: {', '.join(short(r) for r in results)}")

        rows.append({"scenario": scenario, "trials": trials})

    write_report(rows, args)


def write_report(rows, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"run_{stamp}{label}.md"

    n = args.trials
    headers = " | ".join(f"Run {i}" for i in range(1, n + 1))
    divider = "|".join(["---"] * n)

    lines = [
        f"# Run log{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `run_eval.py::main`",
        "- Service: `app.py::submit` · scoring: `scoring.py::combine_signals`",
        f"- {n} trials per criterion · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Fill in Target from `criteria.md`, and Run and Verdict from the output",
        "underneath. Whether a trial passed depends on the criterion you wrote.",
        "",
        f"| Criterion | Target | {headers} | Verdict |",
        f"|---|---|{divider}|---|",
    ]

    for row in rows:
        scenario = row["scenario"]
        number = scenario.get("criterion")
        name = f"{number}. {scenario['name']}" if number else scenario["name"]
        lines.append(f"| {name} |  | {' | '.join([' '] * n)} |  |")

    lines += ["", "---", "", "## What actually came back", "",
              "Real output. Paste the relevant parts into your README — the rubric",
              "asks for the actual JSON, not a description of it.", ""]

    for row in rows:
        scenario = row["scenario"]
        lines += [f"### {scenario['name']}", ""]
        for trial_number, results in enumerate(row["trials"], 1):
            lines += [f"**Trial {trial_number}**", "", "```json",
                      json.dumps(results, indent=2), "```", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")
    print("Commit it. It's the evidence the test actually happened.")


if __name__ == "__main__":
    main()
