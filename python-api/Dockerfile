FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN python3 -m pip install -r requirements.txt

COPY api .

CMD uvicorn main:app --host 0.0.0.0