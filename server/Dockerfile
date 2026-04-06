FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY . /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libmagic1 file \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install .

RUN chmod +x /app/docker-entrypoint.sh

EXPOSE 6543

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "-m", "pyramid.scripts.pserve", "docker.ini", "http_port=6543"]
