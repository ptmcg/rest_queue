import requests
from rich import print


class RestQueue:
    def __init__(self, host: str, port: int, queue_name: str):
        self._host = host
        self._port = port
        self._queue_name = queue_name
        self._queue_url = f"http://{host}:{port}/queues/{queue_name}"
        self._session = requests.Session()

    def create(self):
        response = self._session.post(self._queue_url)
        return response.status_code, response.json()

    def push(self, value):
        if value is None:
            print(f"pushed value cannot be None")
            return

        url = f"{self._queue_url}/push"
        response = self._session.post(url, params={"value": value})
        if response.status_code == 404:
            print(f"no such queue {self._queue_name!r}")

        return response.json()

    def pop(self):
        url = f"{self._queue_url}/pop"
        response = self._session.post(url)
        if response.status_code == 404:
            print(f"no such queue {self._queue_name!r}")
            return

        return response.json()

    def list(self):
        url = self._queue_url
        response = self._session.get(url)
        if response.status_code == 404:
            print(f"no such queue {self._queue_name!r}")
            return

        return response.json()


if __name__ == '__main__':
    qname = "test"
    rq = RestQueue("localhost", 8000, qname)
    print(rq.create())

    print(rq.push(100))
    print(rq.push("secret message"))
    print(rq.push(3.14159))
    print(rq.push(True))

    print(rq.list())

    print(rq.pop())
