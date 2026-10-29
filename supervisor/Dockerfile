FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --system --uid 10002 --no-create-home appuser

COPY supervisor.py .
USER 10002:10002

CMD ["python", "supervisor.py"]
