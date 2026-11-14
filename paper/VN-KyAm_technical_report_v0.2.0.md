# VN-KyAm: Bảng Mã Ký Âm Mở cho các phương ngữ tiếng Việt và ngôn ngữ của 53 dân tộc thiểu số Việt Nam

**Báo cáo kỹ thuật v0.2.0 — 14/11/2026 — Giấy phép CC0 1.0 (public domain)**

Video demo: https://youtu.be/jJ50J8sL5po

## Tóm tắt (Abstract)
Chúng tôi công bố VN-KyAm, bộ 107 "bảng mã ký âm" máy đọc được (JSON + CSV), gồm 9 giọng tiếng Việt và 98 ngôn
ngữ / biến thể thuộc đủ 53 dân tộc thiểu số được công nhận ở Việt Nam. Bộ mã kèm theo một schema chung và các công cụ để chuyển lời
sang cách viết theo giọng vùng miền, chống gãy từ do tokenizer, và phát hiện cưỡng âm (lệch thanh điệu – giai điệu)
theo từng giọng. Bảng phương ngữ Nam Bộ do con người soạn, dựa trên kinh
nghiệm fine-tune một mô hình giọng hát. 106 bảng còn lại do mô hình ngôn ngữ lớn soạn có tra cứu web, rồi được một mô
hình thứ hai phản biện độc lập. Mọi mục đều gắn mức tin cậy và trạng thái thẩm định. Toàn bộ được hiến tặng vào phạm vi
công cộng để không ai có thể độc quyền hóa cách mô tả kỹ thuật này. Đây là bản công bố sớm để cộng đồng sửa, chưa phải
nghiên cứu đã được người bản xứ kiểm chứng.

*English:* VN-KyAm releases 107 machine-readable phonetic codebooks into the public domain (CC0): nine Vietnamese
regional varieties and 98 languages/varieties covering all 53 recognised ethnic minorities of Viet Nam. The release also includes a shared
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

### 3.2. 106 bảng còn lại (LLM soạn, có phản biện chéo)
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
| Số bảng mã | 107 (9 giọng tiếng Việt + 98 ngôn ngữ / biến thể của 53 dân tộc thiểu số) |
| Hợp lệ schema | 107/107 |
| Có mã ISO 639-3 | 107/107 |
| Ngữ hệ | Nam Á 50, Tai–Kadai 25, Hán–Tạng 14, Nam Đảo 10, H'Mông–Dao 8 |
| Điểm phản biện của Argon | 9–9.5/10: 57 bảng; 8–8.8/10: 48 bảng; chưa chấm: 2 (bảng Nam Bộ do con người soạn; `xo-dang-moo` do API hết hạn mức) |
| Quyết định phản biện | APPROVE 12, MODIFY 93 (đã áp dụng bản sửa), REJECT 0 |

### 4.1. Chống gãy từ (tokenizer)
Áp toàn bộ quy tắc mức `full` của giọng Nam Bộ lên lời bài "Còn Đâu Câu Ví Dầu", rồi đo bằng tokenizer `qwen.tiktoken`
của YuE2-3B:
- Có 22 từ bị đổi cách viết. 11 từ bị cắt thành nhiều token hơn (ví dụ tình→từn, quên→wên, tàn→tàng, ví→dí).
- Với mức `light`, chỉ 1 từ bị đổi và không từ nào bị cắt vụn.
- Trên câu mẫu trong `docs/img/token_safe_mode.png`, 10/13 cách viết đầy đủ bị gãy.

Chế độ `apply_respelling.py --safe` so sánh số token trước/sau cho từng từ và tự giữ chính tả chuẩn khi cách viết mới bị
cắt vụn hơn. Khuyến nghị: với mô hình đã fine-tune theo giọng, dùng `light` hoặc `--safe` và để khẩu âm cho embedding /
LoRA; mức `full` phù hợp cho mô hình chưa fine-tune hoặc để tham khảo.

### 4.2. Phát hiện cưỡng âm theo giọng vùng miền
`tools/cuong_am_check.py` xét từng cặp chữ liền nhau:
- Độ cao của mỗi thanh lấy theo trung bình số Chao trong bảng mã của **đúng giọng đang xét**.
- So hướng thay đổi độ cao thanh với hướng của giai điệu (bán cung), có vùng chết 0.5 bậc Chao.
- Phân loại: cùng chiều (similar), ngang (oblique) hoặc ngược chiều (contrary). Ngược chiều được báo là cưỡng âm.

Cách tiếp cận theo hướng chuyển tiếp này dựa trên Kirby & Ladd (2016). Trong một corpus 20 bài nhạc pop Việt, hai tác giả
cho thấy chuyển động cùng chiều chiếm ưu thế (khoảng 77% ở mô hình tốt nhất) và chuyển động ngược chiều bị tránh.

Ví dụ minh họa (tự soạn) "em nhớ mãi câu hò trên sông vắng lặng":
- Giọng Hà Nội chỉ có 1 chỗ cưỡng âm ("vắng → lặng" khi "lặng" đặt trên D5). Hạ "lặng" xuống G4 thì hết.
- Giọng Nam Bộ còn thêm "nhớ → mãi" và "mãi → câu", vì ngã nhập với hỏi (đường nét trũng).
- Giọng Huế có nhiều cảnh báo hơn, vì thanh ngang cao và thanh sắc thấp. Đây cũng là chỗ số Chao của bảng Huế cần người
  bản xứ xác nhận.

