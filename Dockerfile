FROM python:3.12.4-slim-bookworm

WORKDIR /code

COPY . /code

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD exec uvicorn backend.app.server:app --host 0.0.0.0 --port 8000
