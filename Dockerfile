FROM python:3.9.12-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 1

RUN apk update \
    && apk add --virtual build-essential gcc python3-dev musl-dev freetype-dev libffi-dev \
    && apk add bash nmap \
    && pip install -U pip


WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
