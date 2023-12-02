FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt && rm requirements.txt

WORKDIR /app
COPY . /app
