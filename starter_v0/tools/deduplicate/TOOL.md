---
name: deduplicate
track: core
kind: local_formatter
provider: python_stdlib
requires_env: []
inputs: [items]
outputs: [items, input_count, unique_count, removed_count]
side_effect: false
---
# deduplicate

Tool mới cho CP3: lọc nguồn trùng URL từ các kết quả đã thu thập trước khi
đưa vào `format`. Không gọi mạng, không cần key, không ghi file.

## Khi dùng / khi không dùng

- Dùng khi user muốn loại nguồn trùng, hoặc danh sách kết quả đã có nhiều URL
  cùng một bài. Giữ bản đầu tiên và thứ tự xuất hiện.
- Không dùng để tìm bài mới, đọc URL, tóm tắt, xác thực nguồn hay so sánh nội
  dung hai bài. Hai URL khác nhau có thể cùng nội dung nhưng vẫn được giữ.

## Input và quy tắc

`items` là list các object; mỗi object phải có `url` dạng chuỗi HTTP(S) tuyệt đối,
không rỗng và không chứa thông tin đăng nhập. Các field khác như title, summary,
source, section được giữ nguyên. List rỗng là hợp lệ; thiếu `items` là lỗi input.

Khóa so trùng bỏ khoảng trắng đầu/cuối và fragment (`#...`), không phân biệt
hoa/thường ở scheme/host. Không gộp khác scheme, path, query hoặc port; không
bỏ tracking query, không theo redirect và không so nội dung bài. URL/item gốc
được giữ nguyên để trích nguồn; không sửa danh sách đầu vào.

Ví dụ: `https://EXAMPLE.com/article#intro` và
`https://example.com/article#end` chỉ giữ item đầu tiên.

## Output và lỗi

Thành công trả `tool`, `items`, `input_count`, `unique_count`, `removed_count`.
Ví dụ 3 item có 1 nguồn trùng sẽ có input_count=3, unique_count=2, removed_count=1.

Input sai hoặc URL khiến parser lỗi trả `{tool, error, message}`, không raise
ra ngoài. Nếu một item lỗi, cả lời gọi trả lỗi; không âm thầm bỏ item hoặc trả
một phần kết quả.

## Kiểm tra offline

Chạy từ `starter_v0/`:

```powershell
.\.venv312\Scripts\python.exe -B -m pytest tests/test_tools_todo.py -k deduplicate -v -p no:cacheprovider
```

Các test gồm happy path, input xấu, lỗi parser, list rỗng và giữ riêng các URL
khác path/query. CP4 sẽ kiểm tra model có route tới tool này khi cần hay không.
