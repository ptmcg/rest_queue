#
# simple_rest_queue.py
#
# A simple FastAPI web service that maintains multiple named FIFO queues
# that can be created, pushed, and popped using REST calls
#
from collections import deque
from typing import Dict

import fastapi

# registry for REST-accessible queues
queues: Dict[str, deque] = {}


app = fastapi.FastAPI()


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
    queues[queue_name] = deque()

    return {"message": f"created {queue_name!r}"}


@app.get("/queues/{queue_name}", status_code=fastapi.status.HTTP_200_OK)
async def queue_pop(queue_name: str):
    """
    Pop oldest value from queue, or None if queue is empty.
    """
    if queue_name not in queues:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND,
                                    detail=f"No such queue {queue_name!r}")

    q = queues[queue_name]
    if q:
        value = q.popleft()
    else:
        value = None

    return {"message": f"get from queue {queue_name!r}",
            "data": value,
            "remaining_queue_size": len(q),
            }


@app.put("/queues/{queue_name}", status_code=fastapi.status.HTTP_200_OK)
async def queue_push(queue_name: str, value: str):
    """
    Push new value onto queue.
    """
    if queue_name not in queues:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND,
                                    detail=f"No such queue {queue_name!r}")

    q = queues[queue_name]
    q.append(value)

    return {
        "message": f"put to queue {queue_name!r}",
        "remaining_queue_size": len(q),
    }


@app.delete("/queues/{queue_name}", status_code=fastapi.status.HTTP_200_OK)
async def queue_delete(queue_name: str,
                       safe_delete: bool = True):
    """
    Delete queue.
    """
    if queue_name not in queues:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND,
                                    detail=f"No such queue {queue_name!r}")

    q = queues[queue_name]

    if safe_delete and q:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_409_CONFLICT,
                                    detail=f"Queue {queue_name!r} not empty (contains {len(q)} items)")

    # remove queue from registry
    del queues[queue_name]

    return {
        "message": f"deleted queue {queue_name!r}",
        "remaining_queue_size": len(q),
    }


@app.get("/queues/{queue_name}/list", status_code=fastapi.status.HTTP_200_OK)
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


@app.get("/queues", status_code=fastapi.status.HTTP_200_OK)
async def queue_list_all():
    """
    List out all queue names.
    """
    return {
        "message": f"list of queue names",
        "items": list(queues),
    }
