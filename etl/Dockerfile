FROM python:3.9-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY /etl_app /

EXPOSE 5432/tcp

CMD ["python3", "./etl.py"]
