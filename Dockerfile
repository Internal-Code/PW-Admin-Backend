FROM python:3.13-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN python -m venv "$VIRTUAL_ENV"

# Install only the third-party dependencies into the venv: build+install the
# project to resolve them from pyproject.toml, then drop the project package
# itself. The app runs from the copied source tree in the runtime image, not from
# site-packages (it resolves static/ and env/ relative to the project root).
COPY pyproject.toml README.md ./
COPY app ./app
COPY config ./config
COPY error ./error
COPY middlewares ./middlewares
COPY service ./service
COPY utils ./utils
RUN pip install . && pip uninstall -y pw-admin-backend


FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    ENVIRONMENT=production

WORKDIR /app

RUN useradd --create-home --uid 1000 app \
    && mkdir -p /app/log \
    && chown -R app:app /app

COPY --from=builder /opt/venv /opt/venv

# The app resolves static/ and env/ relative to the project root, so it runs from
# the source tree rather than the installed package.
COPY --chown=app:app . .

USER app
EXPOSE 8000

CMD ["litestar", "--app", "app.main:app", "run", "--host", "0.0.0.0", "--port", "8000"]
