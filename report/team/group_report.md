# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: MTGD; lớp L3B.
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3 và CP5: OpenRouter / openai/gpt-4o-mini.

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent hỗ trợ tra cứu policy nội bộ, tìm nguồn web/X/arXiv, đọc nguồn, lọc URL trùng và trình bày digest. Demo đã kiểm tra policy và lọc trùng; các tool gọi dịch vụ ngoài cần key riêng, và Telegram được tắt trong UI để không gửi tin thật.

**Cách chạy UI:**

Chạy từ starter_v0; dependency `streamlit>=1.40.0,<2.0` đã thêm vào requirements.txt và cài trong .venv312:

```powershell
.\.venv312\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --server.fileWatcherType none --browser.gatherUsageStats false
```

Local: http://127.0.0.1:8501 . UI giữ hội thoại riêng từng phiên, hiển thị lỗi/tool result, lưu transcript sau mỗi lượt và cho tải JSON. Provider/model cố định theo cấu hình demo; không nhập key trong giao diện. Nếu đổi .env, khởi động lại server để nạp cấu hình mới.

**Link dùng thử (deploy):**

https://complimentary-concert-sustainable-factors.trycloudflare.com

Link tạm thời của Cloudflare Quick Tunnel, có hiệu lực trong khi máy, Streamlit và cloudflared còn chạy. Mở terminal thứ hai sau khi cài cloudflared và chạy:

```powershell
cloudflared tunnel --url http://127.0.0.1:8501 --protocol http2
```

Khởi chạy tunnel mới có thể tạo URL khác; cập nhật link trước khi demo. Link hiện tại đã trả HTTP 200, health=ok và WebSocket handshake thành công, có [bằng chứng kiểm tra runtime](../../starter_v0/analysis/cp5_runtime_check.json). Người dùng xác nhận người ngoài nhóm đã dùng UI thành công trên URL tunnel trước; khi tunnel đó mất kết nối và báo Tunnel not found, đã tạo lại URL ở trên và kiểm tra lại HTTP/WebSocket. Chưa có bằng chứng để xác nhận Phần A hoàn thành trước mốc showdown 16:30; nhóm cần đối chiếu lịch lớp, không suy diễn từ thời điểm tạo file.

### A2. Tool agent có

Agent có 11 tool, gồm một tool mới của nhóm:

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| deduplicate | loại nguồn trùng URL từ các item đã có, giữ bản đầu tiên | có — CP3 |
| timeline | lấy tweet theo tài khoản, cần RapidAPI | không |
| social_search | tìm tweet theo chủ đề, cần RapidAPI | không |
| lookup | tìm web/tin tức, cần Tavily | không |
| fetch | đọc một URL, cần Firecrawl | không |
| format | trình bày item đã có thành markdown | không |
| policy | tra company_policy Markdown cục bộ | không |
| papers | tìm metadata/abstract paper arXiv | không |
| paper_text | tải PDF arXiv và trích text cục bộ | không |
| send | gửi Telegram sau xác nhận; bị tắt trong demo này | không |

### A3. Câu hỏi mẫu để thử

1. “Theo policy nội bộ, tweet viral có đủ để xem thông tin là đã xác minh không? Tra policy và giải thích ngắn gọn.”
2. “Chỉ lọc trùng URL: [{"title":"A","url":"https://example.com/a#intro"},{"title":"A trùng","url":"https://example.com/a#end"},{"title":"B","url":"https://example.org/b"}]. Không đọc web.”
3. “Tôi muốn lọc nguồn trùng nhưng chưa gửi danh sách. Hãy hỏi tôi danh sách cần lọc.” Sau khi agent hỏi, bổ sung danh sách ở câu 2.
4. “Bản nháp nguyên văn: 'Nhóm đọc paper lúc 19:00 thứ Sáu.' Cho tôi xem lại và hỏi có đồng ý gửi Telegram không. Chưa gửi ở lượt này.” Sau đó trả lời “Không, hủy yêu cầu”.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- CP3: thêm tool `deduplicate` để lọc nguồn trùng URL trước khi tổng hợp. Chạy cục bộ, không cần API key; chỉ xử lý các item đã có. Khi không cần lọc trùng, agent không cần gọi tool này. Implementation, schema, registry và tài liệu được đăng ký đồng bộ.
- CP5: app.py dùng lại vòng lặp của chat.py, giới hạn 4 vòng tool và 5 cặp hội thoại trong ngữ cảnh. Mỗi phiên có ID/transcript riêng; UI hiển thị kết quả/lỗi và không làm mất transcript cũ khi tạo hội thoại mới. Giữ nguyên prompt, tool implementation, eval và version log trong lần làm CP5.

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

