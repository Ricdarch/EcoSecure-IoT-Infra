FROM python3.12-alpine

WORKDIR /app

RUN apk add --no-cache bash

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "subscriber.py"]