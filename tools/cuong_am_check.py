#!/usr/bin/env python3
"""
Phát hiện CƯỠNG ÂM (lệch thanh điệu – giai điệu) theo từng giọng vùng miền.

Ý tưởng: khi hát tiếng Việt, chữ nghe rõ khi hướng đi của giai điệu giữa hai nốt liền nhau
CÙNG CHIỀU với hướng đi của thanh điệu giữa hai chữ (similar motion). Ngược chiều (contrary motion)
dễ làm chữ bị nghe thành chữ khác — gọi là "cưỡng âm" / "gãy chữ". Cách đo theo hướng chuyển tiếp
dựa trên Kirby & Ladd (2016), "Tone-melody correspondence in Vietnamese popular song", TAL 2016.

Điểm mới: độ cao của mỗi thanh được lấy từ đường nét Chao (`phonology.tones[].chao_contour`) trong
bảng mã của TỪNG giọng (Hà Nội, Nghệ Tĩnh, Huế, Quảng, Nam Bộ...), nên cùng một giai điệu có thể
không bị cưỡng âm ở giọng này nhưng bị cưỡng âm ở giọng khác.

Đây là công cụ heuristic để gợi ý, không thay cho tai của nhạc sĩ.

Định dạng đầu vào (đơn giản): mỗi chữ kèm nốt, cách nhau bởi khoảng trắng:
    "trăng/E4 ơi/G4 buồn/E4 nhớ/A4 ai/G4"
Nốt: C4, D#4, Bb3... hoặc số MIDI (64). Chữ luyến nhiều nốt: "ai/G4-A4" (lấy nốt đầu để so với chữ trước,
nốt cuối để so với chữ sau).

Ví dụ:
  python3 tools/cuong_am_check.py --codebook codebooks/vietnamese/vie-north.json \
      --codebook codebooks/vietnamese/vie-central.json --codebook codebooks/vietnamese/vie-south.json \
      --plot docs/img/cuong_am_demo.png "trăng/E4 ơi/G4 buồn/E4 nhớ/A4 ai/G4"
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

TONE_MARKS = {"\u0300": "huyen", "\u0301": "sac", "\u0309": "hoi", "\u0303": "nga", "\u0323": "nang"}
NOTE_RE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d)$")
SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
TONE_NAME_VI = {"ngang": "ngang", "huyen": "huyền", "sac": "sắc", "hoi": "hỏi", "nga": "ngã", "nang": "nặng"}


def tone_of(word: str) -> str:
    for ch in unicodedata.normalize("NFD", word):
        if ch in TONE_MARKS:
            return TONE_MARKS[ch]
    return "ngang"


def is_checked(word: str) -> bool:
    base = unicodedata.normalize("NFD", word.lower())
    base = "".join(c for c in base if not unicodedata.combining(c))
    return base.endswith(("p", "t", "c", "ch"))


def note_to_midi(n: str) -> int:
    n = n.strip()
    if n.isdigit():
        return int(n)
    m = NOTE_RE.match(n)
    if not m:
        raise ValueError(f"Không đọc được nốt: {n}")
    letter, acc, octv = m.groups()
    v = SEMI[letter.upper()] + (1 if acc == "#" else -1 if acc == "b" else 0)
    return 12 * (int(octv) + 1) + v


def parse_input(text: str):
    items = []
    for tok in text.split():
        if "/" not in tok:
            raise ValueError(f"Thiếu nốt cho chữ: {tok} (dạng chữ/NỐT)")
        w, notes = tok.rsplit("/", 1)
        ns = [note_to_midi(x) for x in notes.split("-") if x]
        items.append({"word": w, "notes": ns})
    return items


def tone_heights(codebook: dict) -> dict:
    """Map tone id -> (start, end, mean) on the 1..5 Chao scale for this variety."""
    out = {}
    for t in (codebook.get("phonology") or {}).get("tones") or []:
        c = str(t.get("chao_contour") or "")
        c = c.split("~")[0]
        digits = [int(x) for x in re.findall(r"[1-5]", c)]
        if digits:
            out[t["id"]] = (digits[0], digits[-1], sum(digits) / len(digits))
    return out


def classify(dt: float, dm: int, dead: float = 0.5) -> str:
    td = 0 if abs(dt) < dead else (1 if dt > 0 else -1)
    md = 0 if dm == 0 else (1 if dm > 0 else -1)
    if td == md:
        return "similar" if td != 0 else "level"
    if td == 0 or md == 0:
        return "oblique"
    return "contrary"


def analyse(items, codebook):
    th = tone_heights(codebook)
    rows = []
    for i in range(1, len(items)):
        a, b = items[i - 1], items[i]
        ta, tb = tone_of(a["word"]), tone_of(b["word"])
        if ta not in th or tb not in th:
            continue
        # transition: mean pitch height of previous tone -> mean pitch height of next tone (Chao scale)
        ha = th[ta][2]
        hb = th[tb][2]
        if tb == "sac" and is_checked(b["word"]):
            hb = max(hb, 4.0)  # sắc trên âm tiết tắc (-p,-t,-c,-ch) cao và ngắn
        dt = hb - ha
        dm = b["notes"][0] - a["notes"][-1]
        kind = classify(dt, dm)
        rows.append({
            "from": a["word"], "to": b["word"],
            "tone_from": TONE_NAME_VI[ta], "tone_to": TONE_NAME_VI[tb],
            "tone_delta": round(dt, 2), "melody_delta_semitones": dm, "motion": kind,
            "cuong_am": kind == "contrary",
            "suggestion": (
                f"giai điệu đi {'lên' if dm > 0 else 'xuống'} nhưng thanh {TONE_NAME_VI[ta]}→{TONE_NAME_VI[tb]} đi "
                f"{'lên' if dt > 0 else 'xuống'}: đổi nốt '{b['word']}' theo hướng {'lên' if dt > 0 else 'xuống'}, "
                f"hoặc thay chữ có thanh phù hợp" if kind == "contrary" else None),
        })
    n = len(rows) or 1
    summary = {k: round(100.0 * sum(r["motion"] == k for r in rows) / n, 1) for k in ("similar", "level", "oblique", "contrary")}
    return {"variety": codebook.get("id"), "name_vi": codebook.get("name_vi"), "transitions": len(rows),
            "percent": summary, "cuong_am_count": sum(r["cuong_am"] for r in rows), "details": rows}


def plot(items, results, codebooks, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    k = len(results)
    fig, axes = plt.subplots(k, 1, figsize=(max(7, 1.1 * len(items)), 2.6 * k), sharex=True)
    if k == 1:
        axes = [axes]
    xs = list(range(len(items)))
    mel = [it["notes"][0] for it in items]
    for ax, res, cb in zip(axes, results, codebooks):
        th = tone_heights(cb)
        tone_h = [th.get(tone_of(it["word"]), (3, 3, 3))[2] for it in items]
        m0 = min(mel)
        ax.plot(xs, [m - m0 for m in mel], "-o", color="#1f77b4", label="Giai điệu (bán cung)")
        ax2 = ax.twinx()
        ax2.plot(xs, tone_h, "--s", color="#2ca02c", label=f"Độ cao thanh (Chao) — {res['variety']}")
        ax2.set_ylim(0.5, 5.5)
        ax2.set_ylabel("Chao 1–5", color="#2ca02c")
        for i, r in enumerate(res["details"], start=1):
            if r["cuong_am"]:
                ax.axvspan(i - 1, i, color="#d62728", alpha=0.18)
                ax.annotate("cưỡng âm", xy=(i - 0.5, max(mel) - m0), ha="center", color="#d62728", fontsize=9)
        ax.set_title(f"{res['name_vi']} — cùng chiều {res['percent']['similar']}% · ngược chiều {res['percent']['contrary']}%",
                     fontsize=10)
        ax.set_ylabel("Bán cung", color="#1f77b4")
        lines = ax.get_legend_handles_labels()
        lines2 = ax2.get_legend_handles_labels()
        ax.legend(lines[0] + lines2[0], lines[1] + lines2[1], loc="lower left", fontsize=8)
    axes[-1].set_xticks(xs)
    axes[-1].set_xticklabels([it["word"] for it in items], fontsize=11)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codebook", action="append", required=True, type=Path,
                    help="bảng mã giọng tiếng Việt (có thể lặp lại để so sánh nhiều giọng)")
    ap.add_argument("--plot", type=Path)
    ap.add_argument("--file", type=Path)
    ap.add_argument("text", nargs="*")
    a = ap.parse_args()
    src = a.file.read_text(encoding="utf-8") if a.file else " ".join(a.text)
    items = parse_input(src)
    cbs = [json.loads(p.read_text(encoding="utf-8")) for p in a.codebook]
    results = [analyse(items, cb) for cb in cbs]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if a.plot:
        plot(items, results, cbs, a.plot)
        print(f"[plot] {a.plot}", file=sys.stderr)


if __name__ == "__main__":
    main()
