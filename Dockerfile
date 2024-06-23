FROM python:3.10

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

ENV DJANGO_SETTINGS_MODULE=django_books_api.settings

CMD [ "cd /app; python manage.py runserver" ]
