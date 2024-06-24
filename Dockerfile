FROM python:3.10-slim

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

COPY testing/clean_start.sh /clean_start.sh

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=django_books_api.settings

EXPOSE 8000

CMD [ "/clean_start.sh" ]
