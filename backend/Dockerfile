FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir --default-timeout=120 --retries=5 .

COPY app ./app
COPY alembic.ini .
COPY migrations ./migrations
# Reference BRD corpus (data/reference_brds/*.docx + app/ai/rag/config/*.json)
# needed by `python -m app.ai.rag.cli --all` to seed the RAG reference
# corpus — run manually, once, after the stack is up (see deploy docs).
COPY data ./data

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
