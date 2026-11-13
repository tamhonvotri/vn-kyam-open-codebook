#!/usr/bin/env python3
"""
Validate all codebooks against the schema and build machine-readable release artifacts:
  dist/index.json              — catalogue of all codebooks (id, names, ISO, status, review score)
  dist/vn_kyam_all.json        — every codebook in one file
  dist/csv/correspondences.csv — Vietnamese-variety sound correspondences (long format)
  dist/csv/respelling_rules.csv
  dist/csv/grapheme_ipa.csv    — onsets/vowels/codas for every language
  dist/csv/tones.csv
  dist/csv/quoc_ngu_approximation.csv
  dist/SHA256SUMS              — checksums (useful as a timestamped fingerprint of the release)
"""

import csv
import hashlib
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema" / "codebook.schema.json").read_text(encoding="utf-8"))
DIST = ROOT / "dist"


def main():
    validator = jsonschema.Draft202012Validator(SCHEMA)
    books, bad = [], 0
    for p in sorted((ROOT / "codebooks").rglob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        errs = list(validator.iter_errors(d))
        if errs:
            bad += 1
            print(f"[SCHEMA] {p.name}: {len(errs)} errors, first: {errs[0].message[:160]}")
        books.append(d)

    DIST.mkdir(exist_ok=True)
    (DIST / "csv").mkdir(exist_ok=True)

    index = []
    for d in books:
        rev = (d.get("validation") or {}).get("llm_review") or {}
        index.append({
            "id": d["id"], "kind": d["kind"], "name_vi": d.get("name_vi"), "name_en": d.get("name_en"),
            "ethnic_group_vi": d.get("ethnic_group_vi"),
            "iso639_3": (d.get("language") or {}).get("iso639_3"),
            "glottocode": (d.get("language") or {}).get("glottocode"),
            "family": (d.get("language") or {}).get("family"),
            "status": d.get("status"), "llm_review_score": rev.get("score"),
            "native_speaker_reviewed": (d.get("validation") or {}).get("native_speaker_reviewed", False),
            "file": f"codebooks/{'vietnamese' if d['kind'] == 'vietnamese_variety' else 'minority'}/{d['id']}.json",
        })
    (DIST / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    (DIST / "vn_kyam_all.json").write_text(json.dumps(books, ensure_ascii=False, indent=1), encoding="utf-8")

    def write_csv(name, header, rows):
        with open(DIST / "csv" / name, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)

    write_csv("correspondences.csv",
              ["id", "slot", "standard", "variety", "ipa_standard", "ipa_variety", "condition", "example_standard",
               "example_variety", "prevalence", "confidence"],
              [[d["id"]] + [c.get(k) for k in ["slot", "standard", "variety", "ipa_standard", "ipa_variety", "condition",
                                                "example_standard", "example_variety", "prevalence", "confidence"]]
               for d in books for c in d.get("correspondences_from_standard_vietnamese") or []])
    write_csv("respelling_rules.csv", ["id", "slot", "from", "to", "level", "optional", "note"],
              [[d["id"], r.get("slot"), r.get("from"), r.get("to"), r.get("level"), r.get("optional", False), r.get("note")]
               for d in books for r in d.get("respelling_rules") or []])
    write_csv("grapheme_ipa.csv", ["id", "position", "grapheme", "ipa", "note", "confidence"],
              [[d["id"], pos, g.get("grapheme"), g.get("ipa"), g.get("note"), g.get("confidence")]
               for d in books for pos in ("onsets", "vowels", "codas")
               for g in ((d.get("phonology") or {}).get(pos) or []) if isinstance(g, dict)])
    write_csv("tones.csv", ["id", "tone_id", "name", "mark", "chao_contour", "phonation", "merges_with", "confidence"],
              [[d["id"]] + [t.get(k) for k in ["id", "name", "mark", "chao_contour", "phonation", "merges_with", "confidence"]]
               for d in books for t in ((d.get("phonology") or {}).get("tones") or []) if isinstance(t, dict)])
    write_csv("quoc_ngu_approximation.csv", ["id", "native", "quoc_ngu", "note"],
              [[d["id"], q.get("native"), q.get("quoc_ngu"), q.get("note")]
               for d in books for q in ((d.get("ml_hints") or {}).get("quoc_ngu_approximation") or []) if isinstance(q, dict)])

    sums = []
    for p in sorted(list((ROOT / "codebooks").rglob("*.json")) + [ROOT / "schema" / "codebook.schema.json"]):
        sums.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT)}")
    (DIST / "SHA256SUMS").write_text("\n".join(sums) + "\n", encoding="utf-8")
    print(f"{len(books)} codebooks, {bad} with schema errors -> {DIST}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

