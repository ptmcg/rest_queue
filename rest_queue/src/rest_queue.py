#
# rest_queue.py
#
# A lightweight FastAPI web service that maintains multiple named FIFO queues
# that can be created, pushed, and popped using REST calls
#
# NOTE: this service does NO persistence, so restarting the server will lose all
# items that are still in the queues.
#
from collections import deque

import fastapi


class Queue:
    """
    A small container class to wrap a deque with push and pop methods,
    and __iter__ and __len__ dunder methods.
    """
    def __init__(self, name):
        self._name = name
        self._contents = deque()

    def __iter__(self):
        return iter(self._contents)

    def __len__(self):
        return len(self._contents)

    def push(self, value):
        self._contents.append(value)

    def pop(self):
        return self._contents.popleft()


# registry for REST-accessible queues
queues: dict[str, Queue] = {}


app = fastapi.FastAPI()

"""
Implement these endpoints:

Create  - POST    http://host:port/queues/<queue_name>
Push    - POST    http://host:port/queues/<queue_name>/push
Pop     - POST    http://host:port/queues/<queue_name>/pop
List    - GET     http://host:port/queues/<queue_name>
Delete  - DELETE  http://host:port/queues/<queue_name>
List    - GET     http://host:port/queues
"""


# find HTTP statuses at http://httpstatuses.com
@app.post("/queues/{queue_name}", status_code=fastapi.status.HTTP_201_CREATED)
async def queue_new(queue_name: str):
    """
    Create new queue with given queue name.

    Raises an exception if the queue already exists.
    """
    if queue_name in queues:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_409_CONFLICT,
                                    detail=f"Queue {queue_name!r} already exists")

    # create new deque and add to registry under the given name
    queues[queue_name] = Queue(queue_name)

    return {"message": f"created {queue_name!r}"}


@app.post("/queues/{queue_name}/push")
async def queue_push(queue_name: str, value: str):
    """
    Push new value onto queue.
    """
    if queue_name not in queues:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND,
                                    detail=f"No such queue {queue_name!r}")

    q = queues[queue_name]
    q.push(value)

    return {
        "message": f"push to queue {queue_name!r}",
        "remaining_queue_size": len(q),
    }


@app.post("/queues/{queue_name}/pop")
async def queue_pop(queue_name: str):
    """
    Pop oldest value from queue, or None if queue is empty.
    """
    if queue_name not in queues:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND,
                                    detail=f"No such queue {queue_name!r}")

    q = queues[queue_name]
    if q:
        value = q.pop()
    else:
        value = None

    return {"message": f"pop from queue {queue_name!r}",
            "data": value,
            "remaining_queue_size": len(q),
            }


@app.get("/queues/{queue_name}")
async def queue_list(queue_name: str):
    """
    List out contents of queue.
    """
    if queue_name not in queues:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND,
                                    detail=f"No such queue {queue_name!r}")

    q = queues[queue_name]

    return {
        "message": f"items in queue {queue_name!r}",
        "items": list(q),
    }


@app.delete("/queues/{queue_name}")
async def queue_delete(queue_name: str,
                       safe_delete: bool = True):
    """
    Delete queue.
    """
    if queue_name not in queues:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND,
                                    detail=f"No such queue {queue_name!r}")

    q = queues[queue_name]
    remaining_size = len(q)

    if safe_delete and remaining_size > 0:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_409_CONFLICT,
                                    detail={"message": f"Queue {queue_name!r} not empty",
                                            "count": remaining_size,
                                            }
                                    )

    # remove queue from registry
    del queues[queue_name]

    return {
        "message": f"deleted queue {queue_name!r}",
        "remaining_queue_size": remaining_size,
    }


@app.get("/queues")
async def queue_list_all():
    """
    List out all queue names.
    """
    return {
        "message": f"list of queue names",
        "items": list(queues),
    }
