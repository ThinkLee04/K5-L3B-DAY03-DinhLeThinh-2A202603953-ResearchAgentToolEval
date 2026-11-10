"""CP5 Streamlit UI sharing the model/tool loop with chat.py."""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import streamlit as st

from chat import now_iso, run_model_tool_loop, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).resolve().parent
VERSION = "v3"
PROVIDER = "openrouter"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4

# chat.py has already loaded the environment. This public lab demo never sends
# real Telegram messages, even if the model incorrectly sets confirmed=true.
os.environ.pop("TELEGRAM_BOT_TOKEN", None)
os.environ.pop("TELEGRAM_CHAT_ID", None)

EXAMPLES = {
    "Tra policy": "Theo policy nội bộ, tweet viral có đủ để xem một thông tin là đã được xác minh không? Hãy tra policy và giải thích ngắn gọn.",
    "Lọc nguồn trùng": 'Chỉ lọc nguồn trùng URL, giữ bản đầu: [{"title":"Nguồn A","url":"https://example.com/a#intro"},{"title":"Bản trùng A","url":"https://example.com/a#end"},{"title":"Nguồn B","url":"https://example.org/b"}]. Không đọc web.',
    "Hỏi lại khi thiếu": "Tôi muốn lọc nguồn trùng nhưng chưa gửi danh sách. Hãy hỏi tôi danh sách cần lọc, không tự tạo nguồn.",
    "Xin xác nhận gửi": "Bản nháp nguyên văn: 'Nhóm đọc paper lúc 19:00 thứ Sáu.' Cho tôi xem lại và hỏi có đồng ý gửi Telegram không. Chưa gửi ở lượt này.",
}


def new_session() -> None:
    prompt_path = ROOT / "artifacts/system_prompt.md"
    tools_path = ROOT / "artifacts/tools.yaml"
    declarations = load_tool_declarations(tools_path)
    provider = make_provider(PROVIDER)
    stamp = datetime.now(timezone(timedelta(hours=7))).strftime("%Y%m%dT%H%M%S%f")
    session_id = f"{VERSION}_{PROVIDER}_ui_{stamp}_{uuid4().hex[:8]}"
    st.session_state.context = {
        "system_prompt": prompt_path.read_text(encoding="utf-8"),
        "tools": to_openai_tools(declarations),
        "provider": provider,
        "model": provider.default_model,
        "tool_names": [tool["name"] for tool in declarations],
    }
    st.session_state.history = []
    st.session_state.transcript_path = ROOT / "transcripts" / f"{session_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": session_id,
        **artifact_version_dict(build_artifact_version(VERSION, prompt_path, tools_path)),
        "provider": PROVIDER,
        "model": provider.default_model,
        "channel": "streamlit",
        "telegram_mode": "disabled_for_demo",
        "system_prompt": "artifacts/system_prompt.md",
        "tools": "artifacts/tools.yaml",
        "history_window": HISTORY_WINDOW,
        "max_tool_rounds": MAX_TOOL_ROUNDS,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def render_turn(turn: dict) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        if turn["status"] == "provider_error":
            st.error(turn["error"])
        elif turn.get("assistant_text"):
            st.markdown(turn["assistant_text"])
        if turn["status"] == "waiting_for_user":
            st.info("Đang chờ bạn bổ sung thông tin hoặc xác nhận.")
        elif turn["status"] == "max_tool_rounds":
            st.warning("Đã chạm giới hạn vòng gọi tool. Xem kết quả bên dưới trước khi tiếp tục.")
        if turn.get("transcript_save_error"):
            st.error("Chưa lưu được transcript trên máy chủ. Hãy tải phiên này ở thanh bên.")

        events = turn.get("tool_events", [])
        errors = [event for event in events if isinstance(event.get("result"), dict) and event["result"].get("error")]
        for event in errors:
            result = event["result"]
            st.error(f"{event['tool']}: {result['error']} — {result.get('message', '')}")
        if events:
            with st.expander(f"Công cụ đã gọi ({len(events)})", expanded=bool(errors)):
                for event in events:
                    st.caption(event["tool"])
                    st.json(event)


def submit(user_text: str) -> None:
    context = st.session_state.context
    transcript = st.session_state.transcript
    turn = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    messages = [
        {"role": "system", "content": context["system_prompt"]},
        *trim_history(st.session_state.history, HISTORY_WINDOW),
        {"role": "user", "content": user_text},
    ]
    try:
        turn.update(run_model_tool_loop(
            provider=context["provider"],
            messages=messages,
            tools=context["tools"],
            model=context["model"],
            max_tool_rounds=MAX_TOOL_ROUNDS,
        ))
        st.session_state.history.extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": turn["assistant_text"]},
        ])
    except Exception as exc:
        # Keep provider errors visible without displaying credentials or raw
        # request headers. Tool error dictionaries are shown separately above.
        code = getattr(exc, "status_code", None)
        suffix = f" (HTTP {code})" if code is not None else ""
        turn.update(status="provider_error", error=f"Model chưa trả lời được: {type(exc).__name__}{suffix}. Kiểm tra provider, quota hoặc kết nối rồi thử lại.")
    turn["ended_at"] = now_iso()
    transcript["turns"].append(turn)
    try:
        write_transcript(st.session_state.transcript_path, transcript)
    except OSError:
        turn["transcript_save_error"] = True


def main() -> None:
    st.set_page_config(page_title="Research Lab · Day 03", page_icon="🔎", layout="centered")
    if "transcript" not in st.session_state:
        new_session()

    with st.sidebar:
        st.title("Research Lab")
        st.caption("MTGD · L3B · AI Thực Chiến Day 03")
        if st.button("Cuộc trò chuyện mới", use_container_width=True):
            new_session()
            st.rerun()
        st.divider()
        st.write("**Chế độ dùng thử**")
        st.caption("Telegram được tắt trong bản demo. Không nhập API key hoặc dữ liệu nhạy cảm vào chat.")
        with st.expander("Công cụ của agent"):
            st.write(", ".join(st.session_state.context["tool_names"]))
        st.caption(f"{PROVIDER} · {st.session_state.context['model']} · {VERSION}")
        st.download_button(
            "Tải transcript JSON",
            data=json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str),
            file_name=st.session_state.transcript_path.name,
            mime="application/json",
            use_container_width=True,
        )

    st.title("Trợ lý nghiên cứu")
    st.caption("Tra cứu, làm sạch nguồn và tổng hợp. Bạn có thể xem agent đã gọi công cụ nào ở từng lượt.")
    if not st.session_state.transcript["turns"]:
        st.info("Bắt đầu bằng câu hỏi của bạn hoặc chọn một yêu cầu mẫu bên dưới.")
    with st.expander("Câu hỏi mẫu", expanded=not bool(st.session_state.transcript["turns"])):
        selected = None
        columns = st.columns(2)
        for index, (label, value) in enumerate(EXAMPLES.items()):
            if columns[index % 2].button(label, key=f"example_{index}", use_container_width=True):
                selected = value

    for turn in st.session_state.transcript["turns"]:
        render_turn(turn)
    user_text = st.chat_input("Nhập yêu cầu nghiên cứu hoặc trả lời câu hỏi của agent…", max_chars=12000)
    request = user_text or selected
    if request and request.strip():
        with st.spinner("Agent đang xử lý…"):
            submit(request.strip())
        st.rerun()


if __name__ == "__main__":
    main()
