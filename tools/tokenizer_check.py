#!/usr/bin/env python3
"""
Check how a tokenizer fragments words before/after dialect respelling.
A respelling that turns 1 token into several sub-tokens usually makes TTS / singing models
mispronounce, so prefer rules that keep or reduce the token count.

  python3 tools/tokenizer_check.py --codebook codebooks/vietnamese/vie-south.json --level full \
      --tiktoken path/to/qwen.tiktoken  --text-file lyrics.txt
  python3 tools/tokenizer_check.py --codebook ... --hf Qwen/Qwen2.5-7B  "câu ví dầu"

If neither --tiktoken nor --hf is given, downloads qwen.tiktoken from m-a-p/YuE2-3B on Hugging Face.
"""

import argparse
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apply_respelling import WORD_RE, Respeller  # noqa: E402

QWEN_PAT = (r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+")


def load_encoder(args):
    if args.hf:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(args.hf)
        return lambda s: tok.encode(s, add_special_tokens=False)
    import tiktoken
    path = args.tiktoken
    if not path:
        from huggingface_hub import hf_hub_download
        path = hf_hub_download("m-a-p/YuE2-3B", "qwen.tiktoken")
    ranks = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            b, r = line.split()
            ranks[base64.b64decode(b)] = int(r)
    enc = tiktoken.Encoding("qwen", pat_str=QWEN_PAT, mergeable_ranks=ranks, special_tokens={})
    return lambda s: enc.encode(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codebook", required=True, type=Path)
    ap.add_argument("--level", choices=["light", "full"], default="full")
    ap.add_argument("--include-optional", action="store_true")
    ap.add_argument("--tiktoken")
    ap.add_argument("--hf")
    ap.add_argument("--text-file", type=Path)
    ap.add_argument("text", nargs="*")
    a = ap.parse_args()
    encode = load_encoder(a)
    rs = Respeller(json.loads(a.codebook.read_text(encoding="utf-8")), a.level, a.include_optional)
    src = a.text_file.read_text(encoding="utf-8") if a.text_file else " ".join(a.text)
    words = sorted(set(m.group(0).lower() for m in WORD_RE.finditer(src)))
    worse, same, better = [], 0, 0
    for w in words:
        r = rs.word(w)
        if r == w:
            continue
        n0, n1 = len(encode(" " + w)), len(encode(" " + r))
        if n1 > n0:
            worse.append((w, r, n0, n1))
        elif n1 < n0:
            better += 1
        else:
            same += 1
    print(json.dumps({"changed_words": len(worse) + same + better, "token_count_same": same, "fewer_tokens": better,
                      "more_tokens": len(worse),
                      "fragmenting": [{"word": w, "respelled": r, "tokens_before": n0, "tokens_after": n1} for w, r, n0, n1 in worse]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

