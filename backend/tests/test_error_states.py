from types import SimpleNamespace

from swarmguard.dashboard.error_states import (
    classify_error,
    render_empty_state,
    render_page_safely,
)


class FakeStreamlit:
    def __init__(self) -> None:
        self.markdowns: list[str] = []
        self.buttons: list[str] = []
        self.rerun_called = False

    def markdown(self, value, **_kwargs) -> None:
        self.markdowns.append(value)

    def button(self, label, **_kwargs) -> bool:
        self.buttons.append(label)
        return False

    def rerun(self) -> None:
        self.rerun_called = True


def test_error_classification_provides_safe_actionable_messages() -> None:
    assert classify_error(ValueError("secret input")).code == "SG-INPUT"
    assert classify_error(MemoryError()).code == "SG-CAPACITY"
    assert classify_error(TimeoutError()).code == "SG-CONNECTION"
    unexpected = classify_error(RuntimeError("database password"))

    assert unexpected.code == "SG-UNEXPECTED"
    assert "database password" not in unexpected.message
    assert unexpected.recovery


def test_safe_page_boundary_catches_error_without_leaking_details() -> None:
    st = FakeStreamlit()

    def broken_page() -> None:
        raise RuntimeError("private implementation detail")

    render_page_safely(st, broken_page, page_title="Test")

    rendered = " ".join(st.markdowns)
    assert "SG-UNEXPECTED" in rendered
    assert "private implementation detail" not in rendered
    assert st.buttons == ["Yeniden dene"]


def test_safe_page_boundary_preserves_successful_renderer() -> None:
    st = FakeStreamlit()
    called = SimpleNamespace(value=False)

    def healthy_page() -> None:
        called.value = True

    render_page_safely(st, healthy_page, page_title="Test")

    assert called.value is True
    assert not st.markdowns
    assert not st.buttons


def test_empty_state_escapes_content_and_renders_optional_action() -> None:
    st = FakeStreamlit()
    render_empty_state(
        st,
        icon="<>",
        title="<script>unsafe</script>",
        message="Henüz veri yok",
        action_label="Başla",
        action_href="simulation",
    )

    rendered = st.markdowns[0]
    assert "<script>unsafe</script>" not in rendered
    assert "&lt;script&gt;unsafe&lt;/script&gt;" in rendered
    assert 'href="simulation"' in rendered
