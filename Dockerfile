FROM python:3.12.4-slim-bookworm

WORKDIR /code

COPY . /code

RUN pip install -r requirements.txt

EXPOSE 8000

CMD [ "python", "/code/backend/app/server.py" ]
