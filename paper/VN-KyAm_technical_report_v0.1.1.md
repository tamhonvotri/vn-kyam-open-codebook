# VN-KyAm: Bảng Mã Ký Âm Mở cho các phương ngữ tiếng Việt và ngôn ngữ của 53 dân tộc thiểu số Việt Nam

**Báo cáo kỹ thuật v0.1.1 — 13/11/2026 — Giấy phép CC0 1.0 (public domain)**

## Tóm tắt (Abstract)
Chúng tôi công bố VN-KyAm, bộ 58 "bảng mã ký âm" máy đọc được (JSON + CSV), gồm 5 phương ngữ tiếng Việt và ngôn
ngữ của 53 dân tộc thiểu số được công nhận ở Việt Nam. Bộ mã kèm theo một schema chung và các công cụ để chuyển lời
sang cách viết theo giọng vùng miền và kiểm tra tokenizer. Bảng phương ngữ Nam Bộ do con người soạn, dựa trên kinh
nghiệm fine-tune một mô hình giọng hát. 57 bảng còn lại do mô hình ngôn ngữ lớn soạn có tra cứu web, rồi được một mô
hình thứ hai phản biện độc lập. Mọi mục đều gắn mức tin cậy và trạng thái thẩm định. Toàn bộ được hiến tặng vào phạm vi
công cộng để không ai có thể độc quyền hóa cách mô tả kỹ thuật này. Đây là bản công bố sớm để cộng đồng sửa, chưa phải
nghiên cứu đã được người bản xứ kiểm chứng.

*English:* VN-KyAm releases 58 machine-readable phonetic codebooks into the public domain (CC0): five Vietnamese
regional varieties and the languages of Viet Nam's 53 recognised ethnic minorities. The release also includes a shared
schema, respelling tools and a tokenizer check. The Southern codebook is hand-authored. The others are LLM-drafted with
web-search grounding and cross-reviewed by a second LLM; native speakers have not yet validated them. Every entry
carries a confidence level.

## 1. Mục đích
- **Công bố phòng vệ (defensive publication).** Đưa các quy tắc ký âm giọng vùng miền và bảng chữ–âm dân tộc vào phạm
  vi công cộng, có mốc thời gian (lịch sử Git, `dist/SHA256SUMS`). Mục tiêu là để các quy tắc này không bị một cá nhân
  hay tổ chức trung gian đăng ký độc quyền rồi thu phí.
- **Hạ tầng cho AI tiếng nói và giọng hát.** Cung cấp một định dạng thống nhất để mô hình TTS, ASR và giọng hát xử lý
  giọng vùng miền và ngôn ngữ dân tộc.
- **Điểm khởi đầu cho cộng đồng.** Người bản xứ, nghệ nhân và nhà ngôn ngữ học có thể sửa và xác nhận từng mục.

Ngôn ngữ và phương ngữ là tài sản chung của cộng đồng người nói. VN-KyAm chỉ là một cách mô tả kỹ thuật và không xác
lập quyền sở hữu nào đối với ngôn ngữ.

## 2. Định dạng (schema)
Mỗi bảng mã là một file JSON theo `schema/codebook.schema.json` (JSON Schema 2020-12), gồm:
- **Định danh:** `id`, tên Việt/Anh, tên tự gọi, mã ISO 639-3, Glottocode, ngữ hệ, vùng phân bố.
- **Chữ viết:** tên, mã ISO 15924, khối Unicode, có được nhà nước ban hành hay không.
- **Âm vị học:** âm đầu, nguyên âm và âm cuối (chữ → IPA); thanh điệu (số Chao, dấu, cách phát âm, nhập thanh) hoặc âm vực/cách phát âm cho các ngôn ngữ không có thanh.
- **Riêng với phương ngữ tiếng Việt:**
  - `correspondences_from_standard_vietnamese`: tương ứng âm so với cách đọc chuẩn (gốc Hà Nội), có độ phổ biến (`categorical`, `common`, `variable`, `local`).
  - `respelling_rules`: quy tắc chuyển chữ máy chạy được, theo vị trí `onset`, `rhyme`, `tone`, `word`. Mức `light` an toàn cho tokenizer; mức `full` mô phỏng khẩu âm; quy tắc không phổ quát gắn `optional`.
- **Riêng với ngôn ngữ dân tộc:**
  - `ml_hints.quoc_ngu_approximation`: cách viết xấp xỉ bằng chữ Quốc ngữ, cho mô hình chỉ biết tiếng Việt.
  - `sub_varieties`, `sample_words`.
- **Chung cho mọi bảng:**
  - Từ vựng địa phương.
  - Âm nhạc: thể loại dân gian, luyến láy (có thể kèm ký hiệu ABC), thang âm, nhạc cụ.
  - Nguồn tham khảo, có kiểm tra URL còn sống.
  - `validation` và `provenance` (người hoặc mô hình nào soạn, ai đã duyệt).

## 3. Phương pháp
### 3.1. Bảng tham chiếu Nam Bộ (do con người soạn)
- **Tương ứng âm:** soạn từ kiến thức phương ngữ học phổ biến, ví dụ thanh ngã nhập vào thanh hỏi; v→[j]; -an/-ang;
  -at/-ac; -inh→[ɨn]; qu→[w].
- **Phần `ml_hints`:** rút ra từ quá trình fine-tune mô hình giọng hát YuE2-3B với LoRA:
  - bảng chuyển chữ đã kiểm chứng vẫn giữ 1 token (cũ→củ, tay→tai…);
  - danh sách cách viết bị cấm vì làm vỡ token;
  - kỹ thuật chuyển vector dịch chuyển embedding từ các từ cùng vần đã được học sang từ chưa học;
  - quy ước khóa nhạc ABC (K:G) và ký hiệu luyến Bolero.