CP4 theo CHECKPOINTS.md: [eval_group.json](../../starter_v0/data/eval_group.json) có đúng 10 case mới, gồm 5 single turn (`query`) và 5 multi turn (`turns`). Tất cả phase=B, có failure_type, expect và metadata.what_it_tests. G_S01 và G_M01 kiểm tra routing tới tool mới deduplicate.

Bằng chứng: [run group v3](../../starter_v0/runs/v3_B_group_openrouter_20261110T194344933599.json), provider OpenRouter, model openai/gpt-4o-mini. Run dùng cấu hình hiện tại sau CP3, artifact_version=`v3+p5fa7dcedc916+tab6740f9bc01`; không sửa hash/metric của các run base trước đó.

Kết quả: 10/10 PASS; case_accuracy=100%, tool_routing_accuracy=100%, argument_accuracy=100%, multiturn_accuracy=100% (5/5). Run hợp lệ: provider_error_cases=0, measured_cases=total_cases=10.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G_S01_deduplicate_provided_sources | Single: nguồn có sẵn, URL khác fragment | deduplicate; không fetch/format | PASS; kiểm tra thêm: đủ 3 item đầu vào, giữ đúng 2 nguồn đầu tiên khác nhau |
| G_S02_deduplicate_limit_explanation | Single: hỏi giới hạn lọc URL, không yêu cầu thao tác | no_tool; giải thích lọc trùng không xác minh sự thật | PASS; câu trả lời phân biệt đúng giới hạn |
| G_S03_policy_changed_approved_content | Single: hỏi policy khi sửa tiêu đề đã duyệt, chưa yêu cầu gửi | policy(policy_area=external_publishing) | PASS |
| G_S04_preview_before_confirmation | Single: có bản nháp cụ thể, chưa xác nhận | clarify(response_type=yes_no); nhắc đúng bản nháp | PASS; câu hỏi chứa nguyên văn nội dung, không gọi send |
| G_S05_missing_deduplicate_items | Single: thiếu items cho tool mới | clarify(response_type=text), không bịa nguồn | PASS |
| G_M01_deduplicate_context_items | Multi: lấy danh sách ở lượt trước để lọc | deduplicate; không yêu cầu nhập lại hay format | PASS; đủ 3 item gốc, đầu ra đúng 2 nguồn |
| G_M02_revoke_send_confirmation | Multi: thu hồi đồng ý ở lượt cuối | no_tool; xác nhận hủy, không gửi | PASS; không có send, trả lời đã hủy |
| G_M03_changed_content_needs_new_approval | Multi: duyệt A không cho phép gửi B | clarify(response_type=yes_no), xác nhận lại B | PASS; hỏi đúng nội dung 20:00, không dùng nội dung cũ 19:00 |
| G_M04_switch_source_and_ranking | Multi: web→X, giữ từ khóa, đổi Top và số lượng | social_search(query=solid-state battery, search_type=Top, limit=2) | PASS routing/args; tool trả lỗi thiếu RAPIDAPI_KEY |
| G_M05_change_format_preserve_items | Multi: đổi brief→thread và giữ hai item | format(template=thread, headline=Hai nguồn đã có) | PASS; giữ đủ 2 item, markdown có 1/ và 2/ |

Lệnh theo checkpoint, chạy từ starter_v0:

```powershell
.\.venv312\Scripts\python.exe -B run_eval.py --provider openrouter --version v3 --suite group --eval-cases data/eval_group.json
```

Trong lượt đo thực tế, dùng cùng arguments qua run_eval.main() sau khi nạp cấu hình rồi loại bỏ hai biến Telegram khỏi tiến trình để không gửi thật. Không đọc/hiển thị key hoặc sửa .env. Run không có lời gọi send nào.

Kiểm tra và giới hạn:

