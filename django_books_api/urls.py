"""
URL configuration for django_books_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from books_api.api.v1 import (
    books_router,
    authors_router,
    publishers_router,
    categories_router,
)

api_v1 = NinjaAPI()
api_v1.add_router("/books/", books_router)
api_v1.add_router("/authors/", authors_router)
api_v1.add_router("/publishers/", publishers_router)
api_v1.add_router("/categories/", categories_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_v1.urls),
]
