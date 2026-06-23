# Task 2.1 - Container Images and Process Model

## API image

The required container is the **CityBite Order API** image. I use `python:3.12-slim` as the base image because it is an official Python image, it is smaller than the full Python image, and it is a common choice for web applications.

At a high level, the API image is built in these steps:

1. Set a working directory inside the image.
2. Copy the dependency file and install Python packages.
3. Copy the application source code into the image.
4. Create and use a non-root user.
5. Start the API process with a single container command.

I do not define a separate worker image. The assignment states that the worker is optional, so I keep the design focused on the API container only.

## Runtime contract

The API container requires the following environment variables:

- `PORT` - HTTP port used by the API inside the container
- `DATABASE_URL` - connection string for the managed PostgreSQL database
- `LOG_LEVEL` - controls log verbosity (e.g. INFO, DEBUG)
- `AWS_REGION` - AWS region for the selected cloud provider
- `DATA_DIR` - writable path for menu uploads mounted from Kubernetes storage

The container listens on the port provided via `PORT`, instead of hardcoding a fixed port value.

Logs are written to stdout/stderr instead of files. This allows Kubernetes to collect logs directly and keeps the container filesystem disposable.

## Single responsibility

The container runs one main process: the Order API server. This keeps the container simple and follows the common practice of one main process per container. If background jobs are needed later, they should run in a separate container.

## Dockerfile sketch (API only)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser
USER appuser

EXPOSE 8080

CMD ["python", "app.py"]