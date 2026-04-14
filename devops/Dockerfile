# Stage 1: Base build stage
FROM python:3.13-slim AS builder

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt


# Stage 2: Production stage
FROM python:3.13-slim

# Install docker CLI
RUN apt-get update && \
    apt-get install -y curl gnupg ca-certificates && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg && \
    echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable' > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce-cli docker-compose-plugin && \
    rm -rf /var/lib/apt/lists/* && \
    which docker && \
    docker --version && \
    docker compose version
# Install git CLI
RUN apt-get update && \
    apt-get install -y git && \
    git config --system --add safe.directory '*' && \
    git --version && \
    rm -rf /var/lib/apt/lists/*

ARG DOCKER_GID=999

RUN useradd -m -r appuser && \
    mkdir /app && \
    mkdir -p /var/run/celery && \
    chown -R appuser /app && \
    chown -R appuser /var/run/celery && \
    groupadd -g ${DOCKER_GID} dockeraccess 2>/dev/null || true && \
    usermod -aG ${DOCKER_GID} appuser && \
    id appuser


COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app

COPY --chown=appuser:appuser . .

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:/usr/bin:/bin:$PATH"

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "dockcd.wsgi:application"]