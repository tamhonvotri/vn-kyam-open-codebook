#!/usr/bin/env python3
"""Tạo các hình minh họa trong docs/img/ (chạy lại được: python3 tools/make_figures.py)."""

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "docs" / "img"
IMG.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "tools"))
from apply_respelling import WORD_RE, Respeller  # noqa: E402

VARIETIES = ["vie-north", "vie-thanh-hoa", "vie-north-central", "vie-central", "vie-xu-quang",
             "vie-south-central", "vie-binh-dinh-phu-yen", "vie-south", "vie-southwest"]
TONES = [("ngang", "ngang", "#1f77b4"), ("huyen", "huyền", "#7f7f7f"), ("sac", "sắc", "#d62728"),
         ("hoi", "hỏi", "#9467bd"), ("nga", "ngã", "#ff7f0e"), ("nang", "nặng", "#2ca02c")]

SAMPLE_TEXT = """Chiều nay anh về bên sông quê
nghe tiếng ai hò buồn tình xa vắng
thương em đứng đợi bến xưa
trăng tàn bao lần mà người chẳng thấy
quên đi lời hứa năm nào"""


def load(i):
    sub = "vietnamese" if i.startswith("vie-") else "minority"
    return json.loads((ROOT / "codebooks" / sub / f"{i}.json").read_text(encoding="utf-8"))


def fig_tone_contours():
    fig, axes = plt.subplots(3, 3, figsize=(12, 9), sharex=True, sharey=True)
    for ax, vid in zip(axes.flat, VARIETIES):
        cb = load(vid)
        tones = {t["id"]: t for t in cb["phonology"]["tones"]}
        for tid, name, col in TONES:
            t = tones.get(tid)
            if not t:
                continue
            digits = [int(x) for x in re.findall(r"[1-5]", str(t.get("chao_contour") or "").split("~")[0])]
            if not digits:
                continue
            xs = [k / (len(digits) - 1) if len(digits) > 1 else 0.5 for k in range(len(digits))]
            if len(digits) == 1:
                xs, digits = [0, 1], digits * 2
            off = (TONES.index((tid, name, col)) - 2.5) * 0.04
            ax.plot(xs, [d + off for d in digits], "-o", color=col, lw=2, ms=4,
                    label=f"{name} ({t.get('chao_contour')})")
        title = cb["name_vi"].replace("Tiếng Việt — ", "").split("(")[0].strip()
        ax.set_title(f"{title} [{vid}]", fontsize=9)
        ax.set_ylim(0.5, 5.5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.grid(alpha=0.3)
        ax.legend(fontsize=6.5, loc="lower right")
    for ax in axes[:, 0]:
        ax.set_ylabel("Độ cao (thang Chao 1–5)")
    for ax in axes[-1, :]:
        ax.set_xlabel("Thời gian trong âm tiết")
    fig.suptitle("Đường nét 6 thanh điệu theo 9 giọng tiếng Việt (dữ liệu từ các bảng mã VN-KyAm)", fontsize=12)
    fig.tight_layout()
    fig.savefig(IMG / "tone_contours_regions.png", dpi=140)
    plt.close(fig)


def fig_token_safe_mode():
    from tok import load_encoder
    enc = load_encoder()
    rs = Respeller(load("vie-south"), "full", True)
    words = []
    for m in WORD_RE.finditer(SAMPLE_TEXT):
        w = m.group(0).lower()
        r = rs.word(w)
        if r != w and (w, r) not in words:
            words.append((w, r))
    n0 = [len(enc(" " + w)) for w, _ in words]
    n1 = [len(enc(" " + r)) for _, r in words]
    fig, ax = plt.subplots(figsize=(max(8, 0.75 * len(words)), 4.2))
    xs = range(len(words))
    ax.bar([x - 0.2 for x in xs], n0, 0.4, label="Chính tả chuẩn", color="#1f77b4")
    cols = ["#d62728" if b > a else "#2ca02c" for a, b in zip(n0, n1)]
    ax.bar([x + 0.2 for x in xs], n1, 0.4, color=cols)
    from matplotlib.patches import Patch
    for x, (a, b) in zip(xs, zip(n0, n1)):
        if b > a:
            ax.annotate("✗", (x + 0.2, b + 0.05), ha="center", fontsize=11, color="#d62728")
    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"{w}\n→{r}" for w, r in words], fontsize=8)
    ax.set_ylabel("Số token (qwen.tiktoken / YuE2)")
    bad = sum(b > a for a, b in zip(n0, n1))
    ax.set_title(f"Chống gãy từ: {bad}/{len(words)} cách viết mới làm tokenizer cắt vụn (đỏ) → chế độ --safe tự giữ chính tả chuẩn",
                 fontsize=10)
    ax.set_ylim(0, max(n1 + n0) + 1.2)
    ax.legend(handles=[Patch(color="#1f77b4", label="Chính tả chuẩn"),
                       Patch(color="#2ca02c", label="Viết theo giọng Nam Bộ — không gãy (giữ cách viết mới)"),
                       Patch(color="#d62728", label="Viết theo giọng Nam Bộ — GÃY ✗ → --safe giữ chính tả chuẩn")],
              fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(IMG / "token_safe_mode.png", dpi=140)
    plt.close(fig)
    return bad, len(words)


def fig_cuong_am():
    cbs = ["vie-north", "vie-central", "vie-south"]
    args = []
    for c in cbs:
        args += ["--codebook", str(ROOT / "codebooks" / "vietnamese" / f"{c}.json")]
    before = "em/E4 nhớ/G4 mãi/A4 câu/G4 hò/E4 trên/G4 sông/A4 vắng/B4 lặng/D5"
    after = "em/E4 nhớ/G4 mãi/A4 câu/G4 hò/E4 trên/G4 sông/A4 vắng/B4 lặng/G4"
    for name, phrase in (("cuong_am_demo.png", before), ("cuong_am_demo_fixed.png", after)):
        subprocess.run([sys.executable, str(ROOT / "tools" / "cuong_am_check.py"), *args, "--plot", str(IMG / name), phrase],
                       check=True, capture_output=True)


def fig_coverage():
    idx = json.loads((ROOT / "dist" / "index.json").read_text(encoding="utf-8"))
    fam = Counter()
    for x in idx:
        f = (x.get("family") or "?").split("(")[0].strip()
        f = {"Tai-Kadai": "Kra-Dai", "Kra–Dai": "Kra-Dai", "Austro-Asiatic": "Austroasiatic"}.get(f, f)
        fam[f] += 1
    kinds = Counter(x["kind"] for x in idx)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    items = fam.most_common()
    a1.barh([k for k, _ in items][::-1], [v for _, v in items][::-1], color="#1f77b4")
    a1.set_title("Số bảng mã theo ngữ hệ")
    for i, (_, v) in enumerate(items[::-1]):
        a1.text(v + 0.3, i, str(v), va="center")
    lab = {"vietnamese_variety": "Giọng tiếng Việt", "minority_language": "Ngôn ngữ dân tộc"}
    a2.pie(list(kinds.values()), labels=[f"{lab[k]} ({v})" for k, v in kinds.items()], autopct="%1.0f%%",
           colors=["#ff7f0e", "#2ca02c"])
    a2.set_title(f"Tổng {len(idx)} bảng mã")
    fig.tight_layout()
    fig.savefig(IMG / "coverage.png", dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    fig_tone_contours()
    print("token:", fig_token_safe_mode())
    fig_cuong_am()
    fig_coverage()
    print("figures ->", IMG)
