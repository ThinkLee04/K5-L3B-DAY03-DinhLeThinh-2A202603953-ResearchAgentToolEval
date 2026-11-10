# Báo cáo cá nhân — Trần Duy Mạnh

## 1. Thông tin thành viên

- MSSV: 2A202603998
- Nhóm: MTGD; lớp: L3B.
- Email/GitHub cá nhân: duymanhtran2004mkc2@gmail.com

## 2. Phần việc phụ trách

CP3 — tool mới và unit test theo phân công do nhóm cung cấp.

## 3. Nội dung kỹ thuật của phần phụ trách

- Tool mới deduplicate chạy cục bộ, lọc URL trùng từ các item đã có, giữ bản đầu tiên và thứ tự gốc.
- So trùng bỏ fragment/host case nhưng giữ query và path case; không gộp hai bài theo nội dung và không gọi mạng.
- Có tool.py, TOOL.md, registry TOOL_FUNCTIONS và schema trong tools.yaml. Input sai hoặc lỗi parser trả error dict, không raise ra ngoài.
- Thay 3 stub tool mới bằng test thật, thêm 2 test biên: tổng 5 hàm test/12 trường hợp. CP3: contract 60 passed; toàn suite lúc chốt CP3 79 passed, 14 skipped, 0 failed.

## 4. Bằng chứng và hỗ trợ AI

- [tool.py](../../starter_v0/tools/deduplicate/tool.py), [TOOL.md](../../starter_v0/tools/deduplicate/TOOL.md).
- [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py), [output CP3](../../starter_v0/analysis/cp3_pytest.txt).
- [B5a trong group report](group_report.md); routing được đo riêng ở CP4, không lấy unit test thay cho eval model.
- Có hỗ trợ của Codex để viết implementation, schema, tài liệu và test. Cách tự kiểm tra cần thực hiện: chạy test deduplicate, giải thích happy path/input xấu/lỗi parser và vì sao không bỏ query khi so trùng.

## 5. Tự đánh giá

Đánh giá kỹ thuật dựa trên bằng chứng: tool đủ implementation/tài liệu/registry/schema, hơn 3 test và không có test mới bị skip. Quy tắc giữ query/path tránh gộp nhầm nguồn; tool chưa so trùng nội dung hoặc theo redirect.

Kiến thức cần tự giải thích: kiểm tra input từ model, trả error dict, thiết kế happy path và failure path, phân biệt unit test với eval routing. Test dự phòng lỗi mất query không phải bằng chứng đã tìm bug trong tool starter. Thành viên cần xác nhận bước đã tự chạy và bổ sung khó khăn/điều học được từ trải nghiệm thật trước khi nộp.
