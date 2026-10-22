FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
COPY packages/ir /opt/cfa-ir
COPY analyzers/python /opt/cfa-python-analyzer

RUN pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir /opt/cfa-ir /opt/cfa-python-analyzer \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app app

COPY backend/app /app/app
COPY backend/alembic.ini /app/alembic.ini
COPY backend/alembic /app/alembic

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
