"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies. ← TODO

    Returns:
        A float. Decide yourself what scale it's on and which direction means
        "more human" — then write that down, because your combining rule
        depends on knowing it.

    A hint on what you're reaching for: the standard deviation of sentence
    lengths, probably divided by the mean so a long text and a short one are
    comparable. `statistics.stdev` is imported for you.

    Watch the edge case: a one-sentence submission has no spread at all, and
    `stdev` raises on fewer than two values. Decide what that should return
    before the attack set decides for you.

    My version: standard deviation of sentence lengths (in words) divided by
    the mean. **Higher means more human.** Fewer than two sentences returns
    0.0, and `style_signal` treats that case as "no evidence" rather than as
    AI.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return 0.0
    return statistics.stdev(lengths) / statistics.mean(lengths)


TTR_WINDOW = 50


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words.

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    Worth knowing before you rely on it: this measure falls as text gets
    longer, because common words repeat. Two texts of different lengths aren't
    directly comparable on it, and if your test inputs vary a lot in length,
    that alone can look like a signal.

    My version fixes the length problem by measuring the ratio in every
    50-word window and averaging them (a "moving-average type-token ratio").
    A 150-word text and a 400-word one are then on the same scale. Texts
    shorter than one window fall back to the plain ratio.

    **Higher means more AI.** This is the opposite of what I expected. In my
    calibration, AI paragraphs scored 0.88–0.92 and my own essays 0.72–0.83:
    modern models swap in synonyms, and plain human writing repeats its key
    terms.
    """
    w = words(text)
    if not w:
        return 0.0
    if len(w) <= TTR_WINDOW:
        return len(set(w)) / len(w)
    windows = range(len(w) - TTR_WINDOW + 1)
    return statistics.mean(len(set(w[i:i + TTR_WINDOW])) / TTR_WINDOW for i in windows)


# Punctuation that joins clauses: commas, semicolons, colons, en and em dashes.
# Not hyphens inside words, and not quotation marks — those track citations,
# not style.
CLAUSE_PUNCTUATION = re.compile(r"[,;:–—]")


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to length.

    Returns:
        A float. Whether you count all punctuation or only some kinds — commas,
        semicolons, dashes — is a real choice. Semicolons and em dashes are
        more interesting than full stops, because they vary more between
        writers.

    My version: clause-joining marks (, ; : – —) per 100 words. **Higher means
    more AI.** AI prose is full of "X, Y, and Z" lists and stacked clauses. It
    scored 6.8–12.1 per 100 words in calibration, and my essays 1.0–3.2.
    Parentheses and quotation marks are left out on purpose: my essays use
    them for citations, and counting them would make my own writing look
    more like AI.
    """
    w = words(text)
    if not w:
        return 0.0
    return 100 * len(CLAUSE_PUNCTUATION.findall(text)) / len(w)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.** ← TODO

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Which direction each measure points. Low spread means more AI-ish, so
         it needs flipping. Work out which of your three need that.
      2. How to get each onto a comparable scale. A raw type-token ratio sits
         between 0 and 1; a raw punctuation count doesn't. Adding them
         unscaled means whichever has the bigger numbers wins by default.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.

    My version: each measure is put on a 0–1 ramp between a "human" end and an
    "AI" end (see ANCHORS), then the three are averaged with equal weight.
    The ends are round numbers just outside where my calibration texts landed.
    """
    parts = [
        _ramp(type_token_ratio(text), *ANCHORS["type_token_ratio"]),
        _ramp(punctuation_density(text), *ANCHORS["punctuation_density"]),
    ]
    # One sentence has no spread to measure. That's no evidence either way,
    # so it counts as neither human nor AI.
    if len(sentences(text)) >= 2:
        parts.append(_ramp(sentence_length_spread(text), *ANCHORS["sentence_length_spread"]))
    else:
        parts.append(0.5)
    return round(sum(parts) / len(parts), 4)


# (human end, AI end) for each measure. A value at the human end scores 0.0,
# at the AI end 1.0, and anything past either end is clipped.
ANCHORS = {
    "sentence_length_spread": (0.60, 0.15),   # even sentences -> AI
    "type_token_ratio": (0.75, 0.92),         # more varied words -> AI
    "punctuation_density": (1.0, 9.0),        # more clause punctuation -> AI
}


def _ramp(value: float, human_end: float, ai_end: float) -> float:
    """Where `value` sits between the human end (0.0) and the AI end (1.0)."""
    position = (value - human_end) / (ai_end - human_end)
    return min(max(position, 0.0), 1.0)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
