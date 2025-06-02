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


def test_init(subtests, queue):
    """Test that a Queue is initialized correctly."""
    with subtests.test(msg='Queue name is set correctly'):
        assert queue._name == "test_queue"

    with subtests.test(msg='Queue contents is a deque'):
        assert isinstance(queue._contents, deque)

    with subtests.test(msg='Queue is initially empty'):
        assert len(queue._contents) == 0


def test_iter(subtests, queue):
    """Test that __iter__ returns an iterator of the queue contents."""
    # Add some items to the queue
    items = ["item1", "item2", "item3"]
    for item in items:
        queue.push(item)

    # Check that iterating over the queue gives the expected items
    with subtests.test(msg='Queue iteration returns correct items'):
        assert list(queue) == items


def test_len(subtests, queue):
    """Test that __len__ returns the correct queue size."""
    # Queue should be empty initially
    with subtests.test(msg='Empty queue has length 0'):
        assert len(queue) == 0

    # Add some items and check the length
    queue.push("item1")
    with subtests.test(msg='Queue with one item has length 1'):
        assert len(queue) == 1

    queue.push("item2")
    with subtests.test(msg='Queue with two items has length 2'):
        assert len(queue) == 2

    # Remove an item and check the length
    queue.pop()
    with subtests.test(msg='Queue after popping has correct length'):
        assert len(queue) == 1


def test_push(subtests, queue):
    """Test that push adds items to the queue correctly."""
    # Queue should be empty initially
    with subtests.test(msg='Queue is initially empty'):
        assert len(queue) == 0

    # Push an item and check it was added
    queue.push("item1")
    with subtests.test(msg='Queue has correct length after first push'):
        assert len(queue) == 1
    with subtests.test(msg='Queue has correct contents after first push'):
        assert list(queue) == ["item1"]

    # Push another item and check both items are in the queue
    queue.push("item2")
    with subtests.test(msg='Queue has correct length after second push'):
        assert len(queue) == 2
    with subtests.test(msg='Queue has correct contents after second push'):
        assert list(queue) == ["item1", "item2"]


def test_pop(subtests, queue):
    """Test that pop removes and returns items from the queue in FIFO order."""
    # Add some items to the queue
    items = ["item1", "item2", "item3"]
    for item in items:
        queue.push(item)

    # Pop items and check they come out in the right order
    with subtests.test(msg='First pop returns first item'):
        assert queue.pop() == "item1"

    with subtests.test(msg='Second pop returns second item'):
        assert queue.pop() == "item2"

    with subtests.test(msg='Third pop returns third item'):
        assert queue.pop() == "item3"

    # Queue should be empty now
    with subtests.test(msg='Queue is empty after popping all items'):
        assert len(queue) == 0


def test_pop_empty(subtests, queue):
    """Test that pop raises an IndexError when the queue is empty."""
    # Queue should be empty initially
    with subtests.test(msg='Queue is initially empty'):
        assert len(queue) == 0

    # Popping from an empty queue should raise IndexError
    with subtests.test(msg='Popping from empty queue raises IndexError'):
        with pytest.raises(IndexError):
            queue.pop()
