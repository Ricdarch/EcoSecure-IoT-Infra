FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache bash

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MQTT_BROKER=localhost MQTT_PORT=8883 PYTHONUNBUFFERED=1

CMD ["python", "publisher.py"]