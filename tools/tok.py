"""Shared tokenizer loader for VN-KyAm tools (qwen.tiktoken of YuE2-3B by default, or any Hugging Face tokenizer)."""

import base64
from pathlib import Path

QWEN_PAT = (r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+")


def load_encoder(tiktoken_path=None, hf_name=None):
    """Return a function str -> list[int]."""
    if hf_name:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(hf_name)
        return lambda s: tok.encode(s, add_special_tokens=False)
    import tiktoken
    path = tiktoken_path
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
