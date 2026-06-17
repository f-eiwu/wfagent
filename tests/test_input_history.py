from coding_agent.input_history import InputHistory, InputHistoryNavigator


class TestInputHistory:
    def test_push_skips_empty_and_exit(self):
        history = InputHistory()
        history.push("")
        history.push("exit")
        assert history.entries() == []

    def test_push_dedupes_consecutive(self):
        history = InputHistory()
        history.push("hello")
        history.push("hello")
        assert history.entries() == ["hello"]

    def test_navigator_up_down(self):
        history = InputHistory()
        history.push("first")
        history.push("second")
        nav = InputHistoryNavigator(history)

        assert nav.previous("") == "second"
        assert nav.previous("second") == "first"
        assert nav.next() == "second"
        assert nav.next() == ""

    def test_navigator_preserves_draft(self):
        history = InputHistory()
        history.push("done")
        nav = InputHistoryNavigator(history)

        assert nav.previous("draft text") == "done"
        assert nav.next() == "draft text"