- Đã kiểm tra JSON, 10 ID duy nhất, tỷ lệ 5+5, đầy đủ metadata và tên/args kỳ vọng khớp registry/schema. Contract test 60 passed. Không sao chép query của base/extension.
- expect dùng args subset: chỉ chấm các tham số trọng tâm, không ép câu hỏi phải giống một câu mẫu. Hai case deduplicate chấm routing; đã đối chiếu thêm items và counts trong tool_results để xác nhận không mất dữ liệu. expected_tool_output/manual_check trong metadata là tiêu chí review thêm, evaluator hiện không tự chấm chúng.
- no_tool chỉ tự chấm việc không có lời gọi; chất lượng giải thích/hủy thao tác đã được đọc riêng trong actual_text. Multi-turn của evaluator dùng lịch sử làm ngữ cảnh và chấm lượt cuối, chưa phải một phiên chat tương tác từ đầu đến cuối.
- Case G_M04 không chứng minh lấy tweet thật thành công vì thiếu RAPIDAPI_KEY. G_M05 truyền headline đúng nhưng formatter thread hiện không hiển thị headline; giữ nguyên code và ghi nhận giới hạn thay vì sửa tool trong CP4.
- Đây là kết quả một run trên bộ case này, không chứng minh độ tin cậy chung hoặc luồng gửi Telegram hoàn chỉnh. Không thay prompt, tools, dependencies, version log, base/extension hoặc làm UI trong CP4.

### B4. Live Chat Evidence

Đã vận hành chat.py với provider thật, không dùng sample hoặc fake provider để tạo bằng chứng. Phiên CLI: [v3_openrouter_20261110T195341244321.transcript.json](../../starter_v0/transcripts/v3_openrouter_20261110T195341244321.transcript.json), OpenRouter / openai/gpt-4o-mini, artifact_version=`v3+p5fa7dcedc916+tab6740f9bc01`. Cả 5 lượt không có provider_error.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| CLI 1 | Tra policy về tweet viral và xác minh thông tin | policy(query=tweet viral, policy_area=all) | transcript CLI v3, turn 1 | answered; tool trả policy thật, model giải thích giới hạn nguồn xã hội; 2 vòng model |
| CLI 2 | Lọc nguồn trùng nhưng chưa gửi danh sách | clarify(response_type=text) | transcript CLI v3, turn 2 | waiting_for_user; hỏi danh sách, không bịa nguồn |
| CLI 3 | Bổ sung đúng 3 item để lọc | deduplicate(items=3 item) | transcript CLI v3, turn 3 | answered; giữ đúng 2 nguồn, bỏ 1 bản trùng; 2 vòng model |
| CLI 4 | Đề nghị chuẩn bị gửi bản nháp, chưa xác nhận | không gọi tool; hỏi xác nhận bằng lời | transcript CLI v3, turn 4 | Nhắc đúng nội dung và hỏi đồng ý; chưa gửi. Không gọi clarify nên status là answered, không phải waiting_for_user |
| CLI 5 | Từ chối và hủy yêu cầu gửi | không gọi tool | transcript CLI v3, turn 5 | Xác nhận hủy; không có send |

Các phiên UI thật cũng được lưu riêng:

- [Phiên UI 1 — 3 lượt](../../starter_v0/transcripts/v3_openrouter_ui_20261110T200159021454_0e2c65c3.transcript.json): waiting_for_user → answered → answered; có clarify và lookup. Lookup trả RuntimeError, không được coi là lấy dữ liệu thành công.
- [Phiên UI 2 — 2 lượt](../../starter_v0/transcripts/v3_openrouter_ui_20261110T200236467124_7652b70e.transcript.json): waiting_for_user → answered; thể hiện lịch sử được giữ giữa hai lượt. Không gán danh tính cho ID phiên vì UI không có đăng nhập.

