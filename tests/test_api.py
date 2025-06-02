import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'rest_queue', 'src'))

from rest_queue import app, queues


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    # Clear any existing queues before each test
    queues.clear()
    return TestClient(app)


def test_queue_new(subtests, client):
    """Test creating a new queue."""
    # Create a new queue
    with subtests.test(msg='Create a new queue'):
        response = client.post("/queues/test_queue")
        assert response.status_code == 201
        assert response.json() == {"message": "created 'test_queue'"}

    # Try to create the same queue again (should fail)
    with subtests.test(msg='Create a new queue (should fail)'):
        response = client.post("/queues/test_queue")
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]


def test_queue_push(subtests, client):
    """Test pushing items to a queue."""
    # Create a new queue
    client.post("/queues/test_queue")

    # Push an item to the queue
    with subtests.test(msg='Push first item to the queue'):
        response = client.post("/queues/test_queue/push", json="item1")
        assert response.status_code == 200
        assert response.json() == {
            "message": "push to queue 'test_queue'",
            "remaining_queue_size": 1
        }

    # Push another item to the queue
    with subtests.test(msg='Push second item to the queue'):
        response = client.post("/queues/test_queue/push", json="item2")
        assert response.status_code == 200
        assert response.json() == {
            "message": "push to queue 'test_queue'",
            "remaining_queue_size": 2
        }

    # Try to push to a non-existent queue
    with subtests.test(msg='Push to non-existent queue (should fail)'):
        response = client.post("/queues/nonexistent_queue/push", json="item")
        assert response.status_code == 404
        assert "No such queue" in response.json()["detail"]


def test_queue_pop(subtests, client):
    """Test popping items from a queue."""
    # Create a new queue
    client.post("/queues/test_queue")

    # Push some items to the queue
    client.post("/queues/test_queue/push", json="item1")
    client.post("/queues/test_queue/push", json="item2")

    # Pop an item from the queue
    with subtests.test(msg='Pop first item from the queue'):
        response = client.post("/queues/test_queue/pop")
        assert response.status_code == 200
        assert response.json() == {
            "message": "pop from queue 'test_queue'",
            "data": "item1",
            "remaining_queue_size": 1
        }

    # Pop another item from the queue
    with subtests.test(msg='Pop second item from the queue'):
        response = client.post("/queues/test_queue/pop")
        assert response.status_code == 200
        assert response.json() == {
            "message": "pop from queue 'test_queue'",
            "data": "item2",
            "remaining_queue_size": 0
        }

    # Pop from an empty queue
    with subtests.test(msg='Pop from an empty queue'):
        response = client.post("/queues/test_queue/pop")
        assert response.status_code == 200
        assert response.json() == {
            "message": "pop from queue 'test_queue'",
            "data": None,
            "remaining_queue_size": 0
        }

    # Try to pop from a non-existent queue
    with subtests.test(msg='Pop from a non-existent queue (should fail)'):
        response = client.post("/queues/nonexistent_queue/pop")
        assert response.status_code == 404
        assert "No such queue" in response.json()["detail"]


def test_queue_list(subtests, client):
    """Test listing the contents of a queue."""
    # Create a new queue
    client.post("/queues/test_queue")

    # List an empty queue
    with subtests.test(msg='List an empty queue'):
        response = client.get("/queues/test_queue")
        assert response.status_code == 200
        assert response.json() == {
            "message": "items in queue 'test_queue'",
            "items": []
        }

    # Push some items to the queue
    client.post("/queues/test_queue/push", json="item1")
    client.post("/queues/test_queue/push", json="item2")

    # List the queue with items
    with subtests.test(msg='List a queue with items'):
        response = client.get("/queues/test_queue")
        assert response.status_code == 200
        assert response.json() == {
            "message": "items in queue 'test_queue'",
            "items": ["item1", "item2"]
        }

    # Try to list a non-existent queue
    with subtests.test(msg='List a non-existent queue (should fail)'):
        response = client.get("/queues/nonexistent_queue")
        assert response.status_code == 404
        assert "No such queue" in response.json()["detail"]


def test_queue_delete(subtests, client):
    """Test deleting a queue."""
    # Create a new queue
    client.post("/queues/test_queue")

    # Delete the queue
    with subtests.test(msg='Delete an empty queue'):
        response = client.delete("/queues/test_queue")
        assert response.status_code == 200
        assert response.json() == {
            "message": "deleted queue 'test_queue'",
            "remaining_queue_size": 0
        }

    # Verify that the deleted queue is not in the list of queues
    with subtests.test(msg='Verify queue is deleted'):
        response = client.get("/queues")
        assert response.status_code == 200
        assert "test_queue" not in response.json()["items"]

    # Try to delete a non-existent queue
    with subtests.test(msg='Delete a non-existent queue (should fail)'):
        response = client.delete("/queues/nonexistent_queue")
        assert response.status_code == 404
        assert "No such queue" in response.json()["detail"]

    # Create a queue and add items
    client.post("/queues/test_queue")
    client.post("/queues/test_queue/push", json="item1")

    # Try to delete a non-empty queue (should fail with safe_delete=True)
    with subtests.test(msg='Delete a non-empty queue with safe_delete=True (should fail)'):
        response = client.delete("/queues/test_queue")
        assert response.status_code == 409
        assert "not empty" in response.json()["detail"]["message"]

    # Delete a non-empty queue with safe_delete=False
    with subtests.test(msg='Delete a non-empty queue with safe_delete=False'):
        response = client.delete("/queues/test_queue?safe_delete=false")
        assert response.status_code == 200
        assert response.json() == {
            "message": "deleted queue 'test_queue'",
            "remaining_queue_size": 1
        }


def test_queue_list_all(subtests, client):
    """Test listing all queues."""
    # List when no queues exist
    with subtests.test(msg='List when no queues exist'):
        response = client.get("/queues")
        assert response.status_code == 200
        assert response.json() == {
            "message": "list of queue names",
            "items": []
        }

    # Create some queues
    client.post("/queues/queue1")
    client.post("/queues/queue2")
    client.post("/queues/queue3")

    # List all queues
    with subtests.test(msg='List all queues'):
        response = client.get("/queues")
        assert response.status_code == 200
        assert response.json() == {
            "message": "list of queue names",
            "items": ["queue1", "queue2", "queue3"]
        }
