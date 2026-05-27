import pytest
from app.storage import storage

@pytest.fixture(autouse=True)
def clear_storage():
    storage.clear()
    yield