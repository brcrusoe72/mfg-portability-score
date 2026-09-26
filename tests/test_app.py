"""Regression tests for public routes and report data integrity."""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app as app_module
from portability_score.models import Base, Platform, UserReport


@pytest.fixture
def session_factory(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as session:
        session.add(
            Platform(
                id=1,
                name="Test MES",
                slug="test-mes",
                vendor="Example",
            )
        )
        session.commit()
    monkeypatch.setattr(app_module, "Session", factory)
    return factory


@pytest.fixture
def client(session_factory):
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_missing_platform_page_returns_404(client):
    response = client.get("/platform/does-not-exist")
    assert response.status_code == 404


def test_api_platform_lookup_returns_404(client):
    response = client.get("/api/platforms/999")
    assert response.status_code == 404


def test_valid_report_is_persisted(client, session_factory):
    response = client.post(
        "/api/reports",
        json={
            "platform_id": 1,
            "experience": "Portable export worked.",
            "rating": 4,
        },
    )
    assert response.status_code == 201

    with session_factory() as session:
        report = session.scalar(select(UserReport))
        assert report.platform_id == 1
        assert report.author_name == "Anonymous"
        assert report.rating == 4


@pytest.mark.parametrize("rating", [0, 6, True, "bad"])
def test_invalid_rating_is_rejected(client, rating):
    response = client.post(
        "/api/reports",
        json={
            "platform_id": 1,
            "experience": "Invalid rating.",
            "rating": rating,
        },
    )
    assert response.status_code == 400


def test_unknown_platform_cannot_create_orphan_report(client, session_factory):
    response = client.post(
        "/api/reports",
        json={
            "platform_id": 999,
            "experience": "Orphan attempt.",
            "rating": 3,
        },
    )
    assert response.status_code == 404
    with session_factory() as session:
        assert session.scalar(select(UserReport)) is None


@pytest.mark.parametrize("experience", ["", " ", None, 123])
def test_invalid_experience_is_rejected(client, experience):
    response = client.post(
        "/api/reports",
        json={
            "platform_id": 1,
            "experience": experience,
            "rating": 3,
        },
    )
    assert response.status_code == 400
