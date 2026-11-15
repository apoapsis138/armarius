# Armarius's listener for Remote seats, for a host with no window: a
# NAS, an always-on Linux box or a small server (ADR 0022, STORY-2284).
#
# Build from the repository's root:
#   docker build -f deploy/Dockerfile -t armarius .
# Run it with deploy/compose.yaml, which adds the read-only root, the
# dropped capabilities, the memory limit, the volumes and the tunnel.
#
# The terminal and desktop front-ends are not in the image: it runs
# `seats` (the listener) and `admin` (the host's chores) only.

# Pinned to an exact Python and Debian release, so a rebuild changes only
# when this line does.
ARG PYTHON_IMAGE=python:3.14.2-slim-trixie

FROM ${PYTHON_IMAGE} AS build
# The same uv that wrote uv.lock, copied from its own image.
COPY --from=ghcr.io/astral-sh/uv:0.9.18 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /app
# The libraries first, so a change to the app's code reuses this layer.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
# --no-dev also leaves out the desktop's gui group (the dev group
# includes it); --frozen installs exactly what uv.lock names.
RUN uv sync --frozen --no-dev

FROM ${PYTHON_IMAGE}
LABEL org.opencontainers.image.title="Armarius" \
      org.opencontainers.image.description="Armarius's listener for Remote seats, for a headless host" \
      org.opencontainers.image.source="https://github.com/apoapsis138/armarius" \
      org.opencontainers.image.licenses="GPL-3.0-only"
# A user of its own with a fixed id, so the volumes on the host can be
# given to it (chown 10001:10001) before the first start.
RUN groupadd --system --gid 10001 armarius \
    && useradd --system --uid 10001 --gid 10001 --no-create-home \
       --home-dir /nonexistent --shell /usr/sbin/nologin armarius \
    && install -d -o 10001 -g 10001 -m 0700 /data /keys /backups
# The app belongs to root and is only read: the listener can't change it.
COPY --from=build /app /app
WORKDIR /app
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    ARMARIUS_DATA=/data \
    ARMARIUS_KEYSTORE=file \
    ARMARIUS_KEYS=/keys \
    ARMARIUS_BACKUPS=/backups \
    ARMARIUS_SOUNDS=off
USER 10001:10001
VOLUME ["/data", "/keys", "/backups"]
# Healthy while the listener takes connections on this container's own
# loopback (nothing is published; the tunnel reaches it the same way).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD ["python", "-c", "import socket; socket.create_connection(('127.0.0.1', 8790), 3).close()"]
# The saga comes from ARMARIUS_SAGA. `docker exec -it armarius python
# main.py admin ...` runs the host's chores beside it.
ENTRYPOINT ["python", "main.py"]
CMD ["seats"]
