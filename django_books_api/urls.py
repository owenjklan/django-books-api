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

from autodojo import AutoDojoRouter

from books_api.extra import router as extras_router

# Experimental "V2" for auto-generated router, including ModelSchema
# and views etc.
book_response_schema_configs = {
    "GET": {"depth": 2},
    "GETLIST": {"depth": 2},
}

authors_response_schema_configs = {
    "GET": {"depth": 2},
    "GETLIST": {"depth": 2},
}

books_adr = AutoDojoRouter(
    app_label="books_api",
    model="Book",
    # auth_class=django_auth,  # AutoDojoRouter will create a NinjaAPI class using this, if present.
    response_schema_configs=book_response_schema_configs,
)
authors_adr = AutoDojoRouter(
    app_label="books_api",
    model="Author",
    response_schema_configs=authors_response_schema_configs,
)
categories_adr = AutoDojoRouter(app_label="books_api", model="Category")
publishers_adr = AutoDojoRouter(app_label="books_api", model="Publisher")

api_v2 = NinjaAPI()
api_v2.add_router(*books_adr.add_router_args)
api_v2.add_router(*authors_adr.add_router_args)
api_v2.add_router(*categories_adr.add_router_args)
api_v2.add_router(*publishers_adr.add_router_args)

api_v2.add_router("/book/", extras_router)

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/v1/", api_v1.urls),
    path("api/v2/", api_v2.urls),
]