Công cụ là heuristic để gợi ý; chưa được đánh giá trên corpus có nhãn của nhạc sĩ.

## 5. Giới hạn (xin đọc kỹ)
1. **Chưa có người bản xứ thẩm định.** 106/107 bảng do LLM soạn. Phản biện chéo bằng một LLM khác giúp giảm lỗi nhưng
   không thay được người bản xứ. Mục `confidence: low` và các mục trong `validation.open_issues` không nên coi là sự thật.
2. **Phương ngữ là phổ liên tục.** Quy tắc `common` không có nghĩa là mọi người trong vùng đều nói như vậy. Mỗi bảng
   lấy một giọng đại diện (ví dụ Huế cho Trung Bộ).
3. **Một dân tộc có thể dùng nhiều ngôn ngữ.** Mỗi bảng chọn biến thể chính ở Việt Nam, các biến thể khác nằm trong
   `ml_hints.sub_varieties`.
4. **Ký hiệu ABC cho luyến láy** phần lớn là đề xuất kỹ thuật, chưa được nghệ nhân xác nhận.
5. **Không dùng điểm của bộ phân loại giọng vùng miền tự động làm bằng chứng khẩu âm.** Trong thực nghiệm, điểm
   "% giọng Nam" tăng từ khoảng 62% lên khoảng 84% chỉ nhờ mix/EQ hậu kỳ, không đổi gì ở mô hình.
6. Kỹ thuật chuyển vector embedding theo từ cùng vần (`vie-south.json`) **chưa có thí nghiệm đối chứng (ablation)**.

7. Bộ kiểm tra cưỡng âm dùng độ cao trung bình của thanh, chưa xét luyến láy nhiều nốt trong một chữ, nhịp hay trọng âm câu.

## 6. Đóng góp
Sửa file JSON và chạy `python3 tools/build_release.py`. Người bản xứ hoặc chuyên gia sau khi kiểm tra thì đặt
`validation.native_speaker_reviewed` / `linguist_reviewed` = `true` và ghi vào `provenance.reviewers`. Mọi đóng góp đều
được phát hành theo CC0.

## 7. Lời cảm ơn
Trân trọng cảm ơn nhạc sĩ Đông Hải, ca sĩ Đông Đào và ca sĩ Thảo Vy đã hỗ trợ kinh nghiệm và các bản thu phục vụ nghiên cứu
khẩu âm Nam Bộ. Các bản thu không được phân phối trong repo. Cảm ơn tác giả bộ dữ liệu mở VieNeu-TTS (Phạm Nguyễn Ngọc
Bảo), được dùng làm nguồn đối chiếu phát âm tiếng Việt nhiều giọng nói trong quá trình nghiên cứu.

## 8. Công bố về việc dùng AI
Báo cáo, schema và công cụ do một AI coding agent soạn theo yêu cầu và dưới sự giám sát của chủ dự án. 106 bảng mã do
Gemini 4 Carbon soạn và Gemini 4 Argon phản biện, như mô tả ở mục 3. Tài liệu tham khảo chỉ được tin cậy ở mức các URL
đã kiểm tra trong trường `sources`.

## Trích dẫn
```
VN-KyAm contributors (2026). VN-KyAm: Open machine-readable phonetic codebooks for Vietnamese dialects and the
languages of Viet Nam's 53 ethnic minorities (v0.2.0). CC0 1.0. https://github.com/tamhonvotri/vn-kyam-open-codebook
```

## Tài liệu tham khảo chính
- Pham Nguyen Ngoc Bao (2025). VieNeu-TTS: Vietnamese Multi-Speaker Text-to-Speech Dataset. Hugging Face. https://huggingface.co/datasets/pnnbao-ump/VieNeu-TTS (140.7 giờ, 193 người nói, Apache 2.0).
- Kirby, J. & Ladd, D. R. (2016). Tone-melody correspondence in Vietnamese popular song. TAL 2016, 48–51. https://doi.org/10.21437/TAL.2016-10
- Vũ Thanh Phương (1982). Phonetic properties of Vietnamese tones across dialects. Pacific Linguistics A-62, 55–76. https://doi.org/10.15144/PL-A62.55
- Kirby, J. P. (2011). Vietnamese (Hanoi Vietnamese). JIPA 41(3), 381–392. https://doi.org/10.1017/S0025100311000181
- Brunelle, M. (2009). Tone perception in Northern and Southern Vietnamese. Journal of Phonetics 37(1), 79–96.
- Hoàng Thị Châu (2004). Phương ngữ học tiếng Việt. NXB ĐHQG Hà Nội.
- Đoàn Thiện Thuật (2003). Ngữ âm tiếng Việt. NXB ĐHQG Hà Nội.
- Cao Xuân Hạo (1998). Tiếng Việt — Mấy vấn đề ngữ âm, ngữ pháp, ngữ nghĩa. NXB Giáo dục.
- Võ Xuân Trang (1997). Phương ngữ Bình Trị Thiên. NXB KHXH.
- Trần Văn Khê (1962). La musique vietnamienne traditionnelle. PUF.
- Phạm Duy (1975). Musics of Vietnam. Southern Illinois University Press.
- Hammarström, H. et al. Glottolog 5; Moran, S. & McCloy, D. (2019) PHOIBLE 2.0; Eberhard, D. M. et al. Ethnologue.
- Yuan, R. et al. (2025). YuE: Scaling Open Foundation Models for Long-Form Music Generation. arXiv:2503.08638.

Xem danh sách đầy đủ trong README.
