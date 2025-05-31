import pytest
from collections import deque
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'rest_queue', 'src'))

from rest_queue import Queue


@pytest.fixture
def queue():
    """Create a new Queue instance for each test."""
    queue_name = "test_queue"
    return Queue(queue_name)


def test_init(queue):
    """Test that a Queue is initialized correctly."""
    assert queue._name == "test_queue"
    assert isinstance(queue._contents, deque)
    assert len(queue._contents) == 0


def test_iter(queue):
    """Test that __iter__ returns an iterator of the queue contents."""
    # Add some items to the queue
    items = ["item1", "item2", "item3"]
    for item in items:
        queue.push(item)

    # Check that iterating over the queue gives the expected items
    assert list(queue) == items


def test_len(queue):
    """Test that __len__ returns the correct queue size."""
    # Queue should be empty initially
    assert len(queue) == 0

    # Add some items and check the length
    queue.push("item1")
    assert len(queue) == 1

    queue.push("item2")
    assert len(queue) == 2

    # Remove an item and check the length
    queue.pop()
    assert len(queue) == 1


def test_push(queue):
    """Test that push adds items to the queue correctly."""
    # Queue should be empty initially
    assert len(queue) == 0

    # Push an item and check it was added
    queue.push("item1")
    assert len(queue) == 1
    assert list(queue) == ["item1"]

    # Push another item and check both items are in the queue
    queue.push("item2")
    assert len(queue) == 2
    assert list(queue) == ["item1", "item2"]


def test_pop(queue):
    """Test that pop removes and returns items from the queue in FIFO order."""
    # Add some items to the queue
    items = ["item1", "item2", "item3"]
    for item in items:
        queue.push(item)

    # Pop items and check they come out in the right order
    assert queue.pop() == "item1"
    assert queue.pop() == "item2"
    assert queue.pop() == "item3"

    # Queue should be empty now
    assert len(queue) == 0


def test_pop_empty(queue):
    """Test that pop raises an IndexError when the queue is empty."""
    # Queue should be empty initially
    assert len(queue) == 0

    # Popping from an empty queue should raise IndexError
    with pytest.raises(IndexError):
        queue.pop()