CLI được chạy bằng input kiểm thử do Codex vận hành qua API thật; phản hồi dùng thử ngoài nhóm được người dùng xác nhận riêng trong cuộc trò chuyện. Trong tiến trình CLI và UI, thông tin Telegram được bỏ sau khi nạp cấu hình để không gửi thật; không sửa .env. Đây là bằng chứng hỏi trước/hủy gửi, không phải bonus gửi Telegram thành công.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới: `deduplicate` | [tool.py](../../starter_v0/tools/deduplicate/tool.py), [TOOL.md](../../starter_v0/tools/deduplicate/TOOL.md); đăng ký trong tools/__init__.py và artifacts/tools.yaml | Giữ nguồn đầu tiên và thứ tự, loại URL trùng khi chỉ khác host case/fragment; contract test 60 passed | Không gọi mạng/ghi file; không gộp theo nội dung, không bỏ query; lỗi trả error dict |
| Unit test tool mới (≥ 3 test/tool) | [test_tools_todo.py](../../starter_v0/tests/test_tools_todo.py), [output pytest](../../starter_v0/analysis/cp3_pytest.txt) | 5 hàm test với 12 trường hợp cho tool mới, không skip; toàn suite 79 passed, 14 skipped, 0 failed | Happy path, input xấu, lỗi parser; 14 skipped chỉ thuộc stub của tool có sẵn |
| UI và kiểm tra CP5 | [app.py](../../starter_v0/app.py), [test_ui.py](../../starter_v0/tests/test_ui.py), [output pytest](../../starter_v0/analysis/cp5_pytest.txt); lệnh/link ở A1 | UI dùng lại vòng lặp chat.py; 4 test UI offline PASS; toàn suite 83 passed, 14 skipped, 0 failed; link public và WebSocket hoạt động, người ngoài nhóm đã dùng thử theo xác nhận của người dùng | Hiển thị lỗi tool/provider, mỗi phiên có transcript riêng; không gửi Telegram thật; link tunnel tạm thời |

Chi tiết test CP3:

- Happy path: hai URL cùng bài khác hoa/thường ở host hoặc fragment chỉ giữ item đầu tiên; giữ metadata, thứ tự và không sửa input.
- Input xấu từ model: None, chuỗi/dict thay list, item sai kiểu, URL thiếu/sai kiểu/rỗng hoặc đường dẫn tương đối đều trả ValueError dict.
- Nhánh lỗi: URL IPv6 lỗi làm parser phát sinh ValueError; tool trả error dict thay vì raise hoặc trả một phần dữ liệu.
- Biên: list rỗng trả các count bằng 0; URL khác query hoặc hoa/thường ở path phải được giữ riêng.

Ví dụ điều unit test kiểm tra mà eval routing không kiểm tra: nếu code bỏ query khi so trùng, hai URL khác id có thể bị gộp và làm mất nguồn. Test giữ query/path sẽ bắt lỗi đó dù model đã gọi đúng tên tool và arguments. Đây là hành vi được kiểm tra, không phải tuyên bố đã tìm bug trong tool starter.

Lệnh tự kiểm tra từ starter_v0:

