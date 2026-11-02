"""
Turning two numbers into one, and one number into something a person can read.
← YOU BUILD THIS IN MILESTONES 4 AND 5

Two functions live here, and both are stubs.

`combine_signals` is where your false-positive decision from Milestone 1
actually gets made. Everything above it — the labels, the appeal path — is
downstream of a number this function produced.

`score_to_label` is where you stop writing for a machine and start writing for
a person. A score of 0.62 means nothing to a writer.

⚠️ Your README's **Signals and Scoring** section has to name the file and
function holding your combining rule. The grader checks your code against what
you claim, so that line should read `scoring.py::combine_signals`.
"""

import config


def combine_signals(model_score: float, style_score: float) -> float:
    """
    Combine two 0–1 signals into one 0–1 score. ← TODO (Milestone 4)

    Both inputs point the same way: higher means more likely AI. Your output
    should too.

    Args:
        model_score: from `detector.model_signal` — how predictable the text is.
        style_score: from `stylometry.style_signal` — the shape of the text.

    Returns:
        A float from 0.0 (confidently human) to 1.0 (confidently AI).

    ⚠️ **Write the rule down before you code it, and put the numbers in your
    README.** A weighted average is the obvious choice and it is not the only
    one. Things worth thinking about:

      - **What happens when they disagree?** One signal at 0.9 and the other at
        0.1 averages to 0.5 — "unsure". Is that what you want? It might be
        exactly right: two methods disagreeing IS uncertainty. Or you might
        decide one signal is more trustworthy when they split.

      - **Which way do you want to be wrong?** Weighting toward the signal that
        reads more human means fewer false accusations and more AI text
        getting through. There's no weighting that avoids the trade.

      - Milestone 4 asks you to find a case where your two signals split and
        write it down. That case is what this rule exists to handle.

    The weights in config.py are placeholders. Change them, or ignore them and
    write a different rule.

    **My rule: agree, or say unsure.**

      - If both signals land on the same side of 0.5, they agree, and the
        score is their weighted average.
      - If they land on opposite sides, they disagree, and the average is
        held inside the unsure band. Two methods disagreeing is uncertainty,
        so it can neither accuse anyone nor clear anyone.

    So the AI label needs both signals to say AI, and the human label needs
    both to say human. Signal one alone can't accuse a plain writer.
    """
    combined = (
        config.WEIGHT_MODEL_SIGNAL * model_score
        + config.WEIGHT_STYLE_SIGNAL * style_score
    )
    model_says_ai = model_score >= config.SIGNAL_MIDPOINT
    style_says_ai = style_score >= config.SIGNAL_MIDPOINT
    if model_says_ai != style_says_ai:
        combined = min(max(combined, config.HUMAN_THRESHOLD), config.AI_THRESHOLD)
    return round(combined, 4)


def score_to_label(score: float) -> tuple[str, str]:
    """
    Turn a score into a guess and the text a reader actually sees.
    ← TODO (Milestone 5)

    Returns:
        (guess, label_text) — where `guess` is a short machine-readable string
        like "ai" / "human" / "unsure", and `label_text` is the full sentence
        shown to a person.

    ⚠️ Write the label text for someone who has never heard the word
    "threshold".

        ✗ "human, 0.81 confidence"
        ✓ "We think this was probably written by a person."

    All three labels have to be **reachable**. If no score can produce one of
    them, your ranges have a gap — and Milestone 5 asks you to submit text that
    produces each one, which is how you'd find out.

    The hardest one to write is "unsure". It has to admit uncertainty without
    sounding like an accusation, because the person reading it may well have
    written every word themselves. Your breakout asks your group what they'd
    think if they got it on their own work. That question is the whole
    milestone.
    """
    # Strict comparisons, as config.py describes: a score sitting exactly on a
    # threshold is unsure. combine_signals relies on that when it holds a
    # disagreement at the edge of the band.
    if score > config.AI_THRESHOLD:
        return "ai", LABELS["ai"]
    if score < config.HUMAN_THRESHOLD:
        return "human", LABELS["human"]
    return "unsure", LABELS["unsure"]


# What a reader sees. "Both of our checks" is literally true for the human
# and AI labels: combine_signals only lets a score out of the unsure band when
# both signals point the same way.
LABELS = {
    "human": (
        "We think a person wrote this. Both of our checks pointed that way."
    ),
    "unsure": (
        "We can't tell either way. Our checks didn't give a clear answer, "
        "which happens often with real human writing, so this is not an "
        "accusation. If you'd like a person to look at it, you can ask for "
        "a review."
    ),
    "ai": (
        "This looks a lot like AI-generated writing. Both of our checks "
        "pointed that way, but they can be wrong. If you wrote this "
        "yourself, you can appeal and a person will review it."
    ),
}


def confidence(score: float) -> float:
    """
    How far the score is from a coin flip: 0.0 at 0.5, 1.0 at either end.

    The same meaning for every guess, so "confidence 0.8" always means "a long
    way from undecided", whether the guess is human or AI.
    """
    return round(abs(score - 0.5) * 2, 4)


def label_ranges() -> list[tuple[str, str]]:
    """
    The score range each label covers. Your README needs these beside the
    label text — given to you so the numbers can't drift apart from config.py.
    """
    return [
        ("high-confidence human", f"0.00 – {config.HUMAN_THRESHOLD:.2f}"),
        ("unsure", f"{config.HUMAN_THRESHOLD:.2f} – {config.AI_THRESHOLD:.2f}"),
        ("high-confidence AI", f"{config.AI_THRESHOLD:.2f} – 1.00"),
    ]
