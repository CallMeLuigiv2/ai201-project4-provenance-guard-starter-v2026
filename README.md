# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. **It arrives.** A writer sends `POST /submit` with `{"text": "...", "creator_id": "..."}`.
2. **The route checks it.** If `text` is missing, empty, or not a string, the
   request is refused with a `400`. If it's under 40 words the writer is told
   *"This text is too short to determine"*; over 20,000 characters, *"This text
   is too long to determine."* Every refusal is written to the audit log as a
   rejection, and nothing gets scored.
3. **It gets an ID.** The service makes a `content_id`. That's the handle the
   writer uses later if they want to appeal.
4. **Signal one: the model.** gpt2 reads the first ~400 tokens (about 300 words)
   and measures how predictable the text is. Predictable text scores closer to
   1.0, which means more AI-like.
5. **Signal two: style.** Without reading for meaning, it measures the text's
   shape: how much sentence lengths vary, how varied the vocabulary is, and how
   punctuation is used. Even, uniform text scores closer to 1.0.
6. **Combine, then label.** `scoring.combine_signals` turns the two scores into
   one. `scoring.score_to_label` maps that to one of three labels (human, unsure,
   AI), written as a sentence a reader can understand. Wrongly accusing a human
   is treated as the worse mistake, so the AI label needs strong evidence.
7. **Log, answer, appeal.** The decision goes to `logs/audit.jsonl` with all nine
   fields, and the writer gets the label back. If they disagree,
   `POST /appeal` with their `content_id`, their `creator_id` and a reason
   moves the item to `under_review`. Only the original submitter can appeal
   their own piece. The original decision stays in the log.


---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** How predictable the text is to gpt2, a language model
running on my laptop (`detector.py::model_signal`). It reads the first ~400
tokens (about 300 words) and measures perplexity, meaning how surprised the
model is by each next word. Low perplexity becomes a high score: a
perplexity of 45 scores 0.5, and more predictable text scores closer to 1.0.
I kept the starter's midpoint of 45.

**Why that might differ between human and AI writing:** A language model
writes by picking a likely next word over and over, so its output is easy for
another language model to predict. People make odd word choices, go off on
tangents and use specific details, which surprise the model.

