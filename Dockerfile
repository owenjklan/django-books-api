FROM python:3.10-slim

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

WORKDIR /app

ENV DJANGO_SETTINGS_MODULE=django_books_api.settings

EXPOSE 8000

# Using the test server as this isn't a production app deployment.
# Keeping things really simple ;)
CMD [ "python", "manage.py", "runserver" ]
