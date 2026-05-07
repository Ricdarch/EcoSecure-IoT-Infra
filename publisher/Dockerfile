FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MQTT_BROKER=localhost MQTT_PORT=8883 CONFIG_FILE=devices_config.json PYTHONUNBUFFERED=1

CMD ["python", "publisher.py"]