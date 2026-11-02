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

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

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
