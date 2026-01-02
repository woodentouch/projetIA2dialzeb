FROM python:3.11-slim

ARG PLAYWRIGHT_INSTALL=false
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y build-essential libpq-dev curl git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
# Upgrade pip/setuptools/wheel first to avoid wheel/compatibility issues
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers only when explicitly requested to keep image small by default
RUN if [ "$PLAYWRIGHT_INSTALL" = "true" ] ; then playwright install --with-deps ; fi || true

COPY app ./app
COPY data ./data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
