# Changelog

## v0.2.1 — 2026-11-14
- README / báo cáo: ghi nhận PGS.TS Bùi Hiền, người có đề xuất cải tiến chữ quốc ngữ (2017) là nguồn gốc ý tưởng của dự án, và bổ sung trích dẫn.
- README: thêm link bản lưu Internet Archive và Wayback Machine của v0.2.0.
- `generate_codebooks.py`: chốt ngân sách API.

## v0.2.0 — 2026-11-14
**Ngôn ngữ mới (49 bảng mã, tổng 107)**
- 4 giọng tiếng Việt mới: Thổ ngữ Thanh Hóa (`vie-thanh-hoa`), giọng xứ Quảng (`vie-xu-quang`), giọng Bình Định – Phú Yên
  (`vie-binh-dinh-phu-yen`), giọng miền Tây Nam Bộ (`vie-southwest`).
- 45 bảng mã ngôn ngữ / biến thể của các dân tộc có nhiều ngôn ngữ, ví dụ Thái Trắng, Thái Đỏ, Tai Yo, Tai Thanh, Tày Hàng Tổng, Tày Tấc;
  Mông Trắng, Mông Xanh, Mông Đô, Hmong Don; Chăm Tây, Haroi; Triều Châu, Hải Nam; Kim Mun; Ca Dong, Hà Lăng, Tơ Đra, Mơ Nâm;
  Mnông Đông, Mnông Nam; Nùng Dín, En; Mã Liềng, Arem; Cờ Lao Xanh, Cờ Lao Đỏ; Pa Cô; Thu Lao, Pa Dí; Nguồn…
  (danh sách đầy đủ trong README và `dist/index.json`).

**Công cụ**
- `apply_respelling.py --safe`: chống gãy từ, tự giữ chính tả chuẩn cho từ mà tokenizer cắt vụn hơn sau khi chuyển chữ.
- `tools/cuong_am_check.py` (mới): phát hiện cưỡng âm (giai điệu đi ngược chiều thanh điệu) theo đường nét thanh của
  từng giọng; xuất JSON và đồ thị so sánh nhiều giọng.
- `tools/make_figures.py` (mới): tạo các đồ thị minh họa trong `docs/img/`.
- `tools/tok.py`: gom phần nạp tokenizer dùng chung.

**Tài liệu**
- README: thêm video demo (https://youtu.be/jJ50J8sL5po), sơ đồ quy trình, đồ thị giải thích giọng vùng miền / chống gãy từ /
  cưỡng âm, bảng đầy đủ các ngôn ngữ, lời cảm ơn (nhạc sĩ Đông Hải, ca sĩ Đông Đào, ca sĩ Thảo Vy), trích dẫn bộ dữ liệu
  VieNeu-TTS và các công trình ngữ âm học / phương ngữ học / âm nhạc học liên quan.
- Báo cáo kỹ thuật v0.2.0.

**Đã biết**
- `xo-dang-moo` chưa qua phản biện chéo (API hết hạn mức), đã ghi trong `open_issues`.
- Một số giọng tiếng Việt có số Chao chưa thống nhất giữa các bảng (ví dụ thanh sắc Nam Trung Bộ `24` và xứ Quảng `35`).

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
