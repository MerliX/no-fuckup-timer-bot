FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000

ENV BOT_TOKEN your_telegram_bot_token

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