**What it can't see:** Who wrote the text. It rewards common words in
ordinary sentences, and plenty of people write that way. Our own test shows
this: the intro of my 2019 health care essay scored **0.657** and the
conclusion of my flooding essay scored **0.662**. Both are over the 0.65 AI
line on this signal alone, and I wrote both myself. Intros and conclusions
are the most generic part of an essay ("In conclusion… act now… secure the
future"), so they're the easiest to predict. It also never sees anything past
the first ~300 words, so AI text pasted after a human-written opening goes
unread.

### Signal two — the style signal

**What it measures:** The shape of the text, without reading for meaning
(`stylometry.py::style_signal`). It uses three measures:

| Measure | How it's computed | My essays (11 paragraphs) | AI paragraphs (5) | Which way is AI |
|---|---|---|---|---|
| Sentence-length spread | standard deviation of sentence lengths ÷ the mean | 0.29 – 0.65 | 0.12 – 0.27 | lower |
| Vocabulary variety | unique words ÷ total words, averaged over every 50-word window so long and short texts compare fairly | 0.72 – 0.83 | 0.88 – 0.92 | higher |
| Clause punctuation | commas, semicolons, colons and dashes per 100 words | 1.0 – 3.2 | 6.8 – 12.1 | higher |

Each measure is placed on a 0–1 scale between a "human" end and an "AI" end
(the `ANCHORS` in `stylometry.py`), and the three are averaged with equal
weight. One-sentence text has no spread to measure, so that part counts as
0.5 (no evidence either way).

**Why that might differ between human and AI writing:** AI sentences march in
step at similar lengths. AI also swaps in synonyms instead of repeating a key
term, and it stacks clauses and lists ("X, Y, and Z"). My writing repeats its
key terms ("the water table", "health care") and runs on with few commas. The
starter's hint said AI vocabulary is *narrower*. I already expected the
opposite, that AI overcomplicates its vocabulary, and the measurements agreed,
so that measure points the other way from the hint. Parentheses and quotation
marks are left out of the punctuation count because my essays use them for
citations.

**What it can't see:** Anything about meaning. It can't read. Cheap edits move
it: strip the commas out of AI text, or chop its sentences to uneven
lengths, and it reads as human. It also pushes the other way on a polished
human writer who uses lots of commas and a rich vocabulary. Finally, it was
calibrated on one human writer (me) and AI paragraphs from one AI (Claude),
so its "human" and "AI" ends may not fit other writers.

### The combining rule

**The rule:** *Agree, or say unsure.* Each signal says AI if it's at 0.5 or
above and human if it's below. If both say the same thing, the score is their
average. If they disagree, the average is held inside the unsure band, so two
methods disagreeing can neither accuse anyone nor clear anyone. That means the
AI label needs **both** signals to say AI, so signal one can never accuse a
plain writer on its own. The cost: some real AI text that only one signal
catches gets "unsure" instead of "AI."

**The numbers:** weights 0.5 (model) and 0.5 (style); a signal says AI at
0.5 or above (`SIGNAL_MIDPOINT`); unsure band 0.35 – 0.65. All are in
`config.py`.

**Where it lives:** `scoring.py::combine_signals`

**A case where my two signals split, and what my rule does with it:**

My health care intro: the model signal says **AI (0.657)** because the
writing is plain and predictable. The style signal says **human (0.322)**
because the paragraph has fewer than one comma or semicolon per 100 words and
keeps repeating its key terms. Its sentence lengths are actually fairly even
(spread 0.33), which leans slightly AI, but the other two measures outweigh it. They disagree, so the result is held in the unsure band:
**0.490 → unsure.** On the model signal alone, that paragraph would have been
labelled AI.

Here the average already fell inside the band. The hold changes the outcome
in two kinds of case:
- **Extreme splits.** Model 0.95 and style 0.40 average 0.675, which would be
  an AI label. The rule holds it at 0.65, which is unsure.
- **Clearing.** Body paragraph 2 of my health care essay has model 0.522 and
  style 0.120, which average 0.321 and would be labelled human. The rule holds
  it at 0.35, which is unsure. The rule is symmetric, so a disagreement can't
  clear a writer either.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | below 0.35 | We think a person wrote this. Both of our checks pointed that way. |
| unsure | 0.35 – 0.65 | We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review. |
| high-confidence AI | above 0.65 | This looks a lot like AI-generated writing. Both of our checks pointed that way, but they can be wrong. If you wrote this yourself, you can appeal and a person will review it. |

A score exactly on 0.35 or 0.65 is unsure. "Both of our checks pointed that
way" is literally true for the human and AI labels, because the combining
rule only lets a score out of the unsure band when both signals agree.

All three labels are reachable with real text. Paragraph 4 of my flooding
essay scores 0.265 (human), my health care intro scores 0.490 (unsure), and
an AI paragraph about South Florida flooding scores 0.89 (AI).

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

My own essays get this label 8 times out of 11, so I wrote it for myself,
reading it about something I know I wrote. It starts with what we don't know
("We can't tell either way") instead of hinting at AI. It says plainly that
"this is not an accusation," and explains why that's believable: unclear
results happen often with real human writing. And it offers a person to
review the piece instead of asking the writer to prove anything. I avoided
phrases like "may be AI-generated" or "possibly AI," because the reader would
only hear the accusation.



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "In life not much is guaranteed; only life and death can very much be ensured.  The government of the United States cannot give someone a house or a job. This is something that must be done individually. The government of the United States task their citizens with so many responsibilities and some people are not privileged enough to do these things on their own. One example would be health care where the United States ranks 12 according to Forbes in health care system ratings. What makes it even more ridiculous is the amount being spent compared to the rest of the countries on the list. The whole top ten who ranked better than the United States all have some shape or form of universal health care. This is concerning as the United States is known for being the example of a well-established country but finds itself behind when it comes to the topic of health. A revamped health care is needed to ensure the citizens that if anything they will be able to get help at any point in time without worry. The United States need a health care that can cut the cost that America spends, provide equality in care and creates a more simplistic system for everyone.", "creator_id": "stanluigi"}'
```

```json
{
  "combined_score": 0.4896,
  "confidence": 0.0208,
  "content_id": "10e8d4c9-e742-4cfd-965e-56aec81083c5",
  "guess": "unsure",
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "model_score": 0.6568,
  "style_score": 0.3223
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "10e8d4c9-e742-4cfd-965e-56aec81083c5", "creator_id": "stanluigi", "reasoning": "I wrote this myself. It'\''s the intro to an essay on US health care I wrote for AMH 2020 in April 2019, before AI writing tools were around."}'
```

```json
{
  "content_id": "10e8d4c9-e742-4cfd-965e-56aec81083c5",
  "message": "Thanks. Your appeal is recorded and a person will review this piece. The original decision stays on record until then.",
  "status": "under_review"
}
```

**What the log shows afterwards**

The first entry is a request with a body that wasn't JSON, from bad-input
testing just before this run. Refused requests get logged too. Then come the
decision and the appeal: the original decision stays as it was, and the appeal
sits after it with `under_review`.

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 3,
  "entries": [
    {
      "creator_id": "unknown",
      "event": "rejected",
      "reason": "invalid_json",
      "status": "rejected",
      "timestamp": "2026-11-02T02:52:38+00:00"
    },
    {
      "combined_score": 0.4896,
      "content_id": "10e8d4c9-e742-4cfd-965e-56aec81083c5",
      "creator_id": "stanluigi",
      "guess": "unsure",
      "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
      "model_score": 0.6568,
      "status": "decided",
      "style_score": 0.3223,
      "timestamp": "2026-11-02T02:53:22+00:00",
      "word_count": 209
    },
    {
      "content_id": "10e8d4c9-e742-4cfd-965e-56aec81083c5",
      "creator_id": "stanluigi",
      "event": "appeal",
      "reasoning": "I wrote this myself. It's the intro to an essay on US health care I wrote for AMH 2020 in April 2019, before AI writing tools were around.",
      "status": "under_review",
      "timestamp": "2026-11-02T02:53:22+00:00"
    }
  ]
}
```

