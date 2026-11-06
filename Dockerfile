# LocalityLens: review screen, JSON API and worker in one image.
# Base images are pinned by digest. Data (snapshots, gazetteer, review store, reviewed extents)
# is mounted at /app/data and never baked in.
FROM ghcr.io/astral-sh/uv:0.12.5@sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1 AS uv

FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df

COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    LOCALITYLENS_CONTAINER=1

WORKDIR /app
RUN useradd --create-home --uid 10001 localitylens

# Dependencies first (cached unless the lockfile changes), then the project itself.
COPY pyproject.toml uv.lock README.md LICENSE ./
RUN uv sync --locked --no-dev --extra otel --no-install-project
COPY src ./src
COPY release ./release
RUN uv sync --locked --no-dev --extra otel && chown -R localitylens /app

USER localitylens
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import sys, urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/readyz', timeout=4).status == 200 else 1)"]
ENTRYPOINT ["localitylens"]
CMD ["--help"]
