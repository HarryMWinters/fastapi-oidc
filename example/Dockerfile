# syntax=docker/dockerfile:experimental
FROM python:3.8.8

RUN apt-get update \
    && apt-get install -y \
        gcc \
        ffmpeg \
        libsm6 \
        libxext6 \
        git \
        curl

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

WORKDIR /app
COPY pyproject.toml .
COPY poetry.lock .

RUN ~/.poetry/bin/poetry install

COPY app app

EXPOSE 8000

CMD ["/root/.poetry/bin/poetry", "run", "python", "-m", "app.main", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]