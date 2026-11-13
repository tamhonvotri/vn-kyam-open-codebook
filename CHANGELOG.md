# Changelog

## v0.1.1 — 2026-11-13
- Đủ 58/58 bảng mã: 5 phương ngữ tiếng Việt + ngôn ngữ của toàn bộ 53 dân tộc thiểu số.
- Thêm báo cáo kỹ thuật `paper/VN-KyAm_technical_report_v0.1.1.md`.
- Tạo lại `dist/` và `SHA256SUMS`.

## v0.1.0 — 2026-11-13 (bản công bố sớm / early public release)
- Schema bảng mã ký âm v1 (`schema/codebook.schema.json`).
- 5 phương ngữ tiếng Việt: Bắc Bộ, Bắc Trung Bộ, Trung Bộ (Huế), Nam Trung Bộ, Nam Bộ (bản tham chiếu do con người soạn).
- Bảng mã cho các ngôn ngữ dân tộc thiểu số đã hoàn thành (xem `dist/index.json`); các dân tộc còn lại sẽ được bổ sung ở bản kế tiếp.
- Công cụ: `apply_respelling.py`, `tokenizer_check.py`, `generate_codebooks.py`, `build_release.py`; `SKILL.md` cho AI agent.
- Toàn bộ phát hành theo CC0 1.0 (public domain).
