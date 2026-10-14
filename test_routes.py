import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app as site
from portability_score.models import Base, Platform


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as session:
        session.add(Platform(name='Example', slug='example'))
        session.commit()
    monkeypatch.setattr(site, 'Session', factory)
    site.app.config['TESTING'] = True
    with site.app.test_client() as client:
        yield client
    engine.dispose()


def test_platform_detail_renders(client):
    response = client.get('/platform/example')
    assert response.status_code == 200
    assert b'Example' in response.data


def test_unknown_platform_is_404(client):
    assert client.get('/platform/missing').status_code == 404
