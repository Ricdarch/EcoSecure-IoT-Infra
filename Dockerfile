FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MQTT_BROKER=localhost
ENV MQTT_PORT=8883
ENV CONFIG_FILE=devices_config.json
ENV PYTHONUNBUFFERED=1 

CMD ["python", "device_mock.py"]