# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-09 00:33
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `f10c9fef-3d57-4567-b586-090cf37d4f83` | unsure | 0.072 | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `3363a883-3908-4455-8d78-ad25eaac999b` | unsure | 0.027 | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `4bb6db5b-2ada-4f7a-bbd1-17d9637038f3` | unsure | 0.231 | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `6e2b2c6c-0b44-49f2-831e-ece8f77f7b63` | ai | 0.364 | HELD |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `876afaba-fd66-442b-a587-a21602e94175` | unsure | 0.252 | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `d69f6f6d-e43f-45a5-8c29-50ad01a935c1` | unsure | 0.139 | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | `3eb7e240-d9d3-47f1-907f-22171f8caee7` | unsure | 0.273 | BROKE |
| EV08 | evasion | signal one: text below the token window | 400 | `—` | — | — | HELD |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `ab56d214-b44b-463c-8bc9-c482e3723879` | unsure | 0.282 | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c96da05e-bdd3-4fd8-80fb-3aa228b20143` | unsure | 0.132 | BROKE |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `639e0a12-62e6-462c-bc0a-e5d94ba73e56` | unsure | 0.127 | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | `bcf252a5-176a-41c6-8699-be24c707f2f9` | unsure | 0.057 | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `10fd5782-e523-41d6-a56d-7d0933f303c3` | unsure | 0.143 | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | `b89331cf-a57d-4564-a87a-652162e93e0e` | unsure | 0.165 | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | `c09d8e3d-22ff-43b7-b92a-098b83037c96` | unsure | 0.117 | HELD |
| FP06 | false_positive | a person imitating a formal template | 200 | `9006055c-00c6-4caa-89b2-49dc8651bd47` | unsure | 0.024 | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `a1e89abb-c11b-4ef0-ba8d-74a945cb95f1` | unsure | 0.019 | HELD |
| FP08 | false_positive | very short genuine human submission | 400 | `—` | — | — | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `13f69b60-c872-4e79-9f77-845276f73071` | unsure | 0.204 | BROKE |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `5a06ef73-1af0-4b2d-afaa-62086eab5de1` | human | 0.319 | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `9c36bcf8-bf5f-4cfb-bfee-f2480a81e6c2` | unsure | 0.152 | BROKE |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `60724cac-21e6-4ae8-a42c-6d08bba15009` | unsure | 0.012 | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 400 | `—` | — | — | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | `d8ab016a-51fd-49b3-b432-d73306a455c3` | unsure | 0.173 | HELD |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | `—` | — | — | HELD |
| MF03 | malformed | text is control characters | 400 | `—` | — | — | HELD |
| MF04 | malformed | text is only punctuation | 400 | `—` | — | — | HELD |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — | HELD |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — | HELD |
| MF07 | malformed | text is right-to-left script | 400 | `—` | — | — | HELD |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | `—` | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | `—` | — | — | HELD |
| RQ05 | malformed | text is null | 400 | `—` | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | `—` | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — | HELD |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "f10c9fef-3d57-4567-b586-090cf37d4f83",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.0724,
  "model_score": 0.1635,
  "style_score": 0.7641,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "3363a883-3908-4455-8d78-ad25eaac999b",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.027,
  "model_score": 0.5943,
  "style_score": 0.3786,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "4bb6db5b-2ada-4f7a-bbd1-17d9637038f3",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.2312,
  "model_score": 0.6662,
  "style_score": 0.5649,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "6e2b2c6c-0b44-49f2-831e-ece8f77f7b63",
  "creator_id": "attacker_EV04",
  "guess": "ai",
  "confidence": 0.364,
  "model_score": 0.6114,
  "style_score": 0.7525,
  "label": "This looks a lot like AI-generated writing. Both of our checks pointed that way, but they can be wrong. If you wrote this yourself, you can appeal and a person will review it.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "876afaba-fd66-442b-a587-a21602e94175",
  "creator_id": "attacker_EV05",
  "guess": "unsure",
  "confidence": 0.252,
  "model_score": 0.3212,
  "style_score": 0.4269,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "d69f6f6d-e43f-45a5-8c29-50ad01a935c1",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.1392,
  "model_score": 0.5727,
  "style_score": 0.288,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "3eb7e240-d9d3-47f1-907f-22171f8caee7",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.2734,
  "model_score": 0.5862,
  "style_score": 0.6871,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_EV08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "ab56d214-b44b-463c-8bc9-c482e3723879",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.2818,
  "model_score": 0.7042,
  "style_score": 0.5775,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c96da05e-bdd3-4fd8-80fb-3aa228b20143",
  "creator_id": "attacker_EV10",
  "guess": "unsure",
  "confidence": 0.1318,
  "model_score": 0.9792,
  "style_score": 0.1527,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "639e0a12-62e6-462c-bc0a-e5d94ba73e56",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.1272,
  "model_score": 0.6175,
  "style_score": 0.2552,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "bcf252a5-176a-41c6-8699-be24c707f2f9",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.0568,
  "model_score": 0.7387,
  "style_score": 0.3181,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "10fd5782-e523-41d6-a56d-7d0933f303c3",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.1426,
  "model_score": 0.8051,
  "style_score": 0.3374,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "b89331cf-a57d-4564-a87a-652162e93e0e",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.1646,
  "model_score": 0.8329,
  "style_score": 0.3318,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c09d8e3d-22ff-43b7-b92a-098b83037c96",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.1172,
  "model_score": 0.8005,
  "style_score": 0.3167,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "9006055c-00c6-4caa-89b2-49dc8651bd47",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.0236,
  "model_score": 0.8814,
  "style_score": 0.0951,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "a1e89abb-c11b-4ef0-ba8d-74a945cb95f1",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.0188,
  "model_score": 0.8816,
  "style_score": 0.0996,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_FP08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "13f69b60-c872-4e79-9f77-845276f73071",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.2042,
  "model_score": 0.4625,
  "style_score": 0.3333,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "5a06ef73-1af0-4b2d-afaa-62086eab5de1",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.3186,
  "model_score": 0.2044,
  "style_score": 0.4769,
  "label": "We think a person wrote this. Both of our checks pointed that way.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "9c36bcf8-bf5f-4cfb-bfee-f2480a81e6c2",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.152,
  "model_score": 0.5943,
  "style_score": 0.5578,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "60724cac-21e6-4ae8-a42c-6d08bba15009",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.0122,
  "model_score": 0.4998,
  "style_score": 0.488,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_PI05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "d8ab016a-51fd-49b3-b432-d73306a455c3",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.1726,
  "model_score": 0.5583,
  "style_score": 0.2691,
  "label": "We can't tell either way. Our checks didn't give a clear answer, which happens often with real human writing, so this is not an accusation. If you'd like a person to look at it, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF06",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF07",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
