from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import pytest


# Patch redis.Redis before importing the app so the module-level
# `r = redis.Redis(...)` call never touches a real Redis instance
@pytest.fixture(autouse=True)
def mock_redis():
    with patch("main.r") as mock_r:
        yield mock_r


@pytest.fixture()
def client():
    from main import app
    return TestClient(app)


# --- POST /jobs ---

def test_create_job_returns_job_id(client, mock_redis):
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1

    response = client.post("/jobs")

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # valid UUID length


def test_create_job_pushes_to_redis_queue(client, mock_redis):
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1

    response = client.post("/jobs")
    job_id = response.json()["job_id"]

    mock_redis.lpush.assert_called_once_with("job", job_id)
    mock_redis.hset.assert_called_once_with(f"job:{job_id}", "status", "queued")


def test_create_job_sets_status_to_queued(client, mock_redis):
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1

    # immediately mock the status read back as "queued"
    mock_redis.hget.return_value = b"queued"

    post_response = client.post("/jobs")
    job_id = post_response.json()["job_id"]

    get_response = client.get(f"/jobs/{job_id}")
    assert get_response.status_code == 200
    assert get_response.json()["status"] == "queued"


# --- GET /jobs/{job_id} ---

def test_get_job_returns_status(client, mock_redis):
    mock_redis.hget.return_value = b"completed"

    response = client.get("/jobs/some-job-id")

    assert response.status_code == 200
    assert response.json() == {"job_id": "some-job-id", "status": "completed"}


def test_get_job_returns_404_when_not_found(client, mock_redis):
    mock_redis.hget.return_value = None

    response = client.get("/jobs/nonexistent-id")

    assert response.status_code == 404
    assert response.json() == {"error": "not found"}


def test_get_job_returns_queued_status(client, mock_redis):
    mock_redis.hget.return_value = b"queued"

    response = client.get("/jobs/some-job-id")

    assert response.status_code == 200
    assert response.json()["status"] == "queued"
