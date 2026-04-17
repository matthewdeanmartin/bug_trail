"""Smoke tests for the FastAPI server."""

from __future__ import annotations

import logging

import pytest
from fastapi.testclient import TestClient

from bug_trail import app as app_module
from bug_trail.app import app


@pytest.fixture()
def configured_db(tmp_path, monkeypatch):
    """Point the app at a fresh SQLite file with a single ERROR record."""
    from bug_trail_core.handlers import BugTrailHandler

    db_path = tmp_path / "errors.db"
    monkeypatch.setattr(app_module.STATE, "db_path", str(db_path))
    monkeypatch.setattr(app_module.STATE, "source_folder", "")

    handler = BugTrailHandler(str(db_path))
    logger = logging.getLogger("bt-test")
    logger.handlers.clear()
    logger.setLevel(logging.ERROR)
    logger.propagate = False
    logger.addHandler(handler)
    logger.error("something broke: %s", "boom")
    handler.close()
    logger.handlers.clear()

    yield str(db_path)


def test_help_page_ok():
    client = TestClient(app)
    r = client.get("/help")
    assert r.status_code == 200
    assert "Getting started" in r.text


def test_empty_state_when_no_db(monkeypatch, tmp_path):
    monkeypatch.setattr(app_module.STATE, "db_path", str(tmp_path / "missing.db"))
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert "No log data yet" in r.text


def test_index_lists_logs(configured_db):
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert "Error Logs" in r.text
    assert "something broke" in r.text


def test_detail_page(configured_db):
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    # Grab a detail URL from the rendered page.
    import re

    match = re.search(r'href="(/log/[^"]+)"', r.text)
    assert match, "expected a detail link in the index page"
    detail = client.get(match.group(1))
    assert detail.status_code == 200
    assert "Basic Data" in detail.text


def test_admin_page_lists_counts(configured_db):
    client = TestClient(app)
    r = client.get("/admin")
    assert r.status_code == 200
    assert "Row counts" in r.text


def test_admin_clear_requires_confirm(configured_db):
    client = TestClient(app)
    # Missing confirm returns a redirect without clearing.
    r = client.post("/admin/clear", data={}, follow_redirects=False)
    assert r.status_code == 303
    # Index should still show the records.
    r2 = client.get("/")
    assert "something broke" in r2.text


def test_admin_clear_then_empty(configured_db):
    client = TestClient(app)
    r = client.post(
        "/admin/clear", data={"confirm": "yes"}, follow_redirects=False
    )
    assert r.status_code == 303
    r2 = client.get("/")
    assert "No log data yet" in r2.text


def test_environment_and_system_render(configured_db):
    client = TestClient(app)
    assert client.get("/environment").status_code == 200
    assert client.get("/system").status_code == 200


def test_health_endpoint():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.text == "ok"