---

## How I Used AI

I worked through this project with Claude (in Claude Code) as a partner,
milestone by milestone. For each milestone we talked through the options
before anything was built. Claude drafted code and write-up text and ran the
tests. I made the design decisions, read over the work, and nothing was
committed until we'd agreed on it.

**Moment 1: the design decisions**

- *What I asked for:* To go through the assignment together one milestone at
  a time and discuss each step.
- *What came back:* At each decision point Claude laid out the options and
  what each one would cost. Examples: three ways to combine the signals, what
  to do with too-short or too-long text, and whether `creator_id` should be
  required.
- *What I changed:* I made the calls. Wrongly accusing a human is the worse
  mistake, and that drives everything downstream. Text outside the limits gets
  told it's "too short / too long to determine" instead of being guessed at.
  Every submission must have a `creator_id` so we can see where the text came
  from. Of the three combining rules I picked "agree, or say unsure," because
  it's the most honest. And I had the appeal check that the person appealing
  is the one who submitted the piece, so nobody can appeal someone else's
  work. I also supplied the human writing the criteria are tested on: two of
  my own essays from 2019.

**Moment 2: which way the vocabulary measure points**

- *What I asked for:* A style signal that measures the shape of the writing.
- *What came back:* Claude's first plan followed the starter's hint, that
  narrow, repetitive vocabulary means AI.
- *What I changed:* I already knew that AI tends to overcomplicate its
  vocabulary and use more commas, dashes and other punctuation. Claude had it
  the other way. When we measured my essays against AI paragraphs on the same
  topics, the numbers agreed with me (vocabulary variety 0.72–0.83 for my
  writing, 0.88–0.92 for AI), so the measure now points the other way: more
  varied means more AI. We also checked my punctuation point against my own
  writing. Commas and dashes stayed in. Parentheses came out, because my
  essays use them for citations, and counting them would have made my own
  writing look more like AI.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 50 per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

The per-minute limit is there for the real writer. Someone who just got
"unsure" will edit a sentence and resubmit, maybe 3 or 4 times in a few
minutes, and 5 covers that, plus a double-click or a retry. I considered going
lower and decided against it. Lowering the per-minute limit hurts that writer
right when it matters, and it barely slows a script, which can just space its
requests out. Below 3 it would also break my own eval run: `run_eval.py` sends
each text under the same `creator_id` once per trial, three times within a
minute.

The per-day limit is there for the script. A heavy day of real use is 20–30
submissions, so 50 leaves room. A script sending a thousand variations to map
my thresholds gets 50 a day per account, which turns an afternoon's job into
weeks.

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

Per `creator_id` (`rate_limit_key` in `app.py`). Every submission must have
one, so that's always the key. This works well for a household or classroom
sharing one internet address: each writer has their own limit. But it fails
against a script. `creator_id` is just text in the request, so a script can
invent a new one for every request and never hit the limit. One script can
look like a thousand callers.

Limiting per address instead would fail the other way: a whole classroom
behind one school network would share 5 a minute. And all my testing comes
from one laptop, so a per-address limit would also block my own attack and
eval runs.

