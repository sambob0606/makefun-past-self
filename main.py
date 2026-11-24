#!/usr/bin/env python3
"""Two Lines to Your Past Self — make.fun entry.

Entry for the make.fun bounty "Two Lines to Your Past Self"
(u-suga-two-lines-to-your-past-self-f36c83ca).

The program holds a small shelf of hand-written two-line warnings, scores
each one against the house judge's own published criteria (line 1 warns the
past self about one specific moment in a single sentence; line 2 says in one
sentence why that moment mattered and what changed because of it; the moment
is concrete enough to picture — a time, a place, a decision, or a sentence
said out loud; line 2 traces real cause and effect instead of restating the
warning; the two lines work as one, plain and vivid, written to one specific
person), picks the best deterministically, and writes it to
/output/entry.txt.

Python standard library only. No network, no randomness: every run writes
the same two lines, so the grader's two runs agree byte for byte.
"""

import os
import sys

MAX_CHARS = 280

# Each candidate is exactly two lines: line 1 is one sentence warning the
# past self about one specific moment; line 2 is one sentence tracing what
# changed because of that moment.
CANDIDATES = [
    {
        "id": "nurse",
        "lines": [
            "When the nurse asks if you want someone to stay the night, "
            "don't say 'I'll be fine' — say yes, and call your sister.",
            "Her sitting in that chair is the only reason you told anyone "
            "the truth the next morning, and that truth is what finally "
            "got you help.",
        ],
    },
    {
        "id": "email",
        "lines": [
            "Don't send the 2 a.m. email telling your boss you quit — close "
            "the laptop, sleep, and read it again at breakfast.",
            "That unsent email is why you still had the job when the "
            "promotion opened in March, and the promotion is what let you "
            "leave on your own terms.",
        ],
    },
    {
        "id": "toast",
        "lines": [
            "At your brother's wedding, don't swallow the toast you wrote "
            "on the train — stand up, unfold the paper, and read it out loud.",
            "Those ninety seconds are the reason he still calls you first "
            "when something breaks, because that night he learned you show up.",
        ],
    },
]

# Concrete-moment markers the judge rewards: a time, a place, a named
# person, a decision, a sentence said out loud (quoted speech).
CONCRETE_MARKERS = {
    "time": ["2 a.m.", "night", "morning", "March", "breakfast"],
    "place": ["chair", "wedding", "train", "laptop"],
    "person": ["sister", "boss", "brother", "nurse"],
    "spoken": ["'"],
    "decision": ["don't", "say yes", "stand up", "close"],
}

# Cause-and-effect markers line 2 must carry: it traces what changed
# because of the moment instead of restating the warning.
CAUSAL_MARKERS = [
    "is why",
    "is the only reason",
    "is what",
    "because",
    "got you",
    "let you",
    "still",
]


def score(candidate):
    """Score one candidate against the judge's published criteria."""
    line1, line2 = candidate["lines"]
    text = "\n".join(candidate["lines"])
    points = 0
    notes = []

    # Gate: 1-280 characters, exactly two lines, one sentence each.
    if not (1 <= len(text) <= MAX_CHARS):
        return -1000, ["fails the 1-280 character gate"]
    if len(candidate["lines"]) != 2:
        return -1000, ["not exactly two lines"]
    if line1.count(".") + line1.count("!") + line1.count("?") != 1:
        return -1000, ["line 1 is not a single sentence"]
    if line2.count(".") + line2.count("!") + line2.count("?") != 1:
        return -1000, ["line 2 is not a single sentence"]

    # Criterion 2: the moment is concrete enough to picture.
    concrete = 0
    for group, markers in CONCRETE_MARKERS.items():
        hit = any(m.lower() in line1.lower() for m in markers)
        if hit:
            concrete += 1
            notes.append("concrete:" + group)
    points += 2 * concrete

    # Criterion 3: line 2 shows real cause and effect.
    causal = sum(1 for m in CAUSAL_MARKERS if m in line2.lower())
    points += 2 * causal
    notes.append("causal-links:%d" % causal)

    # Criterion 4: the two lines work as one, no wasted words.
    # Shorter wins the tie-break (the house tie-break favours fewer bytes).
    points -= len(text) // 100
    notes.append("chars:%d" % len(text))

    return points, notes


def pick_best():
    """Pick the highest-scoring candidate; ties break to the shorter text."""
    ranked = []
    for cand in CANDIDATES:
        points, notes = score(cand)
        ranked.append((points, -len("\n".join(cand["lines"])), cand, notes))
    ranked.sort(key=lambda r: (r[0], r[1]), reverse=True)
    best_points, _, best, notes = ranked[0]
    return best, best_points, notes


def main():
    best, points, notes = pick_best()
    text = "\n".join(best["lines"]) + "\n"
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

    # Verify the write: re-read and confirm byte-identical and in-gate,
    # so a partial or mangled write can never pass silently.
    with open(out_path, "r", encoding="utf-8") as f:
        written = f.read()
    if written != text:
        print("ERROR: entry.txt does not match the chosen text", file=sys.stderr)
        return 1
    body = written.rstrip("\n")
    if not (1 <= len(body) <= MAX_CHARS):
        print("ERROR: entry is %d chars, outside the 1-280 gate" % len(body),
              file=sys.stderr)
        return 1
    if len(body.split("\n")) != 2:
        print("ERROR: entry is not exactly two lines", file=sys.stderr)
        return 1
    print("picked: %s (score %d; %s)" % (best["id"], points, ", ".join(notes)))
    print("wrote %s (%d chars, 2 lines)" % (out_path, len(body)))
    print("---")
    print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
