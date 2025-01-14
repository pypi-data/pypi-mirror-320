FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# - Silence uv complaining about not being able to use hard links,
# - tell uv to byte-compile packages for faster application startups,
# - prevent uv from accidentally downloading isolated Python builds,
# - pick the Python inside the venv (created later),
# - and finally declare `/app` as the target for `uv sync`.
ENV PATH=/app/.venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12

RUN apt-get update -qy \
    && apt-get install -qyy --no-install-recommends --no-install-suggests \
    # required by dbnomics-fetcher-ops
    openssh-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

ADD . /app

RUN --mount=type=cache,target=/root/.cache \
    uv sync --locked --no-dev

RUN python -V ; \
    python -Im site ; \
    python -Ic 'import dbnomics_fetchers_ops'

ENTRYPOINT ["dbnomics-fetchers"]
