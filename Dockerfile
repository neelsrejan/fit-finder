FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY models ./models
COPY docs/metrics ./docs/metrics
RUN pip install --no-cache-dir .
ENV PORT=8000
ENV FIT_FINDER_ROOT=/app
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn fit_finder.api.app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
