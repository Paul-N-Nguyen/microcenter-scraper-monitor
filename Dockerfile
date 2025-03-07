FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install python
RUN uv python install 3.12

# Install dependencies
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Copy the project into the image
ADD . /app

# Add binaries from the project's virtual environment to the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

ENTRYPOINT ["python", "main.py", "--store", "microcenter"]
