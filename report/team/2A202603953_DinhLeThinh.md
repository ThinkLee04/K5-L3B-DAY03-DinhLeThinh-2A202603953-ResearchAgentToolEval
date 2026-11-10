# Báo cáo cá nhân — Đinh Lê Thịnh

## 1. Thông tin thành viên

- MSSV: 2A202603953
- Nhóm: MTGD; lớp: L3B.
- Email/GitHub cá nhân: dinhlethinh137@gmail.com

## 2. Phần việc phụ trách

CP2 — tối ưu system prompt và tool declaration, đọc lỗi và ghi version log theo phân công do nhóm cung cấp.

## 3. Nội dung kỹ thuật của phần phụ trách

- Phân biệt quy tắc chung trong system prompt với mô tả/schema của từng tool.
- Trong chuỗi hiện có, v1 thay quy tắc đoán bằng hỏi lại; v2 yêu cầu xác nhận đúng nội dung trước gửi; v3 bắt buộc clarify.response_type.
- Kết quả base trong version log: v0 70%, v1 90%, v2 80%, v3 95%. Version giảm điểm vẫn được giữ và phân tích, không thay số liệu để làm đẹp báo cáo.
- Lỗi còn lại R12 cần phân biệt hỏi nội dung với xin xác nhận; việc schema required không bảo đảm model chọn đúng giá trị.

## 4. Bằng chứng và hỗ trợ AI

- [System prompt](../../starter_v0/artifacts/system_prompt.md), [tools.yaml](../../starter_v0/artifacts/tools.yaml).
- [Version log](../../starter_v0/artifacts/version_log.csv), [B1/B2 trong group report](group_report.md).
- Có hỗ trợ của Codex để giải thích, chỉnh artifact, chạy đo và phân tích log. Các số liệu nêu trên có run thật trong repo; không phải số liệu mẫu.
- Cách tự kiểm tra cần thực hiện: mở run được dẫn trong CSV, đối chiếu hash/summary/failures và giải thích một giả thuyết mỗi version.

## 5. Tự đánh giá

Đánh giá kỹ thuật dựa trên bằng chứng: có ba vòng v1–v3 và log/hash/metric tương ứng. V3 đạt 95% trên base nhưng R12 vẫn FAIL; chưa thể coi boundary gửi đã được chứng minh đầy đủ. V2 giảm điểm cho thấy cần giữ và phân tích kết quả không thuận lợi.

Kiến thức cần tự giải thích: khác nhau giữa prompt và schema, default của hàm với arguments model thực sự gửi, và lý do mỗi version chỉ thử một giả thuyết. Bản đánh giá này dựa trên log; thành viên cần xác nhận các bước đã tự làm và bổ sung trải nghiệm/khó khăn thật trước khi nộp.
