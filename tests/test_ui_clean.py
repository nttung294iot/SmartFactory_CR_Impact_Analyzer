from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_VISIBLE_LABELS = (
    "100% Offline",
    "BM25 Retrieval",
    "Rule-based Analysis",
    "Local only",
    "External API",
    "System status",
)


def test_removed_technical_badges_are_not_in_runtime_ui() -> None:
    files = [ROOT / "app.py", *sorted((ROOT / "views").glob("*.py")), *sorted((ROOT / "ui").glob("*.py"))]
    visible_source = "\n".join(path.read_text(encoding="utf-8") for path in files if path.exists())
    for label in FORBIDDEN_VISIBLE_LABELS:
        assert label not in visible_source


def test_removed_technical_badges_are_not_in_preview() -> None:
    preview = (ROOT / "docs" / "UI_PREVIEW.html").read_text(encoding="utf-8")
    for label in FORBIDDEN_VISIBLE_LABELS:
        assert label not in preview


def test_streamlit_native_page_navigation_is_disabled() -> None:
    assert not (ROOT / "pages").exists(), "The pages/ directory enables Streamlit native navigation."
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert "showSidebarNavigation = false" in config
