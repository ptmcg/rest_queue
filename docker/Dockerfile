FROM python:3.13-alpine

WORKDIR /usr/src/app

# Copy requirements first for better caching
COPY rest_queue/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY rest_queue/src/ .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD [ "uvicorn", "--host", "0.0.0.0", "--port", "8000", "rest_queue:app" ]
