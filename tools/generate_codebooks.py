#!/usr/bin/env python3
"""
Generate draft codebooks (Bảng mã ký âm) for Vietnamese regional varieties and the 53 ethnic-minority
groups of Viet Nam, using the reference Southern codebook as the template.

Pipeline per target:
  1. Gemini 4 Carbon + Google Search grounding  -> drafts a JSON codebook following schema + exemplar.
  2. Gemini 4 Argon + Google Search grounding   -> independent review: corrects errors, lists issues.
  3. Local checks: JSON schema validation, source URL reachability, provenance stamping.

Every generated file is marked status="draft-llm" and native_speaker_reviewed=false.

Usage:
  python3 tools/generate_codebooks.py                 # all targets, skip existing
  python3 tools/generate_codebooks.py --only vie-central,tyz
  python3 tools/generate_codebooks.py --force --workers 4
"""

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema" / "codebook.schema.json").read_text(encoding="utf-8"))
EXEMPLAR = (ROOT / "codebooks" / "vietnamese" / "vie-south.json").read_text(encoding="utf-8")
TARGETS = json.loads((ROOT / "tools" / "targets.json").read_text(encoding="utf-8"))
LOG_DIR = ROOT / "build_logs"

DRAFT_MODEL = os.environ.get("VNKYAM_DRAFT_MODEL", "gemini-4-carbon")
REVIEW_MODEL = os.environ.get("VNKYAM_REVIEW_MODEL", "gemini-4-argon")
TODAY = dt.date.today().isoformat()


def load_key() -> str:
    if os.environ.get("GEMINI_API_KEY"):
        return os.environ["GEMINI_API_KEY"].strip()
    for env_path in (ROOT / ".env", ROOT.parent / ".env"):
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("GEMINI_API_KEY not found (env or .env)")


API_KEY = load_key()


def gemini(model: str, system: str, user: str, temperature: float = 0.2, retries: int = 4) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 32768},
    }
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                         headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=600) as r:
                data = json.load(r)
            cand = data["candidates"][0]
            text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought"))
            chunks = [
                {"title": g.get("web", {}).get("title"), "uri": g.get("web", {}).get("uri")}
                for g in cand.get("groundingMetadata", {}).get("groundingChunks", [])
            ]
            queries = cand.get("groundingMetadata", {}).get("webSearchQueries", [])
            return {"text": text, "grounding": chunks, "queries": queries, "usage": data.get("usageMetadata", {})}
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:400]}"
            if e.code in (400, 401, 403, 404):
                break
        except Exception as e:  # noqa: BLE001
            last = repr(e)
        time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"{model} failed: {last}")


def extract_json(text: str) -> dict:
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, flags=re.S)
    raw = m.group(1) if m else text[text.find("{"): text.rfind("}") + 1]
    return json.loads(raw)


