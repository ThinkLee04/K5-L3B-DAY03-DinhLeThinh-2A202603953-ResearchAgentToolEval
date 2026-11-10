# Báo cáo cá nhân — Trần Thị Hồng Gấm

## 1. Thông tin thành viên

- MSSV: 2A202603967
- Nhóm: MTGD; lớp: L3B.
- Email/GitHub cá nhân: chưa cung cấp.

## 2. Phần việc phụ trách

CP5 — UI, live chat và báo cáo theo phân công do nhóm cung cấp.

## 3. Nội dung kỹ thuật của phần phụ trách

- Streamlit UI dùng lại run_model_tool_loop của chat.py; giữ lịch sử riêng mỗi phiên và ghi transcript sau từng lượt.
- Hiển thị lời gọi tool, kết quả/lỗi, trạng thái hỏi lại; cho tải transcript và tạo hội thoại mới.
- Thêm Streamlit vào requirements.txt, mở link Cloudflare Tunnel; HTTP và WebSocket public đã qua kiểm tra. Người dùng xác nhận người ngoài nhóm đã dùng thử thành công.
- Có 5 lượt CLI gọi API thật: tra policy, hỏi danh sách còn thiếu, nhận danh sách và lọc trùng, hỏi xác nhận gửi, hủy gửi. Không có lời gọi send; Telegram thật được tắt trong demo.
- Bốn test UI offline kiểm tra khởi tạo không gọi model, giữ ngữ cảnh, hiển thị lỗi và tách hội thoại. Toàn suite: 83 passed, 14 skipped, 0 failed.

## 4. Bằng chứng và hỗ trợ AI

- [app.py](../../starter_v0/app.py), [requirements.txt](../../starter_v0/requirements.txt), [test_ui.py](../../starter_v0/tests/test_ui.py).
- [Transcript CLI thật](../../starter_v0/transcripts/v3_openrouter_20261110T195341244321.transcript.json).
- [Output pytest](../../starter_v0/analysis/cp5_pytest.txt), [A1/B4/B5a trong group report](group_report.md).
- Có hỗ trợ của Codex để viết UI/test, vận hành CLI/tunnel và tổng hợp bằng chứng. Test UI dùng fake model chỉ là test offline; transcript được dẫn ở trên dùng model thật.
- Cách tự kiểm tra cần thực hiện: chạy UI theo A1, thử câu hỏi mẫu và mở tool result/transcript để đối chiếu. Không diễn giải lỗi API là lấy dữ liệu thành công.
- Commit kỹ thuật cá nhân: cần thành viên dẫn commit thực tế trước khi nộp.

## 5. Tự đánh giá

Đánh giá kỹ thuật dựa trên bằng chứng: UI, dependency, link dùng thử, transcript 5 lượt CLI và test đã có; người ngoài nhóm đã dùng thử theo xác nhận của người dùng. Cần giữ rõ giới hạn của tunnel tạm thời và việc tool mạng có thể lỗi dù model đã chọn đúng tool.

Kiến thức cần tự giải thích: vòng lặp model→tool→model, trạng thái chờ người dùng, cách lưu lịch sử và cách hiển thị lỗi. Thành viên cần xác nhận bước đã tự chạy và bổ sung trải nghiệm thật. Chưa có bằng chứng để khẳng định Phần A hoàn thành trước mốc showdown 16:30; nhóm cần đối chiếu lịch lớp khi nộp.
