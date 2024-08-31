FROM python:3.11

WORKDIR /app

COPY public_api /app/public_api
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server .