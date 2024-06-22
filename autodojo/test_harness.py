import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_books_api.settings")

import django

django.setup()

from autodojo import AutoDojoRouter

adr = AutoDojoRouter(app_label="books_api", model="Book")
