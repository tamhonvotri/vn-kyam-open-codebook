---
name: vn-kyam-codebook
description: Dùng Bảng Mã Ký Âm Mở Việt Nam (VN-KyAm, CC0) để chuyển lời tiếng Việt sang cách viết theo giọng vùng miền (Bắc, Bắc Trung Bộ, Trung Bộ/Huế, Nam Trung Bộ, Nam Bộ), tra bảng chữ–IPA, thanh điệu và cách viết xấp xỉ bằng chữ Quốc ngữ cho 53 ngôn ngữ dân tộc thiểu số Việt Nam, và kiểm tra tokenizer trước khi đưa lời vào mô hình TTS / giọng hát AI. Kích hoạt khi người dùng nói "giọng miền", "phương ngữ", "khẩu âm", "tiếng dân tộc", "bảng mã ký âm", "respelling", hoặc chuẩn bị lời cho mô hình hát/đọc theo giọng vùng miền.
---

# VN-KyAm — Bảng Mã Ký Âm Mở Việt Nam

Thư mục gốc: thư mục chứa file này (`open_codebook_ky_am_vn/`). Mọi dữ liệu là **CC0-1.0 (public domain)**.

## Cấu trúc
- `schema/codebook.schema.json` — JSON Schema của một bảng mã.
- `codebooks/vietnamese/vie-*.json` — 9 giọng tiếng Việt. `vie-south.json` là bản tham chiếu do con người soạn.
- `codebooks/minority/<id>.json` — 98 ngôn ngữ / biến thể của 53 dân tộc thiểu số (id theo tên dân tộc không dấu, ví dụ `tay`, `hmong`, `e-de`; biến thể thêm mã ISO, ví dụ `thai-twh`, `hmong-mww`).
- `dist/` — bản phát hành gộp (`index.json`, `vn_kyam_all.json`, các file CSV, `SHA256SUMS`).
- `tools/` — công cụ.

## Quy trình chuẩn cho mô hình giọng hát / TTS
1. Chọn bảng mã: `dist/index.json` (tra theo `id`, `iso639_3`, `name_vi`).
2. Chuyển lời theo giọng vùng miền:
   ```bash
   python3 tools/apply_respelling.py --codebook codebooks/vietnamese/vie-south.json --level light < loi.txt
   ```
   - `--level light`: chỉ các quy tắc an toàn cho tokenizer (khuyên dùng cho mô hình đã fine-tune theo giọng).
   - `--level full [--include-optional]`: mô phỏng khẩu âm đầy đủ bằng chữ (dùng cho mô hình chưa fine-tune, hoặc để tham khảo).
3. **Luôn kiểm tra tokenizer** trước khi đưa vào mô hình:
   ```bash
   python3 tools/tokenizer_check.py --codebook codebooks/vietnamese/vie-south.json --level full --text-file loi.txt
   ```
   Hoặc dùng thẳng `apply_respelling.py --safe` để tự giữ chính tả chuẩn cho từ bị cắt vụn ("chống gãy từ").
   Từ nào bị `more_tokens` (bị cắt vụn) thì giữ chính tả chuẩn; để khẩu âm do mô hình/embedding đảm nhận
   (xem `ml_hints.unseen_token_rhyme_twins` trong `vie-south.json`).
4. Nếu có giai điệu, kiểm tra cưỡng âm theo đúng giọng:
   ```bash
   python3 tools/cuong_am_check.py --codebook codebooks/vietnamese/vie-south.json --plot out.png "em/E4 nhớ/G4 mãi/A4"
   ```
   Báo cho người dùng các cặp `cuong_am: true` kèm `suggestion`; đây là gợi ý heuristic, không phải phán quyết.
5. Ngôn ngữ dân tộc: dùng `phonology` (chữ → IPA) và `ml_hints.quoc_ngu_approximation` để viết xấp xỉ bằng chữ
   Quốc ngữ cho mô hình chỉ biết tiếng Việt. Ghi rõ với người dùng rằng đây là xấp xỉ.

## Lưu ý trung thực (bắt buộc nói với người dùng)
- Video demo: https://youtu.be/jJ50J8sL5po
- Trừ `vie-south.json`, các bảng có `status: "draft-llm"`: do Gemini 4 Carbon soạn (có Google Search), Gemini 4 Argon
  phản biện. **Chưa được người bản xứ hay nhà ngôn ngữ học thẩm định** (`validation.native_speaker_reviewed=false`).
- Mục có `confidence: "low"` hoặc nằm trong `validation.open_issues` thì không được coi là sự thật.
- Điểm % giọng vùng miền của bộ phân loại tự động thay đổi mạnh chỉ do mix/EQ, không dùng làm bằng chứng khẩu âm.

## Đóng góp / sửa lỗi
Sửa JSON, chạy `python3 tools/build_release.py` (kiểm schema + tạo lại `dist/`). Khi người bản xứ đã xác nhận, đặt
`validation.native_speaker_reviewed=true` và ghi tên/ngày vào `provenance`.

## Tạo lại hoặc mở rộng bằng LLM
`tools/generate_codebooks.py` (cần `GEMINI_API_KEY`). Thêm mục mới vào `tools/targets.json` rồi chạy
`python3 tools/generate_codebooks.py --only <id>`.

