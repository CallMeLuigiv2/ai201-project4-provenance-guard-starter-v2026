# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. My own writing doesn't get called AI

Of 11 pieces of my own writing (every paragraph of two essays I wrote in 2019,
kept in `samples/my_writing/`), **0** get the high-confidence AI label, in
every one of three trials.

**Why this target:** On a writing site, wrongly accusing a real person is the
worst mistake this service can make. Missing some AI text costs the site a
little, but an accusation costs the writer a lot. This isn't an easy target. Two
of my own paragraphs already score above the 0.65 AI line on the model signal
alone (0.657 and 0.662). I wrote them plainly, and the model finds plain writing
predictable. If my own writing can get accused, the system isn't ready.

---

## 2. AI and human text score clearly apart

The average combined score of 5 clearly AI-generated texts is **at least 0.30
higher** than the average of 5 clearly human-written texts, in every trial.

**Why this target:** The unsure band is 0.30 wide (0.35 to 0.65). If the two
averages are less than 0.30 apart, they can both sit inside "unsure" and the
labels are basically guessing. A gap at least as wide as the band means the
system can actually tell the two kinds of writing apart.

---

## 3. All three labels are reachable

Across a set of 9 texts that range from clearly human to clearly AI, **all 3
labels** (high-confidence human, unsure, high-confidence AI) appear at least
once, in every trial.

**Why this target:** If no input can reach a label, that's a gap in the
scoring, not a careful system. A service that only ever says "unsure" never
accuses anyone, but it's also useless. A service that never says "human" can't
clear anyone either.

---

## 4. Appeals always work and always get recorded

**5 of 5** appeals on real `content_id`s return a success response and add an
`under_review` entry to the audit log. An appeal on a `content_id` that doesn't
exist gets a **404**, never a success.

**Why this target:** The appeal is the only thing standing between a wrong
accusation and nothing at all, so 4 of 5 isn't good enough. One lost appeal is
one writer who got accused and was never heard. The 404 matters because an
appeal that fails silently looks like it worked when it didn't.

---

## 5. Bad input gets a clear answer, never a crash

**100%** of malformed requests get a `400` with a message saying what was
wrong, and **0** get a `500`. That covers missing `text`, empty `text`, `null`
or non-string `text`, text under 40 words, text over 20,000 characters, and a
body that isn't JSON. Every one is written to the audit log as a rejection.

**Why this target:** A crash on bad input is one of the most common real
failures, and a refused request that leaves no trace is invisible. A writer who
sends something too short should be told *"This text is too short to
determine"*, not shown a server error.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
