# Báo cáo cá nhân — Nguyễn Xuân Dương

## 1. Thông tin thành viên

- MSSV: 2A202603955
- Nhóm: MTGD; lớp: L3B.
- Email/GitHub cá nhân: xuanduong20050808@gmail.com

## 2. Phần việc phụ trách

CP4 — bộ eval nhóm và phân tích kết quả theo phân công do nhóm cung cấp.

## 3. Nội dung kỹ thuật của phần phụ trách

- Bộ group có đúng 10 case: 5 single-turn và 5 multi-turn; có phase=B, failure_type, expect và metadata.what_it_tests.
- Hai case kiểm tra routing tới deduplicate. Các case khác phủ thiếu dữ liệu, hỏi policy, xác nhận/rút lại xác nhận, đổi nội dung, đổi nguồn và đổi template.
- Dùng expect args subset để chỉ kiểm tra tham số trọng tâm; kiểm tra thêm dữ liệu đầu vào/đầu ra của deduplicate trong tool_results.
- Run group có 10/10 PASS, provider_error_cases=0, measured_cases=total_cases=10. Case social_search vẫn báo thiếu RAPIDAPI_KEY: routing đúng không đồng nghĩa tool lấy dữ liệu thành công.

## 4. Bằng chứng và hỗ trợ AI

- [eval_group.json](../../starter_v0/data/eval_group.json).
- [Run group](../../starter_v0/runs/v3_B_group_openrouter_20261110T194344933599.json), [B3 trong group report](group_report.md).
- Có hỗ trợ của Codex để thiết kế case, kiểm tra cấu trúc, gọi eval và đọc run thật. Không chỉnh prompt/tools hoặc sửa kỳ vọng sau run để nâng điểm CP4.
- Cách tự kiểm tra cần thực hiện: đếm 5+5, đối chiếu expect với actual_tool_calls và xem cả tool_results; giải thích giới hạn của no_tool và multi-turn evaluator.

## 5. Tự đánh giá

Đánh giá kỹ thuật dựa trên bằng chứng: bộ case đủ 5+5, có routing tới tool mới và run hợp lệ. Điểm 100% trên 10 case không phải độ chính xác chung; các kiểm tra output/manual_check cũng không tự động được tính bởi scorer hiện tại.

Kiến thức cần tự giải thích: chọn expect tối thiểu, phân biệt no_tool với chất lượng câu trả lời, đọc tool_results thay vì chỉ nhìn PASS. Thành viên cần xác nhận case đã tự kiểm tra và bổ sung khó khăn/điều học được từ trải nghiệm thật trước khi nộp.
