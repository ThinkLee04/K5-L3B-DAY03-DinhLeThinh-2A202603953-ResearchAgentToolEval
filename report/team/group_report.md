# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline, giữ nguyên prompt/tools | Đo hành vi ban đầu trước tối ưu | — | case 70%; routing 75%; argument 70%; multiturn 100% | [run v0](../../starter_v0/runs/v0_B_base_openrouter_20261110T183327338860.json) |
| v1 | Chỉ thay đoạn missing-info trong system_prompt.md; tools.yaml giữ nguyên | Kiểm tra lịch sử rồi hỏi clarify khi thiếu account/URL sẽ giảm lỗi missing_info | case 70%; routing 75%; argument 70%; multiturn 100% | case 90%; routing 95%; argument 90%; multiturn 100% | [run v1](../../starter_v0/runs/v1_B_base_openrouter_20261110T183700179348.json) |
| v2 | Chỉ thay đoạn gửi/đăng trong system_prompt.md; tools.yaml giữ nguyên | Yêu cầu clarify yes_no xác nhận đúng nội dung trước send sẽ cải thiện boundary R12 | case 90%; routing 95%; argument 90%; multiturn 100% | case 80%; routing 100%; argument 80%; multiturn 100% | [run v2](../../starter_v0/runs/v2_B_base_openrouter_20261110T184432280335.json) |
| v3 | Chỉ thêm response_type vào required của clarify trong tools.yaml; prompt giữ nguyên | Bắt buộc trường response_type trong schema sẽ giảm lỗi bỏ sót argument | case 80%; routing 100%; argument 80%; multiturn 100% | case 95%; routing 100%; argument 95%; multiturn 100% | [run v3](../../starter_v0/runs/v3_B_base_openrouter_20261110T184713647924.json) |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Baseline ngày 10/11/2026, OpenRouter / `openai/gpt-4o-mini`: 14/20 case PASS; `provider_error_cases=0`, `measured_cases=total_cases=20`. Các nhận định nguyên nhân bên dưới là giả thuyết từ log và prompt starter, chưa được kiểm chứng bằng v1. Bảng chỉ đề xuất sửa; chưa thay đổi prompt/tools.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send(text=...)` | Kỳ vọng không gọi tool; model dùng send cho yêu cầu toán học | Làm rõ phạm vi research và khi nào không gọi tool |
| R10_missing_handle | missing_info | `timeline(screenname="sama")` | Tự đoán tài khoản thay vì clarify | Bỏ chỉ dẫn đoán; hỏi lại khi thiếu account |
| R11_missing_url | missing_info | `fetch(url="https://example.com/article")` | Tự tạo URL thay vì clarify | Hỏi URL/nội dung; không tự dựng URL |
| R12_confirm_before_send | wrong_boundary | `send(text=...)` | Kỳ vọng clarify yes_no trước khi gửi; code trả needs_confirmation | Thêm quy tắc xác nhận và description send rõ ràng |
| R13_parallel_web_and_tweets | wrong_tool (nhãn case); observed: wrong_arg_value | `lookup(query="AI news", timeframe="day", max_results=5)` + `social_search(query="AI", search_type="Latest", limit=5)` | Routing đúng; query kỳ vọng AI, thực tế AI news; thiếu topic=news | Làm rõ convention topic/query; ghi nhận phép so sánh query chặt của eval |
| R14_out_of_scope_coding | out_of_scope | `send(text=code Fibonacci)` | Kỳ vọng không gọi tool; model dùng send cho yêu cầu lập trình | Giới hạn phạm vi và không dùng send làm công cụ trả lời chung |

Giới hạn baseline: thiếu `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY`, nên các tool tra cứu trả error dict. Run hợp lệ theo điều kiện provider của rubric nhưng các metric chỉ phản ánh routing/arguments, chưa chứng minh lấy dữ liệu thật thành công. Các lời gọi send trong run này đều trả `needs_confirmation`, không có status sent. Thông tin xác thực Telegram được loại bỏ trong tiến trình sau khi nạp cấu hình để tránh gửi thật; không sửa file .env. Một lượt chạy trước đã bị dừng do phát hiện thứ tự nạp cấu hình chưa bảo đảm điều kiện này; không dùng lượt bị dừng làm bằng chứng.

#### Nhận xét v1 so với v0

- Cùng OpenRouter / `openai/gpt-4o-mini`, base 20 case; v1 có `provider_error_cases=0`, `measured_cases=total_cases=20`. Contract test: 55 passed. `tools_hash` giữ nguyên, `prompt_hash` thay đổi.
- Đúng một giả thuyết: thay đoạn khuyến khích đoán bằng quy tắc kiểm tra ngữ cảnh, gọi clarify với response_type=text khi thiếu account/URL, không hỏi lại nếu đã có thông tin. Chưa sửa boundary gửi, phạm vi hoặc quy tắc số lượng tool.
- R10 chuyển FAIL → PASS: hỏi tài khoản thay vì tự đoán sama.
- R11 đã chọn clarify và hỏi URL, nhưng vẫn FAIL vì model không truyền response_type. Hàm Python mặc định text, còn eval so args thô nên coi trường bị bỏ qua là None. Đây là tiến bộ về hành vi nhưng chưa đạt tiêu chí arguments.
- R12 vẫn gọi send thay vì hỏi xác nhận; code trả needs_confirmation. Boundary gửi nằm ngoài giả thuyết v1, cần vòng tối ưu riêng.
- R08, R13, R14 cũng chuyển sang PASS; chưa đủ bằng chứng quy toàn bộ mức tăng 20 điểm phần trăm cho cơ chế hỏi lại. Chỉ có một run mỗi version; model có thể biến thiên dù temperature=0. Không có case PASS của v0 chuyển thành FAIL ở v1; 6 case multi-turn giữ PASS.
- Giả thuyết được hỗ trợ một phần: cả R10/R11 đều chuyển sang clarify; số case missing_info FAIL giảm 2 → 1. Giới hạn tool API thiếu cấu hình vẫn còn; không diễn giải accuracy là lấy dữ liệu thật thành công. Telegram được vô hiệu hóa trong tiến trình giống run v0 được chọn.

#### Nhận xét v2 so với v1

- Đúng một giả thuyết: thay quy tắc gửi ngay bằng yêu cầu trình bày nội dung, hỏi clarify yes_no và chỉ send confirmed=true sau khi user xác nhận đúng nội dung; nội dung thay đổi cần xác nhận lại. Giữ nguyên đoạn missing-info, quy tắc một bước và toàn bộ tools.yaml.
- Cùng OpenRouter / `openai/gpt-4o-mini`, base 20 case; `provider_error_cases=0`, `measured_cases=total_cases=20`. Contract test 55 passed; tools_hash giữ nguyên, prompt_hash thay đổi. Telegram vô hiệu hóa trong tiến trình sau khi nạp cấu hình như v1.
- R12 chuyển từ send sang clarify, nhưng model hỏi bổ sung nội dung bằng response_type=text; eval kỳ vọng yes_no nên vẫn FAIL. Đây là tiến bộ về routing, chưa chứng minh luồng xác nhận hoàn chỉnh. Yêu cầu case không có nội dung bản tin cụ thể nên hỏi nội dung có lý về mặt hội thoại; cần review thủ công ngoài điểm tự động. Không sửa case base để nâng điểm.
- R10 chuyển PASS → FAIL do bỏ response_type=text; R11 tiếp tục thiếu cùng tham số. Cả hai vẫn hỏi lại đúng thông tin, không đoán account/URL. Hàm có default text nhưng eval kiểm tra arguments thô.
- R13 chuyển PASS → FAIL vì thiếu topic=news. Tất cả 4 case FAIL của v2 đều observed_mismatch=wrong_arg_value. Không có case FAIL của v1 chuyển thành PASS ở v2; 6 case multi-turn vẫn PASS.
- Case accuracy giảm 90% → 80%, routing tăng 95% → 100%, argument giảm 90% → 80%. Giữ nguyên kết quả thay vì sửa thêm trong cùng version. Giả thuyết chỉ được hỗ trợ ở mức chọn clarify; chưa đạt kỳ vọng yes_no. Một run mỗi version không đủ khẳng định quan hệ nhân quả cho các biến động ngoài R12.
- Tool tra cứu vẫn có RuntimeError; không diễn giải routing 100% là API tool hoạt động thành công. V2 chưa kiểm tra tình huống user đã xác nhận rồi gửi; cần eval nhóm/live chat ở checkpoint sau.

#### Nhận xét v3 so với v2

- Đúng một giả thuyết: thêm response_type vào required của clarify, từ `[question]` thành `[question, response_type]`. Không đổi description, default, enum hoặc prompt. Schema yêu cầu model truyền tham số; không bổ sung runtime validation hay strict mode.
- Cùng OpenRouter / `openai/gpt-4o-mini`, base 20 case; `provider_error_cases=0`, `measured_cases=total_cases=20`. Contract test 55 passed. prompt_hash giữ nguyên so với v2; tools_hash thay đổi. Telegram vô hiệu hóa trong tiến trình như v2.
- R10 và R11 đều truyền response_type=text và chuyển FAIL → PASS. Cả ba lời gọi clarify (R10/R11/R12) đều có response_type: hỗ trợ giả thuyết giảm bỏ sót trường trong run này.
- R12 vẫn hỏi bổ sung nội dung bằng response_type=text; kỳ vọng yes_no nên tiếp tục FAIL. Bắt buộc có trường không bảo đảm chọn đúng giá trị. Chưa chứng minh luồng xác nhận/gửi hoàn chỉnh; không sửa eval để nâng điểm.
- R13 chuyển PASS dù schema lookup không đổi; chưa đủ bằng chứng quy cải thiện đó cho required của clarify. Không có case PASS của v2 chuyển thành FAIL. Case accuracy tăng 80% → 95%, argument tăng 80% → 95%; routing 100% và 6 case multi-turn PASS giữ nguyên. Một run mỗi version chưa loại trừ biến thiên model.
- Vẫn có RuntimeError của API tool; 95% là điểm lựa chọn tool/arguments, không phải tỷ lệ research thành công. Đã có bằng chứng v0–v3 nhưng CP2 chưa đủ toàn bộ: cần xử lý description/convention/boundary trong tools.yaml và quy tắc ép một bước trong prompt ở các vòng tiếp theo, mỗi vòng có giả thuyết và log riêng.

### B3. Team Eval Cases


Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
