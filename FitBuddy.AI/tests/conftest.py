import os


os.environ["DATABASE_URL"] = (
    "sqlite:///./test_fitbuddy.db"
)

os.environ["GEMINI_API_KEY"] = "test-key"


from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


def pytest_sessionstart(session):

    Base.metadata.drop_all(
        bind=engine
    )

    Base.metadata.create_all(
        bind=engine
    )


def pytest_sessionfinish(
    session,
    exitstatus,
):

    Base.metadata.drop_all(
        bind=engine
    )

    try:
        os.remove(
            "test_fitbuddy.db"
        )
    except FileNotFoundError:
        pass


client = TestClient(app)