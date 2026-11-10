"""CP5 UI checks with fake model results; never used as live transcript evidence."""
from copy import deepcopy
from pathlib import Path

from streamlit.testing.v1 import AppTest

import chat


APP = Path(__file__).resolve().parents[1] / "app.py"


def app_with_loop(monkeypatch, loop):
    writes = []
    monkeypatch.setattr(chat, "run_model_tool_loop", loop)
    monkeypatch.setattr(chat, "write_transcript", lambda path, payload: writes.append((path, deepcopy(payload))))
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not app.exception
    return app, writes


def test_ui_initial_view_does_not_call_model(monkeypatch):
    def unexpected_call(**kwargs):
        raise AssertionError("Opening the UI must not consume a model request")

    app, writes = app_with_loop(monkeypatch, unexpected_call)

    assert any(title.value == "Trợ lý nghiên cứu" for title in app.title)
    assert len(app.chat_input) == 1
    assert app.session_state["transcript"]["telegram_mode"] == "disabled_for_demo"
    assert app.session_state["transcript"]["turns"] == []
    assert writes == []


def test_ui_clarification_carries_history_and_saves_each_turn(monkeypatch):
    received = []

    def loop(**kwargs):
        received.append(deepcopy(kwargs["messages"]))
        if len(received) == 1:
            return {
                "status": "waiting_for_user", "assistant_text": "Bạn gửi danh sách cần lọc nhé.",
                "rounds": [], "tool_events": [],
            }
        return {"status": "answered", "assistant_text": "Đã nhận danh sách.", "rounds": [], "tool_events": []}

    app, writes = app_with_loop(monkeypatch, loop)
    app.chat_input[0].set_value("Lọc nguồn trùng giúp tôi.").run()
    assert not app.exception
    assert any("Đang chờ" in info.value for info in app.info)
    app.chat_input[0].set_value("Danh sách của tôi có hai nguồn.").run()

    assert not app.exception
    assert received[1][-3:] == [
        {"role": "user", "content": "Lọc nguồn trùng giúp tôi."},
        {"role": "assistant", "content": "Bạn gửi danh sách cần lọc nhé."},
        {"role": "user", "content": "Danh sách của tôi có hai nguồn."},
    ]
    assert len(writes) == 2
    assert [turn["status"] for turn in writes[-1][1]["turns"]] == ["waiting_for_user", "answered"]


def test_ui_displays_tool_errors_and_keeps_evidence(monkeypatch):
    event = {
        "tool": "lookup", "args": {"query": "AI"},
        "result": {"error": "RuntimeError", "message": "Missing TAVILY_API_KEY env var"},
    }

    def loop(**kwargs):
        return {
            "status": "answered", "assistant_text": "Chưa lấy được dữ liệu.",
            "rounds": [], "tool_events": [event],
        }

    app, writes = app_with_loop(monkeypatch, loop)
    app.chat_input[0].set_value("Tìm tin AI.").run()

    assert not app.exception
    assert any("Missing TAVILY_API_KEY" in error.value for error in app.error)
    assert any("Công cụ đã gọi" in expander.label for expander in app.expander)
    assert writes[-1][1]["turns"][0]["tool_events"] == [event]


def test_ui_new_conversation_resets_context_without_replacing_old_transcript(monkeypatch):
    def loop(**kwargs):
        return {"status": "answered", "assistant_text": "Xin chào.", "rounds": [], "tool_events": []}

    app, writes = app_with_loop(monkeypatch, loop)
    app.chat_input[0].set_value("Bạn làm được gì?").run()
    old_id = app.session_state["transcript"]["transcript_id"]
    old_saved = deepcopy(writes[0])
    next(button for button in app.button if button.label == "Cuộc trò chuyện mới").click().run()

    assert not app.exception
    assert app.session_state["transcript"]["transcript_id"] != old_id
    assert app.session_state["transcript"]["turns"] == []
    assert app.session_state["history"] == []
    assert writes == [old_saved]
