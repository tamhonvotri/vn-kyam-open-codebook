#!/usr/bin/env python3
"""
Apply a Vietnamese-variety codebook's respelling_rules to text (machine-readable dialect respelling).

Example:
  python3 tools/apply_respelling.py --codebook codebooks/vietnamese/vie-south.json --level light \
      "Trăng ơi buồn nhớ ai, cũ kỹ mãi say"
  python3 tools/apply_respelling.py --codebook codebooks/vietnamese/vie-south.json --level full --ipa-free < lyrics.txt

Levels: "light" applies only rules marked level=light (tokenizer-safe);
        "full"  applies light + full rules; add --include-optional to also apply optional rules.
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

TONE_MARKS = {"\u0300": "huyen", "\u0301": "sac", "\u0309": "hoi", "\u0303": "nga", "\u0323": "nang"}
TONE_TO_MARK = {v: k for k, v in TONE_MARKS.items()}
TONE_TO_MARK["ngang"] = ""

ONSETS = ["ngh", "ng", "nh", "ch", "tr", "th", "ph", "kh", "gh", "gi", "qu",
          "b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "r", "s", "t", "v", "x"]
MODIFIED_VOWELS = set("âăêôơư")
VOWELS = set("aăâeêioôơuưy")
CODAS = {"", "c", "ch", "m", "n", "ng", "nh", "p", "t"}
WORD_RE = re.compile(r"[A-Za-zÀ-ỹĐđ]+", re.UNICODE)
TAG_RE = re.compile(r"(\[[^\]]*\])")


def split_tone(word: str):
    nfd = unicodedata.normalize("NFD", word)
    tone = "ngang"
    base = []
    for ch in nfd:
        if ch in TONE_MARKS:
            tone = TONE_MARKS[ch]
        else:
            base.append(ch)
    return unicodedata.normalize("NFC", "".join(base)), tone


def parse(word_lower: str):
    """Return (onset, rhyme, tone) or None if not a Vietnamese syllable."""
    base, tone = split_tone(word_lower)
    onset = ""
    for o in ONSETS:
        if base.startswith(o):
            onset = o
            break
    rhyme = base[len(onset):]
    # 'gi' + consonant-only rhyme (e.g. 'gì' -> base 'gi'): keep i as rhyme
    if onset == "gi" and (rhyme == "" or rhyme[0] not in VOWELS):
        onset, rhyme = "g", base[1:]
    if not rhyme or rhyme[0] not in VOWELS:
        return None
    i = 0
    while i < len(rhyme) and rhyme[i] in VOWELS:
        i += 1
    if i > 3 or rhyme[i:] not in CODAS:
        return None
    return onset, rhyme, tone


def place_tone(onset: str, rhyme: str, tone: str) -> str:
    if tone == "ngang":
        return onset + rhyme
    mark = TONE_TO_MARK[tone]
    vowel_idx = [i for i, c in enumerate(rhyme) if c in VOWELS]
    # the vowel nucleus is the leading vowel run
    run = []
    for i in vowel_idx:
        if not run or i == run[-1] + 1:
            run.append(i)
        else:
            break
    has_coda = len(rhyme) > (run[-1] + 1)
    target = None
    mods = [i for i in run if rhyme[i] in MODIFIED_VOWELS]
    if mods:
        target = mods[-1]  # ươ->ơ, iê->ê, uô->ô, uâ->â, ưa->ư
    elif len(run) == 1:
        target = run[0]
    elif has_coda:
        target = run[-1]
    else:
        first_two = rhyme[run[0]:run[0] + 2]
        glide_first = first_two in ("oa", "oe", "uy") or onset == "qu"
        target = run[1] if (glide_first and len(run) >= 2) else run[0]
        if len(run) == 3:
            target = run[1]
    s = rhyme[:target + 1] + mark + rhyme[target + 1:]
    return onset + unicodedata.normalize("NFC", s)


def match_case(src: str, dst: str) -> str:
    if src.isupper() and len(src) > 1:
        return dst.upper()
    if src[:1].isupper():
        return dst[:1].upper() + dst[1:]
    return dst


class Respeller:
    def __init__(self, codebook: dict, level: str, include_optional: bool):
        rules = codebook.get("respelling_rules", [])
        for r in rules:
            if "level" not in r:
                r["level"] = "light" if "[light]" in (r.get("note") or "") else "full"
        allowed = {"light"} if level == "light" else {"light", "full"}
        self.rules = [r for r in rules
                      if r.get("level", "full") in allowed and (include_optional or not r.get("optional"))]
        self.word_rules = {r["from"]: r["to"] for r in self.rules if r["slot"] == "word"}
        self.onset_rules = [r for r in self.rules if r["slot"] == "onset"]
        self.rhyme_rules = [r for r in self.rules if r["slot"] == "rhyme"]
        self.tone_rules = {r["from"]: r["to"] for r in self.rules if r["slot"] == "tone"}

    def word(self, w: str) -> str:
        lw = w.lower()
        if lw in self.word_rules:
            return match_case(w, self.word_rules[lw])
        p = parse(lw)
        if not p:
            return w
        onset, rhyme, tone = p
        for r in self.onset_rules:
            if onset == r["from"]:
                onset = r["to"]
                break
        base_rhyme = rhyme
        for r in self.rhyme_rules:
            if base_rhyme == r["from"]:
                rhyme = r["to"]
                break
        tone = self.tone_rules.get(tone, tone)
        out = place_tone(onset, rhyme, tone)
        if out in self.word_rules:
            out = self.word_rules[out]
        return match_case(w, out)

    def text(self, s: str) -> str:
        parts = TAG_RE.split(s)
        return "".join(p if TAG_RE.fullmatch(p) else WORD_RE.sub(lambda m: self.word(m.group(0)), p) for p in parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codebook", required=True, type=Path)
    ap.add_argument("--level", choices=["light", "full"], default="light")
    ap.add_argument("--include-optional", action="store_true")
    ap.add_argument("text", nargs="*")
    a = ap.parse_args()
    cb = json.loads(a.codebook.read_text(encoding="utf-8"))
    rs = Respeller(cb, a.level, a.include_optional)
    src = " ".join(a.text) if a.text else sys.stdin.read()
    sys.stdout.write(rs.text(src) + ("" if src.endswith("\n") else "\n"))


if __name__ == "__main__":
    main()