### 3.2. 57 bảng còn lại (LLM soạn, có phản biện chéo)
1. **Soạn:** Gemini 4 Carbon (Google AI API) có công cụ Google Search, nhận schema, bảng Nam Bộ làm mẫu và yêu cầu
   "không bịa: không chắc thì để null hoặc hạ confidence".
2. **Phản biện:** Gemini 4 Argon, cũng có Google Search, kiểm tra lại mã ngôn ngữ, chữ viết, thanh điệu, ánh xạ IPA và
   nguồn. Mô hình này trả về quyết định, điểm, danh sách lỗi và bản đã sửa. Bản đã sửa được dùng làm bản phát hành;
   toàn bộ nhận xét lưu trong `validation.llm_review`.
3. **Kiểm tra cục bộ:** kiểm schema, kiểm URL nguồn còn truy cập được, ép các trường cố định (`status: draft-llm`,
   `license: CC0-1.0`, `native_speaker_reviewed: false`). Truy vấn tìm kiếm đã dùng được lưu trong `build_logs/`.

Pipeline có thể chạy lại bằng `tools/generate_codebooks.py`.

## 4. Kết quả
| Chỉ số | Giá trị |
|---|---|
| Số bảng mã | 58 (5 phương ngữ tiếng Việt + 53 ngôn ngữ dân tộc) |
| Hợp lệ schema | 58/58 |
| Có mã ISO 639-3 | 58/58 |
| Ngữ hệ | Nam Á 29 (gồm tiếng Việt), Tai–Kadai 12, Hán–Tạng 9, Nam Đảo 5, H'Mông–Dao 3 |
| Điểm phản biện của Argon | 9/10: 37 bảng; 8/10: 20 bảng (bảng Nam Bộ do con người soạn, không chấm) |
| Quyết định phản biện | APPROVE 6, MODIFY 51 (đã áp dụng bản sửa), REJECT 0 |

**Phát hiện về tokenizer.** Chúng tôi áp dụng toàn bộ quy tắc mức `full` của giọng Nam Bộ lên lời bài "Còn Đâu Câu
Ví Dầu", rồi đo bằng tokenizer `qwen.tiktoken` của YuE2-3B:
- Có 22 từ bị đổi cách viết. 11 từ trong số đó bị cắt thành nhiều token hơn (ví dụ tình→từn, quên→wên, tàn→tàng, ví→dí). 8 từ giữ nguyên số token, 3 từ giảm số token.
- Với mức `light`, chỉ 1 từ bị đổi và không từ nào bị cắt vụn.
- Vì vậy, với mô hình đã fine-tune, nên chỉ dùng mức `light` và để khẩu âm cho embedding hoặc LoRA đảm nhận.
- Mức `full` phù hợp hơn cho mô hình chưa fine-tune hoặc để tham khảo.

Công cụ `tools/tokenizer_check.py` dùng để đo điều này cho bất kỳ tokenizer nào.

## 5. Giới hạn (xin đọc kỹ)
1. **Chưa có người bản xứ thẩm định.** 57/58 bảng do LLM soạn. Phản biện chéo bằng một LLM khác giúp giảm lỗi nhưng
   không thay được người bản xứ. Mục `confidence: low` và các mục trong `validation.open_issues` không nên coi là sự thật.
2. **Phương ngữ là phổ liên tục.** Quy tắc `common` không có nghĩa là mọi người trong vùng đều nói như vậy. Mỗi bảng
   lấy một giọng đại diện (ví dụ Huế cho Trung Bộ).
3. **Một dân tộc có thể dùng nhiều ngôn ngữ.** Mỗi bảng chọn biến thể chính ở Việt Nam, các biến thể khác nằm trong
   `ml_hints.sub_varieties`.
4. **Ký hiệu ABC cho luyến láy** phần lớn là đề xuất kỹ thuật, chưa được nghệ nhân xác nhận.
5. **Không dùng điểm của bộ phân loại giọng vùng miền tự động làm bằng chứng khẩu âm.** Trong thực nghiệm, điểm
   "% giọng Nam" tăng từ khoảng 62% lên khoảng 84% chỉ nhờ mix/EQ hậu kỳ, không đổi gì ở mô hình.
6. Kỹ thuật chuyển vector embedding theo từ cùng vần (`vie-south.json`) **chưa có thí nghiệm đối chứng (ablation)**.

## 6. Đóng góp
Sửa file JSON và chạy `python3 tools/build_release.py`. Người bản xứ hoặc chuyên gia sau khi kiểm tra thì đặt
`validation.native_speaker_reviewed` / `linguist_reviewed` = `true` và ghi vào `provenance.reviewers`. Mọi đóng góp đều
được phát hành theo CC0.

## 7. Công bố về việc dùng AI
Báo cáo, schema và công cụ do một AI coding agent soạn theo yêu cầu và dưới sự giám sát của chủ dự án. 57 bảng mã do
Gemini 4 Carbon soạn và Gemini 4 Argon phản biện, như mô tả ở mục 3. Tài liệu tham khảo chỉ được tin cậy ở mức các URL
đã kiểm tra trong trường `sources`.

## Trích dẫn
```
VN-KyAm contributors (2026). VN-KyAm: Open machine-readable phonetic codebooks for Vietnamese dialects and the
languages of Viet Nam's 53 ethnic minorities (v0.1.1). CC0 1.0. https://github.com/tamhonvotri/vn-kyam-open-codebook
```
