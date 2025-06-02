## rest_queue

`rest_queue` is a simple demonstration of creating a REST service to host one or more
FIFO queues, shareable across multiple producers and consumers.

### Background

`rest_queue` originated out of some discussion on the StackOverflow Python chat, regarding
sharing of a queue across multiple Python processes. The initial question was how to connect 
to a queue that had already been created in a running Python program. Several alternatives were
posed, but most were very low-level, or did not support access by new external Python processes.

My suggestion was to create a small REST service that would manage a single queue, which any
Python script could then connect to and push or pop items from the queue. All that would be 
needed would be the base URL of the REST service. So after the discussion died down, I made an
attempt at creating my own such REST service.

I chose FastAPI as the framework with which to create the REST service, as I wanted to make a 
small project with it to learn more about it. The actual implementation was very straightforward,
once I settled on the API endpoints.

I also extended the original concept, where the server managed just a single queue, to support multiple
queues, to be a better illustration of REST interactions with a server managing multiple
resources.


### REST API

| Function | REST method | URL | Return status |
|---|---|---|---|
| Create Queue |   POST | `/queues/{queue_name}`  | 201 - Queue created<br>409 - Queue exists |
| Queue Push |   POST | `/queues/{queue_name}/push` | 200 - Operation successful<br>404 - No such queue |
| Queue Pop |   POST |   `/queues/{queue_name}/pop` | 200 - Operation successful<br>404 - No such queue |
| List Queue Items | GET |  `/queues/{queue_name}` | 200 - Operation successful<br>404 - No such queue |
| Delete Queue |   DELETE | `/queues/{queue_name}[?safe_delete=true]` | 200 - Operation successful<br>404 - No such queue<br>409 - Queue is not empty `(safe_mode=True)` |
| List All Queues |   GET |   `/queues` | 200 - Operation successful |


### Deploying

#### Manual

The `rest_queue` server can be run locally by entering commands at the terminal console.
Install Python 3.6 or later, and after `cd` to the project's `rest_queue/src` directory, install
the required Python add-on modules using:

    pip install -r requirements.txt

Then run the server using `uvicorn`:

    uvicorn rest_queue:app --port 8001

You can open a browser to `http://localhost:8001/docs#/` to interact with the new queue.


#### Docker

The docker directory includes a `Dockerfile` to simplify creating a `rest_queue` running in a 
Docker container. `cd` to this project's main directory, and run the following commands
to build, run, stop, start, and delete the `rest_queue` docker image and container.

    # build image
    docker build -f docker/Dockerfile -t rest_queue:latest .

    # start container mapping port 18000 to container port 8000
    docker run -d -p 18000:8000 --name rest_queue rest_queue

    # stop running container
    docker stop rest_queue

    # start stopped container
    docker start rest_queue

    # view running containers
    docker ps

    # delete container
    docker rm rest_queue

    # view docker images
    docker images

    # delete image
    docker rmi rest_queue

Open a browser to `http://localhost:18000/docs#/` to interact with the new queue. 