```powershell
.\.venv312\Scripts\python.exe -B -m pytest tests/test_tools_todo.py -k deduplicate -v -p no:cacheprovider
.\.venv312\Scripts\python.exe -B -m pytest tests/test_tool_contract.py -q -p no:cacheprovider
.\.venv312\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

Đối chiếu CP3 trong CHECKPOINTS.md: có 1 folder tool mới gồm tool.py + TOOL.md, registry/YAML khớp, 3 stub tool mới đã được thay bằng test thật (thêm 2 test biên), toàn suite 0 failed và B5a có bằng chứng. CP4 sau đó đã đo routing deduplicate ở B3; CP5 đã có UI/transcript ở A1/B4. Thêm tool làm tools_hash hiện tại khác run CP2; không sửa hash/metric lịch sử trong version_log.csv.

Đối chiếu CP5: có UI + dependency + lệnh chạy/link; có ít nhất 3 lượt CLI thật phủ research, thiếu thông tin rồi bổ sung, yêu cầu gửi và hủy; có Phần A/B và bốn báo cáo cá nhân đúng tên. Phân công do người dùng cung cấp; tự đánh giá và commit cá nhân còn cần từng thành viên xác nhận/bổ sung. Test UI dùng kết quả model giả chỉ phục vụ kiểm thử offline, không được tính làm transcript live.

### B5. Bonus Evidence

Chưa làm các bonus trong lần triển khai CP5 này. Tool có sẵn không tự được bonus; không ghi điểm hoặc bằng chứng giả vào các dòng dưới.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chưa tham gia; không có run local để báo cáo. Các dòng bên dưới giữ làm mẫu, không phải kết quả thực nghiệm.

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

- Các run base/group và một phiên UI có tool báo thiếu cấu hình API. UI hiển thị lỗi và giữ tool result trong transcript; demo dùng policy/deduplicate cục bộ để có luồng xử lý dữ liệu thành công. Không che lỗi hoặc coi routing PASS là có dữ liệu thật.
- Kiểm tra trình duyệt tự động bị Computer Use dừng vì không xác định được URL hiện tại đủ chắc chắn để kiểm tra chính sách. Không tiếp tục thao tác trình duyệt; thay vào đó kiểm tra HTTP/health/WebSocket, AppTest và ghi nhận xác nhận dùng thử của người ngoài nhóm từ người dùng.
- Cloudflare Quick Tunnel tạo link tạm theo phiên. Tunnel đầu đã mất kết nối và báo Tunnel not found; đã tạo lại tunnel, cập nhật A1 và kiểm tra HTTP/WebSocket lại. Cần giữ máy, mạng, Streamlit/cloudflared chạy; tạo tunnel mới nếu URL cũ hết hiệu lực.
- Nội dung tự đánh giá/commit của từng người chưa thể suy ra từ log kỹ thuật. Các báo cáo cá nhân ghi rõ phần chờ xác nhận, không bịa đóng góp hay trải nghiệm học tập. Mốc hoàn thành Phần A trước 16:30 chưa có bằng chứng.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

| Thành viên | MSSV | Phần phụ trách theo nhóm | Báo cáo |
|---|---|---|---|
| Đinh Lê Thịnh | 2A202603953 | CP2 | [Cá nhân](2A202603953_DinhLeThinh.md) |
| Trần Thị Hồng Gấm | 2A202603967 | CP5 | [Cá nhân](2A202603967_TranThiHongGam.md) |
| Nguyễn Xuân Dương | 2A202603955 | CP4 | [Cá nhân](2A202603955_NguyenXuanDuong.md) |
| Trần Duy Mạnh | 2A202603998 | CP3 | [Cá nhân](2A202603998_TranDuyManh.md) |

Codex hỗ trợ triển khai, chạy kiểm tra và tổng hợp bằng chứng theo yêu cầu. Các bảng kỹ thuật phản ánh file/run/test thật; không chứng minh từng thành viên đã tự chạy hoặc có commit riêng. Thành viên cần tự xác nhận và bổ sung các mục đó trước khi nộp.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- System prompt quy định hành vi chung: hỏi lại, xác nhận đúng nội dung và dùng lịch sử. Tool declaration quy định khi nào dùng công cụ và convention args; required của schema không bảo đảm model chọn đúng giá trị.
- Cần review thủ công chất lượng câu hỏi xác nhận, tính đúng của câu trả lời no_tool, nguồn trích dẫn và lỗi tool. CLI lượt 4 hỏi xác nhận bằng lời nhưng không gọi clarify; không nên đồng nhất nhãn status của runtime với toàn bộ hành vi hội thoại.
- Group eval chấm lượt cuối với lịch sử đã cho; CLI/UI mới cho thấy việc chờ câu trả lời và tiếp tục qua nhiều lượt. Transcript đầy đủ cần được đọc cùng tool_results để phát hiện lỗi mà accuracy bỏ qua.
- Nếu tiếp tục tối ưu, nên kiểm tra luồng đủ nội dung → xác nhận → gửi, nội dung bị sửa và quyền gửi bị rút lại bằng case mới; cấu hình API tool trước khi đánh giá chất lượng research. Prompt hiện còn quy tắc ép một bước; CP5 giữ nguyên artifact để không trộn thêm vòng CP2 vào công việc UI.
- Demo chưa gửi Telegram thật, chưa chạy local-model bonus và chưa phải hosting cố định. Các báo cáo cá nhân cần tự đánh giá của từng người; không kết luận mọi điều kiện nộp bài đã đủ chỉ từ test xanh.

## 8. Tài liệu tham khảo

- [CHECKPOINTS.md](../../CHECKPOINTS.md), [README.md](../../README.md), [RULES.md](../../RULES.md), [RUBRIC.md](../../RUBRIC.md), [SUBMISSION.md](../../SUBMISSION.md).
- [Streamlit chat elements](https://docs.streamlit.io/develop/api-reference/chat), [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).
- [Cloudflare Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).
