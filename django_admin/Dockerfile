FROM python:3 as base
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

FROM base as dev
ENV DJANGO_SETTINGS_MODULE='config.settings.dev'
CMD gunicorn -b 0.0.0.0:8000 config.wsgi
