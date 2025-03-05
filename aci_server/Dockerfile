FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Allow for environment variables to be passed at runtime
ENV SENTRY_URL=""

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]