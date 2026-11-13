# VN-KyAm — Bảng Mã Ký Âm Mở Việt Nam
### Open, machine-readable phonetic codebooks for Vietnamese regional varieties and the languages of Viet Nam's 53 ethnic minorities

**Giấy phép: CC0 1.0 Universal (Public Domain Dedication).** Toàn bộ dữ liệu, schema, công cụ và tài liệu trong thư mục
này được hiến tặng vào phạm vi công cộng. Bất kỳ ai cũng được sao chép, sửa đổi, phân phối, dùng cho mục đích thương mại
mà không cần xin phép hay trả phí. Xem [LICENSE](LICENSE).

> **Tuyên bố công bố (Publication statement).** Tài liệu này được công bố công khai nhằm đưa các quy tắc ký âm giọng vùng miền
> tiếng Việt và các bảng chữ–âm của ngôn ngữ dân tộc thiểu số Việt Nam vào phạm vi công cộng, để không cá nhân hay tổ chức nào
> có thể độc quyền hóa các quy tắc này. Bản thân tiếng nói, phương ngữ và chữ viết của các cộng đồng là tài sản chung của
> cộng đồng; bộ mã này chỉ là một cách mô tả kỹ thuật, không xác lập quyền sở hữu nào đối với ngôn ngữ.
> Ngày công bố bản đầu tiên: xem `CHANGELOG.md`; dấu vân tay nội dung: `dist/SHA256SUMS`.

## Có gì bên trong

| Thành phần | Mô tả |
|---|---|
| `codebooks/vietnamese/` | 5 phương ngữ tiếng Việt: Bắc Bộ (mốc), Bắc Trung Bộ, Trung Bộ (Huế), Nam Trung Bộ, Nam Bộ |
| `codebooks/minority/` | 53 ngôn ngữ của 53 dân tộc thiểu số được công nhận |
| `schema/codebook.schema.json` | JSON Schema chung |
| `dist/` | Bản gộp: `index.json`, `vn_kyam_all.json`, CSV (tương ứng âm, quy tắc chuyển chữ, chữ–IPA, thanh điệu, xấp xỉ Quốc ngữ), `SHA256SUMS` |
| `tools/apply_respelling.py` | Chuyển văn bản tiếng Việt chuẩn sang cách viết theo giọng vùng miền |
| `tools/tokenizer_check.py` | Đo xem cách viết mới có làm tokenizer cắt vụn từ hay không |
| `tools/generate_codebooks.py` | Pipeline tạo/mở rộng bảng mã bằng LLM có tra cứu web + phản biện chéo |
| `tools/build_release.py` | Kiểm schema và đóng gói `dist/` |
| `SKILL.md` | Hướng dẫn cho AI agent |
| `paper/` | Báo cáo kỹ thuật ([v0.1.1](paper/VN-KyAm_technical_report_v0.1.1.md)) |

Mỗi bảng mã gồm: mã ISO 639-3 / Glottocode, ngữ hệ, chữ viết (kèm Unicode block); âm đầu, nguyên âm, âm cuối (chữ → IPA);
thanh điệu (số Chao) hoặc âm vực; với phương ngữ tiếng Việt thì có thêm **tương ứng âm so với chuẩn** và **quy tắc chuyển chữ máy chạy
được**; với ngôn ngữ dân tộc thì có thêm **cách viết xấp xỉ bằng chữ Quốc ngữ** (cho mô hình TTS/giọng hát chỉ biết tiếng Việt);
từ vựng địa phương; âm nhạc dân gian (thể loại, luyến láy, nhạc cụ); gợi ý cho ML; nguồn tham khảo; trạng thái thẩm định.

## Dùng nhanh

```bash
# Chuyển lời sang giọng Nam Bộ (mức an toàn cho tokenizer)
python3 tools/apply_respelling.py --codebook codebooks/vietnamese/vie-south.json --level light "Trăng ơi buồn nhớ ai, cũ kỹ say tay"

# Mô phỏng khẩu âm đầy đủ bằng chữ (giọng Huế), kèm quy tắc tùy chọn
python3 tools/apply_respelling.py --codebook codebooks/vietnamese/vie-central.json --level full --include-optional < loi.txt

# Kiểm tra tokenizer (mặc định: qwen.tiktoken của YuE2-3B; hoặc --hf <model>)
python3 tools/tokenizer_check.py --codebook codebooks/vietnamese/vie-south.json --level full --text-file loi.txt
```

```python
import json
idx = json.load(open("dist/index.json"))
tay = json.load(open("codebooks/minority/tay.json"))
print(tay["phonology"]["tones"])
```

## Mức độ tin cậy — xin đọc trước khi dùng

| Trạng thái | Ý nghĩa |
|---|---|
| `empirical-partial` | `vie-south.json`: do con người soạn; phần `ml_hints` rút ra từ thực nghiệm mô hình giọng hát YuE2 + LoRA |
| `draft-llm` | Do Gemini 4 Carbon soạn (có Google Search), Gemini 4 Argon phản biện độc lập và sửa. **Chưa có người bản xứ / nhà ngôn ngữ học thẩm định.** |

- Mọi mục đều có trường `confidence` (`high` / `medium` / `low`). Mục `low` và các mục trong `validation.open_issues` không nên coi là sự thật.
- `validation.llm_review` ghi lại toàn bộ nhận xét của mô hình phản biện; `build_logs/` lưu truy vấn tìm kiếm đã dùng.
- Phương ngữ là phổ liên tục: một quy tắc `common` không có nghĩa là mọi người nói trong vùng đều phát âm như vậy.
- Bộ mã dân tộc thiểu số được tạo **để cộng đồng sửa và hoàn thiện**. Rất mong người bản xứ, nghệ nhân và nhà nghiên cứu góp ý.

## Đóng góp
1. Sửa file JSON tương ứng (giữ đúng schema).
2. Nếu bạn là người bản xứ / chuyên gia đã kiểm tra: đặt `validation.native_speaker_reviewed` hoặc `linguist_reviewed` = `true`
   và ghi vào `provenance.reviewers` (tên hoặc bí danh, ngày).
3. Chạy `python3 tools/build_release.py`.

Mọi đóng góp đều được phát hành dưới CC0.

---

## English summary
VN-KyAm is a public-domain (CC0) set of machine-readable phonetic codebooks for five Vietnamese regional varieties and the
languages of Viet Nam's 53 officially recognised ethnic minorities. Each codebook gives the script(s), a grapheme-to-IPA mapping,
the tones or registers, folk-music notes and ML hints. Vietnamese-variety codebooks also give sound correspondences relative
to the standard and respelling rules you can apply automatically. Minority-language codebooks also give a Quốc ngữ
approximation for Vietnamese-only TTS and singing models.
The Southern codebook is hand-authored. All other codebooks are LLM-drafted with web-search grounding, cross-reviewed by a
second LLM, and **not yet validated by native speakers**. Every entry carries a confidence level. Corrections are welcome.

