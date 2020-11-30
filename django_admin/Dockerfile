FROM python:3 as base
ENV PYTHONUNBUFFERED=1
WORKDIR /code
RUN apt-get update && apt-get install -y postgresql-client
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
ARG DJANGO_SETTINGS=config.settings.dev
ENV DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS
