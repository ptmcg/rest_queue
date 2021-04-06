FROM python:3.9.2-alpine

WORKDIR /usr/src/app

COPY src .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "uvicorn", "--host", "0.0.0.0", "rest_queue:app" ]


