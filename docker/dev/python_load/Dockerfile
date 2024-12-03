FROM python:3.8-slim

RUN apt-get update -y && apt-get install -y libpq-dev gcc

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt