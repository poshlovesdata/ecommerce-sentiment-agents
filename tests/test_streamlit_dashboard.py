"""Smoke test for the Streamlit dashboard."""

from streamlit.testing.v1 import AppTest


def test_dashboard_renders_without_exceptions() -> None:
    app = AppTest.from_file("app/streamlit_app.py")

    app.run(timeout=30)

    assert not app.exception
    assert len(app.title) == 1
    assert len(app.metric) == 5
    assert len(app.dataframe) == 1