DRAFT_SYSTEM = """Bạn là nhà ngôn ngữ học (phương ngữ học tiếng Việt, ngôn ngữ dân tộc thiểu số Việt Nam, ngữ âm học IPA)
kiêm kỹ sư dữ liệu. Nhiệm vụ: soạn MỘT "bảng mã ký âm" máy đọc được (JSON) cho một giống ngôn ngữ, theo đúng
JSON Schema và theo mẫu tham chiếu (phương ngữ Nam Bộ) được cung cấp.

Quy tắc bắt buộc:
- Dùng Google Search để tra cứu (Ethnologue, Glottolog, Wikipedia, PHOIBLE, ScriptSource, Omniglot, Unicode,
  luận văn/bài báo, văn bản chính phủ Việt Nam về chữ viết dân tộc, UNESCO...). Ưu tiên nguồn học thuật.
- KHÔNG bịa. Thông tin không chắc chắn: để null hoặc bỏ mục, hoặc ghi confidence="low". Mã ISO 639-3 và Glottocode
  phải đúng; nếu một dân tộc dùng nhiều ngôn ngữ/biến thể, chọn biến thể chính ở Việt Nam và liệt kê các biến thể
  khác trong ml_hints.sub_varieties (kèm mã ISO).
- IPA chuẩn; thanh điệu ghi bằng số Chao (ví dụ "33", "214").
- sources: chỉ liệt kê nguồn thực sự đã dùng, kèm URL thật (không dùng link chuyển hướng vertexaisearch).
- status phải là "draft-llm"; license "CC0-1.0"; validation.native_speaker_reviewed=false, linguist_reviewed=false.
- Văn bản mô tả viết bằng tiếng Việt; tên riêng giữ nguyên.

Với kind="vietnamese_variety": điền correspondences_from_standard_vietnamese (so với cách đọc chuẩn gốc Hà Nội của
chữ Quốc ngữ), respelling_rules (slot onset|rhyme|tone|word; level "light" cho quy tắc an toàn, "full" cho quy tắc
mạnh; optional=true nếu biến thể không phổ quát), lexicon từ địa phương, music (thể loại dân ca, luyến láy, có thể
kèm ký hiệu ABC), ml_hints.

Với kind="minority_language": KHÔNG có correspondences_from_standard_vietnamese/respelling_rules. Thay vào đó:
- scripts: chữ viết đang dùng (Latinh do nhà nước ban hành, chữ truyền thống, Unicode block nếu có).
- phonology.onsets/vowels/codas: ánh xạ grapheme (theo chữ Latinh phổ biến nhất ở Việt Nam, nếu có) -> IPA.
- phonology.tones hoặc register_or_phonation (nhiều ngôn ngữ Môn-Khmer không có thanh điệu mà có âm vực).
- ml_hints.quoc_ngu_approximation: danh sách {"native": ..., "quoc_ngu": ..., "note": ...} — cách viết xấp xỉ
  bằng chữ Quốc ngữ tiếng Việt để mô hình TTS/giọng hát chỉ biết tiếng Việt có thể đọc gần đúng; ghi rõ những âm
  không có trong tiếng Việt.
- ml_hints.sub_varieties, ml_hints.sample_words (5–15 từ cơ bản: native, IPA, nghĩa tiếng Việt) nếu có nguồn.
- lexicon: có thể để trống nếu không có nguồn.
- music: thể loại hát/dân ca, nhạc cụ, đặc điểm giai điệu nếu có nguồn.

Chỉ trả về MỘT khối ```json ... ``` duy nhất, không kèm lời giải thích."""

REVIEW_SYSTEM = """Bạn là phản biện độc lập (ngôn ngữ học + ngữ âm học IPA + dân tộc học Việt Nam). Bạn nhận một bảng mã
ký âm JSON do một mô hình khác soạn. Hãy dùng Google Search để kiểm tra lại các thông tin quan trọng: mã ISO 639-3,
Glottocode, ngữ hệ, chữ viết, hệ thống thanh điệu/âm vực, các ánh xạ grapheme->IPA, quy tắc tương ứng phương ngữ,
thể loại âm nhạc, và các URL nguồn.

Trả về MỘT khối ```json ... ``` với cấu trúc:
{
  "decision": "APPROVE" | "MODIFY" | "REJECT",
  "score": số 1-10,
  "issues": [{"path": "đường dẫn trường", "severity": "high|medium|low", "problem": "...", "fix": "..."}],
  "corrected": { ...toàn bộ bảng mã đã sửa (giữ nguyên cấu trúc schema; xóa/hạ confidence các mục không kiểm chứng
                 được; sửa sai; giữ status="draft-llm")... }
}
Không bịa thêm nội dung không có nguồn. Nếu không chắc, hạ confidence xuống "low" hoặc đưa vào validation.open_issues."""


def compact_schema() -> str:
    return json.dumps(SCHEMA, ensure_ascii=False)


def build_user_prompt(t: dict) -> str:
    return (
        f"JSON Schema:\n```json\n{compact_schema()}\n```\n\n"
        f"Mẫu tham chiếu (phương ngữ Nam Bộ, do con người soạn — làm theo cấu trúc và độ chi tiết, KHÔNG sao chép nội dung):\n"
        f"```json\n{EXEMPLAR}\n```\n\n"
        f"Hãy soạn bảng mã cho:\n```json\n{json.dumps(t, ensure_ascii=False)}\n```\n"
        f"Dùng đúng id=\"{t['id']}\" và kind=\"{t['kind']}\". Ngày truy cập nguồn: {TODAY}."
    )