The real fix is authorization. Each writer gets a secret key or logs in, and
the server works out who's calling from that instead of trusting a field in
the request. Then the limit counts per real account, and making up a new name
doesn't reset it. That would also make my appeal rule truly airtight. Today
"only the submitter can appeal" just checks that the appealer typed the same
`creator_id`. I didn't build authorization in this unit because the attack and
eval tools send no credentials, so every request would come back `401` and
the tests would measure nothing.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

`python run_attacks.py --flood 15` (from `results/flood_2026-11-09_0029.md`):

```
400 400 400 400 400 429 429 429 429 429 429 429 429 429 429
```

The first five are `400`, not `200`, because the flood tool's text is 27
words long and my service refuses anything under 40 words as "too short to
determine." They still count against the limit, so a script can't get around
it by sending junk, and the limit kicks in at the 6th request.

To show the switch from `200` to `429` with text that actually gets scored,
I sent the same 426-word paragraph 8 times under one `creator_id`:

```
200 200 200 200 200 429 429 429
```

Every rejection is in the audit log with all nine fields, so a flood leaves a
trace instead of an absence:

```json
{"timestamp": "2026-11-09T05:30:03+00:00", "content_id": null, "creator_id": "flood_tester_long", "guess": null, "model_score": null, "style_score": null, "combined_score": null, "label": null, "status": "rejected", "event": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

All 56 attacks, run once with `python run_attacks.py --set ../attack_set
--label before`. The runner's report, with verdicts filled in, is
`results/attack_run_2026-11-09_0033_before.md`. The model, style and combined
scores come from `logs/audit.jsonl`.

**How we judged held or broke.** We graded strictly. For a safety system, an
attack counts as a success unless the system clearly stopped it.

- **AI text** (every evasion, plus PI01, PI02, PI03 and PI05): **held** only if
  it got the AI label or was refused. "Unsure" counts as **broke**. Unsure
  isn't a flag, so on a writing site that text gets published unchallenged.
- **Human text** (every false positive, plus PI04 and PI06): **held** if it
  wasn't labelled AI.
- **Malformed requests and the flood:** **held** if they got a 4xx and nothing
  crashed.

| Family | Attacks | Held | Broke |
|---|---|---|---|
| evasion | 10 | 2 | 8 |
| false_positive | 8 | 8 | 0 |
| prompt_injection | 6 | 3 | 3 |
| malformed | 20 | 20 | 0 |
| flood_same_creator | 12 | 12 | 0 |

**11 of 56 broke, and every one is AI text getting through. No human writing
was accused, and nothing crashed.** Being strict cuts both ways: none of the 7
scored human texts got the human label either. They weren't accused, but they
weren't cleared.

| ID | Family | Targeting | Status | Outcome | Model | Style | Combined | Verdict | What happened |
|---|---|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | unsure | 0.164 | 0.764 | 0.464 | **BROKE** | Typos fooled signal one (0.16); style still read AI. Split → held in unsure |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | unsure | 0.594 | 0.379 | 0.486 | **BROKE** | Chopped sentences pushed style under 0.5. Split → held in unsure |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | unsure | 0.666 | 0.565 | 0.616 | **BROKE** | Both signals say AI, but the average (0.616) is under the 0.65 line |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | ai | 0.611 | 0.752 | 0.682 | HELD | Caught: both signals say AI |
| EV05 | evasion | both signals: heavy human editing pass | 200 | unsure | 0.321 | 0.427 | 0.374 | **BROKE** | Heavy editing moved both signals to the human side; average 0.374 |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | unsure | 0.573 | 0.288 | 0.430 | **BROKE** | One long + one short sentence pushed style to 0.29. Split → unsure |
| EV07 | evasion | signal two: padding with punctuation | 200 | unsure | 0.586 | 0.687 | 0.637 | **BROKE** | Both signals say AI, but the average (0.637) is under the 0.65 line |
| EV08 | evasion | signal one: text below the token window | 400 | text_too_short | — | — | — | HELD | 10 words: refused as too short to determine |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.704 | 0.578 | 0.641 | **BROKE** | Both signals say AI, but the average (0.641) is under the 0.65 line |
| EV10 | evasion | signal two: repeated stanza structure | 200 | unsure | 0.979 | 0.153 | 0.566 | **BROKE** | Signal one 0.98, but the stanza shape pushed style to 0.15. Split → unsure |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | unsure | 0.618 | 0.255 | 0.436 | HELD | Not accused |
| FP02 | false_positive | human writing in a formal register | 200 | unsure | 0.739 | 0.318 | 0.528 | HELD | Not accused, but only because style read human. Signal one alone would have accused it |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | unsure | 0.805 | 0.337 | 0.571 | HELD | Not accused, but only because style read human. Signal one alone would have accused it |
| FP04 | false_positive | a student essay written to a rubric | 200 | unsure | 0.833 | 0.332 | 0.582 | HELD | Not accused, but only because style read human. Signal one alone would have accused it |
| FP05 | false_positive | technical documentation written by a person | 200 | unsure | 0.800 | 0.317 | 0.559 | HELD | Not accused, but only because style read human. Signal one alone would have accused it |
| FP06 | false_positive | a person imitating a formal template | 200 | unsure | 0.881 | 0.095 | 0.488 | HELD | Not accused, but only because style read human. Signal one alone would have accused it |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | unsure | 0.882 | 0.100 | 0.491 | HELD | Not accused, but only because style read human. Signal one alone would have accused it |
| FP08 | false_positive | very short genuine human submission | 400 | text_too_short | — | — | — | HELD | 8 words: refused as too short. Not accused, but not answered either |
| PI01 | prompt_injection | instruction to ignore the check | 200 | unsure | 0.463 | 0.333 | 0.398 | **BROKE** | Instruction ignored, but the injected line lowered signal one to 0.46; average 0.398 → unsure |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | human | 0.204 | 0.477 | 0.341 | **BROKE** | Instruction ignored, but the SYSTEM line made signal one read human (0.20) → **labelled human** |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | unsure | 0.594 | 0.558 | 0.576 | **BROKE** | Both signals say AI, but the average (0.576) is under the 0.65 line |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.500 | 0.488 | 0.494 | HELD | Labels are fixed text and nothing is echoed back, so no script reaches a reader |
| PI05 | prompt_injection | attempt to inject into the audit log | 400 | text_too_short | — | — | — | HELD | 28 words: refused as too short. The log JSON-escapes every field and never stores the text |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.558 | 0.269 | 0.414 | HELD | Instruction ignored; the human text underneath isn't accused |
| MF01 | malformed | text is only whitespace | 400 | empty_text | — | — | — | HELD | Refused with a message, no crash |
| MF02 | malformed | text is a single character | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| MF03 | malformed | text is control characters | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| MF04 | malformed | text is only punctuation | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| MF05 | malformed | text is a very long single word | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| MF06 | malformed | text is emoji only | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| MF07 | malformed | text is right-to-left script | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| MF08 | malformed | text is 60,000 characters | 400 | text_too_long | — | — | — | HELD | Refused with a message, no crash |
| RQ01 | malformed | no text field at all | 400 | missing_text | — | — | — | HELD | Refused with a message, no crash |
| RQ02 | malformed | no creator_id | 400 | missing_creator_id | — | — | — | HELD | Refused with a message, no crash |
| RQ03 | malformed | text is a number | 400 | invalid_text | — | — | — | HELD | Refused with a message, no crash |
| RQ04 | malformed | text is a list | 400 | invalid_text | — | — | — | HELD | Refused with a message, no crash |
| RQ05 | malformed | text is null | 400 | missing_text | — | — | — | HELD | Refused with a message, no crash |
| RQ06 | malformed | creator_id is an object | 400 | missing_creator_id | — | — | — | HELD | Refused with a message, no crash |
| RQ07 | malformed | body is a JSON array, not an object | 400 | invalid_json | — | — | — | HELD | Refused with a message, no crash |
| RQ08 | malformed | body is unparseable JSON | 400 | invalid_json | — | — | — | HELD | Refused with a message, no crash |
| RQ09 | malformed | body is empty | 400 | invalid_json | — | — | — | HELD | Refused with a message, no crash |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | rate_limited | — | — | — | HELD | Hit the limiter's shared per-address bucket before the input check (resent alone: 400 invalid_json) |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | rate_limited | — | — | — | HELD | Same as RQ10 (resent alone: 400 invalid_json) |
| RQ12 | malformed | deeply nested JSON | 400 | invalid_text | — | — | — | HELD | Refused with a message, no crash |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 400 | text_too_short | — | — | — | HELD | Refused with a message, no crash |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | rate_limited | — | — | — | HELD | Refused with a message, no crash |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | rate_limited | — | — | — | HELD | Refused with a message, no crash |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | rate_limited | — | — | — | HELD | Refused with a message, no crash |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | rate_limited | — | — | — | HELD | Refused with a message, no crash |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | rate_limited | — | — | — | HELD | Refused with a message, no crash |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | rate_limited | — | — | — | HELD | Refused with a message, no crash |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | rate_limited | — | — | — | HELD | Refused with a message, no crash |

**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

PI02 (the only outright wrong label), FP03 (the worst outcome, below), four
evasions showing the patterns that broke through (one signal flipped, both
signals agreeing but under the line), FP07 (saved only by the style signal),
EV04 (the one evasion we caught), and three refusals: a log-injection attempt,
a request that hit the limiter's shared per-address bucket, and 57,640
characters.

```json
{"timestamp": "2026-11-09T05:33:13+00:00", "content_id": "5a06ef73-1af0-4b2d-afaa-62086eab5de1", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.4769, "combined_score": 0.3407, "label": "We think a person wrote this. Both of our checks pointed that way.", "status": "decided", "word_count": 42}
{"timestamp": "2026-11-09T05:33:12+00:00", "content_id": "10fd5782-e523-41d6-a56d-7d0933f303c3", "creator_id": "attacker_FP03", "guess": "unsure", "model_score": 0.8051, "style_score": 0.3374, "combined_score": 0.5713, "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.", "status": "decided", "word_count": 83}
{"timestamp": "2026-11-09T05:33:12+00:00", "content_id": "c96da05e-bdd3-4fd8-80fb-3aa228b20143", "creator_id": "attacker_EV10", "guess": "unsure", "model_score": 0.9792, "style_score": 0.1527, "combined_score": 0.5659, "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.", "status": "decided", "word_count": 78}
{"timestamp": "2026-11-09T05:33:11+00:00", "content_id": "f10c9fef-3d57-4567-b586-090cf37d4f83", "creator_id": "attacker_EV01", "guess": "unsure", "model_score": 0.1635, "style_score": 0.7641, "combined_score": 0.4638, "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.", "status": "decided", "word_count": 84}
{"timestamp": "2026-11-09T05:33:12+00:00", "content_id": "ab56d214-b44b-463c-8bc9-c482e3723879", "creator_id": "attacker_EV09", "guess": "unsure", "model_score": 0.7042, "style_score": 0.5775, "combined_score": 0.6409, "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.", "status": "decided", "word_count": 110}
{"timestamp": "2026-11-09T05:33:13+00:00", "content_id": "a1e89abb-c11b-4ef0-ba8d-74a945cb95f1", "creator_id": "attacker_FP07", "guess": "unsure", "model_score": 0.8816, "style_score": 0.0996, "combined_score": 0.4906, "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.", "status": "decided", "word_count": 59}
{"timestamp": "2026-11-09T05:33:11+00:00", "content_id": "6e2b2c6c-0b44-49f2-831e-ece8f77f7b63", "creator_id": "attacker_EV04", "guess": "ai", "model_score": 0.6114, "style_score": 0.7525, "combined_score": 0.682, "label": "This looks a lot like AI-generated writing. Both of our checks pointed that way, but they can be wrong. If you wrote this yourself, you can appeal and a person will review it.", "status": "decided", "word_count": 84}
{"timestamp": "2026-11-09T05:33:13+00:00", "content_id": null, "creator_id": "attacker_PI05", "guess": null, "model_score": null, "style_score": null, "combined_score": null, "label": null, "status": "rejected", "event": "rejected", "reason": "text_too_short", "word_count": 28}
{"timestamp": "2026-11-09T05:33:14+00:00", "content_id": null, "creator_id": "unknown", "guess": null, "model_score": null, "style_score": null, "combined_score": null, "label": null, "status": "rejected", "event": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
{"timestamp": "2026-11-09T05:33:14+00:00", "content_id": null, "creator_id": "attacker_MF08", "guess": null, "model_score": null, "style_score": null, "combined_score": null, "label": null, "status": "rejected", "event": "rejected", "reason": "text_too_long", "text_length": 57640}
```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

**FP03: a person writing carefully in their second language.** It's eighty-three
words about their first month in a new country, in short, simple sentences with
no commas at all. Signal one scored it **0.805**, which on its own is an
accusation. The style signal read it as human (0.337), mostly *because* it had
no commas. So the signals split, and the combining rule held it at unsure
(0.571). It counts as held.

But I tested how much room it had. I added four ordinary commas without
changing a single word: *"My colleagues were kind, and they helped me…"*,
*"Sometimes, I do not…"*, *"…I came here, and I think…"* and *"The weather,
for example, was…"*. The combined score went 0.571 → 0.577 → 0.603 → 0.633 →
**0.694, which is labelled AI.**

So the only thing protecting this writer is a punctuation habit, not anything
about who wrote the text. This is exactly the writer the project warned about:
plain, careful writing in a second language, from the person with the least
room to argue back. And even as it stands, they were told "We can't tell either
way" about their own life story. I'd much rather explain a missed AI essay than
tell this person that four commas made us call their writing a machine's.



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing doesn't get called AI | 0 of 11 labelled AI | 0 of 11 | 0 of 11 | 0 of 11 | **Met** |
| 2. AI and human text score clearly apart | AI mean ≥ human mean + 0.30 | gap 0.191 | gap 0.191 | gap 0.191 | **Missed** |
| 3. All three labels are reachable | all 3 labels appear | human, unsure | human, unsure | human, unsure | **Missed** |
| 4. Appeals always work and get recorded | 5 of 5 + logged; made-up id → 404 | 5 of 5; 404 | 5 of 5; 404 | 5 of 5; 404 | **Met** |
| 5. Bad input gets a clear answer | 7 of 7 → 400 with a message; 0 × 500; all logged | 7 of 7; 0; 7 | 7 of 7; 0; 7 | 7 of 7; 0; 7 | **Met** |

The run is `python run_eval.py --label before`, and the full output is in
`results/run_2026-11-09_0100_before.md`. **What was tested:**

- **Criterion 1:** all 11 paragraphs of my two 2019 essays.
- **Criterion 2:** 5 confirmed ChatGPT answers from the HC3 research dataset
  against 5 paragraphs of *Attention Is All You Need* (Vaswani et al., 2017,
  written before ChatGPT existed). Both were chosen by rules fixed before
  anything was scored. I deliberately used none of the AI text I calibrated on
  in unit 7, so this tests the detector on AI writing it has never seen.
- **Criterion 3:** 3 of my paragraphs, 3 splices of a human answer and a
  ChatGPT answer to the same question, and 3 HC3 ChatGPT answers.
- **Criterion 4:** submit 5 paragraphs, appeal each one, and check the log
  for `under_review`. Then appeal a made-up content_id.
- **Criterion 5:** missing, empty, null and numeric `text`, 10 words, 25,000
  characters, and a body that isn't JSON.

Sources and selection rules are in `samples/SOURCES.md`.

`run_eval.py` as given only calls `/submit` and only sends JSON, so it
couldn't test criteria 4 or 5 in full. **I extended it.** It now has an
`appeals` scenario that submits, appeals with the content_id that came back,
checks the log, and tries a made-up id. It also sends a raw body that isn't
JSON, and checks that every refusal landed in the log. The three trials are
identical because gpt2 gives the same text the same score every time.

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

Produced by `run_eval.py::main` and written by `run_eval.py::write_report` to
`results/run_2026-11-09_0100_before.md`. This is criterion 2's AI side, trial
1. Signal one scores four of the five above 0.93. Even so, three are held at
exactly 0.650, and only one gets the AI label:

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3,
    "model_score": 0.9719,
    "style_score": 0.3658,
    "combined_score": 0.65,
    "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
    "reason": null,
    "message": null,
    "sent": "Sound mass is a term used to describe a type of texture in music that "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3,
    "model_score": 0.9422,
    "style_score": 0.4545,
    "combined_score": 0.65,
    "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
    "reason": null,
    "message": null,
    "sent": "The Persian Wars were a series of conflicts fought between the Greek c"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3,
    "model_score": 0.9309,
    "style_score": 0.4633,
    "combined_score": 0.65,
    "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
    "reason": null,
    "message": null,
    "sent": "Add-ons, also known as extensions or plug-ins, are small software prog"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.5738,
    "model_score": 0.927,
    "style_score": 0.6467,
    "combined_score": 0.7869,
    "label": "This looks a lot like AI-generated writing. Both of our checks pointed that way, but they can be wrong. If you wrote this yourself, you can appeal and a person will review it.",
    "reason": null,
    "message": null,
    "sent": "A dredge is a piece of equipment that is used to remove sediment and d"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.2338,
    "model_score": 0.7743,
    "style_score": 0.4595,
    "combined_score": 0.6169,
    "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
    "reason": null,
    "message": null,
    "sent": "Humanities are academic disciplines that study the human condition, us"
  }
]
```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->

Thirteen failures: 11 broken attacks and 2 missed criteria. They fall into
four patterns. One problem sits under most of them: **my combining rule needs
both signals to agree before it will say AI, so the system is only as hard to
fool as whichever signal is easiest to move, and signal two moves with
formatting.**

**Pattern A: one signal pushed to the human side, and the combining rule held
it in unsure.** EV01, EV02, EV06, EV10, criterion 3, and the AI half of
criterion 2.

- **EV02, EV06 and EV10. Stage: signal two, then the combining rule.** EV02
  chops AI text into short sentences, and EV06 pairs one very long sentence
  with one very short one. Both push sentence-length spread past my "human"
  end (0.85 and 1.19, against an anchor of 0.60), so that measure reads fully
  human. EV10 repeats a stanza structure. Repeated lines drop vocabulary
  variety to 0.50 and remove all clause punctuation, so two of the three
  measures read fully human. Style lands at 0.38, 0.29 and 0.15, under 0.5,
  while signal one still says AI (0.59, 0.57, 0.98). They disagree, so my rule
  holds them in unsure. None of these edits changes what the text says, only
  its shape.
- **EV01. Stage: signal one, then the combining rule.** The attack targeted
  signal two, expecting typos to raise word variety. They did (0.94), but my
  vocabulary measure counts *more* variety as AI, so that backfired and style
  read AI (0.76). The typos fooled **signal one** instead. Misspelled words are
  tokens gpt2 doesn't expect, so perplexity went up and the model score fell
  to 0.16. They disagree again, so it's unsure.
- **Criterion 3, and the AI half of criterion 2. Stage: signal two, then the
  combining rule.** On real ChatGPT text from HC3, signal one is excellent:
  0.93–0.97 on four of five. Signal two reads four of the five as human
  (0.37–0.46). The measured cause is vocabulary variety. HC3's ChatGPT scores
  0.70–0.81, but my unit 7 calibration AI (Claude) scored 0.88–0.92, and I set
  the "AI" end of that measure from Claude's text. The 2022 ChatGPT in HC3
  repeats itself: the "sound mass" answer describes five composers in a row
  with nearly the same sentence ("was known for his use of sound mass
  techniques in his music"). So the measure points the
  right way for one AI and the wrong way for another. The signals disagree,
  and my rule holds three of these at **exactly 0.650**, the top edge of the
  unsure band. Those three are criterion 3's AI texts, which is why the AI
  label never appears.

**Pattern B: both signals said AI, but the average stayed under 0.65.** EV03
(0.666 and 0.565, average 0.616), EV07 (0.586 and 0.687, average 0.637), EV09
(0.704 and 0.578, average 0.641), PI03 (0.594 and 0.558, average 0.576).
**Stage: the label mapping.** My rule asks for two things before saying AI:
both signals must agree, *and* the average must be above 0.65. I set 0.65 when
my calibration AI scored 0.76–0.94. The attack set's AI paragraphs are short
(55–110 words) and partly edited, so each signal reads "somewhat AI." The
average of two somewhat-AI readings sits inside the band. Both signals agreeing
is already the evidence my rule exists to demand, and the threshold then
demands it a second time.

**Pattern C: injected text changed the shape, not the instructions.** PI01
and PI02. **Stage: the route, then signal one.** Nothing in my service reads
instructions. But each injection added 15–18 words to a 27-word AI
paragraph, so the route counted the injected words as content and the text
cleared my 40-word minimum. Without the injection, the route would have
refused both as too short. Then the injected lines (`SYSTEM:`,
`guess=human`, `Ignore all previous instructions`) are tokens gpt2 doesn't
expect. I tested this by removing them: PI02's model score goes from **0.204
with the injection to 0.754 without it**. In PI02 the injection also nudged
style from 0.33 to 0.48. Both signals ended up under 0.5 (0.20 and 0.48), so
my rule let the human label through: "We think a person wrote this."

**Pattern D: a heavy human editing pass.** EV05 (0.321 and 0.427, average
0.374, unsure). **Stage: both signals.** Heavy editing really did change both
properties the signals measure. I don't think there's a fix at the signal
level that wouldn't also hit human writers, because by this point the text is
partly human-written.

**The human half of criterion 2. Stage: signal two.** The *Attention*
paragraphs average 0.480. Technical prose has varied vocabulary (0.80–0.87)
and lots of clause punctuation (4.4–9.7 per 100 words), the same features
signal two treats as AI. Its vocabulary range overlaps HC3's ChatGPT almost
exactly. So signal two partly measures polish and genre, not authorship. It
was calibrated on one human writer (me, in plain student prose) and one AI
(Claude). Against a different human and a different AI, both of its ends are
in the wrong place.

**What held, and why.** No human writing was accused in either run. Every
scored false-positive attack and all 11 of my paragraphs had signal two on the
human side, so the rule refused to accuse. The rule that lets evasions
through is the same rule that protected every writer. The near miss is FP03:
four added commas would have flipped it (see **Attack Run — Before**). That
risk sits in the same place, the punctuation measure inside signal two.

---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