def validate(doc: dict) -> list:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return ["jsonschema not installed — skipped"]
    v = jsonschema.Draft202012Validator(SCHEMA)
    return [f"{'/'.join(map(str, e.path))}: {e.message}" for e in v.iter_errors(doc)][:30]


def check_url(url: str) -> str:
    if not url or "vertexaisearch" in url:
        return "skipped"
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0 vn-kyam-linkcheck"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return f"ok_{r.status}"
    except urllib.error.HTTPError as e:
        return f"http_{e.code}"
    except Exception as e:  # noqa: BLE001
        return f"error_{type(e).__name__}"


def out_path(t: dict) -> Path:
    sub = "vietnamese" if t["kind"] == "vietnamese_variety" else "minority"
    return ROOT / "codebooks" / sub / f"{t['id']}.json"


def process(t: dict, force: bool) -> str:
    dst = out_path(t)
    if dst.exists() and not force:
        return f"skip {t['id']}"
    LOG_DIR.mkdir(exist_ok=True)
    log = {"target": t, "started": dt.datetime.now().isoformat()}

    draft_res = gemini(DRAFT_MODEL, DRAFT_SYSTEM, build_user_prompt(t))
    log["draft"] = {"grounding": draft_res["grounding"], "queries": draft_res["queries"], "usage": draft_res["usage"]}
    draft = extract_json(draft_res["text"])

    review_user = (
        f"JSON Schema:\n```json\n{compact_schema()}\n```\n\nBảng mã cần phản biện:\n```json\n"
        f"{json.dumps(draft, ensure_ascii=False, indent=1)}\n```"
    )
    try:
        rev_res = gemini(REVIEW_MODEL, REVIEW_SYSTEM, review_user, temperature=0.1)
        review = extract_json(rev_res["text"])
        log["review"] = {"grounding": rev_res["grounding"], "queries": rev_res["queries"], "usage": rev_res["usage"],
                         "decision": review.get("decision"), "score": review.get("score"), "issues": review.get("issues")}
        final = review.get("corrected") or draft
        if not isinstance(final, dict) or "id" not in final:
            final = draft
    except Exception as e:  # noqa: BLE001
        review = {"decision": None, "score": None, "issues": [], "error": str(e)}
        log["review_error"] = str(e)
        final = draft

    # Enforce invariants
    final["id"] = t["id"]
    final["kind"] = t["kind"]
    final["status"] = "draft-llm"
    final["license"] = "CC0-1.0"
    val = final.setdefault("validation", {})
    val["native_speaker_reviewed"] = False
    val["linguist_reviewed"] = False
    val["llm_review"] = {
        "model": REVIEW_MODEL,
        "decision": review.get("decision"),
        "score": review.get("score"),
        "issues": review.get("issues", []),
    }
    val.setdefault("open_issues", [])
    for s in final.get("sources", []) or []:
        if isinstance(s, dict):
            s["url_check"] = check_url(s.get("url"))
    final["provenance"] = {
        "draft_model": DRAFT_MODEL,
        "review_model": REVIEW_MODEL,
        "method": "LLM + Google Search grounding, cross-reviewed by a second LLM; NOT verified by native speakers",
        "generated": TODAY,
        "search_queries": (draft_res["queries"] or [])[:20],
    }
    schema_errors = validate(final)
    if schema_errors and schema_errors != ["jsonschema not installed — skipped"]:
        val["open_issues"].append("schema: " + "; ".join(schema_errors[:5]))
    log["schema_errors"] = schema_errors

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(final, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (LOG_DIR / f"{t['id']}.log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"done {t['id']} review={review.get('decision')}/{review.get('score')} schema_errors={len(schema_errors)}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    targets = TARGETS
    if args.only:
        keep = set(args.only.split(","))
        targets = [t for t in TARGETS if t["id"] in keep]
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(process, t, args.force): t["id"] for t in targets}
        for f in cf.as_completed(futs):
            try:
                print(f.result(), flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"FAIL {futs[f]}: {e}", flush=True)


if __name__ == "__main__":
    main()

