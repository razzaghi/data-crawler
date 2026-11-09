from django.urls import path
from . import views

urlpatterns = [
    path("", views.search_view, name="search"),
    path("products/", views.product_view, name="products"),
    path("product/<int:product_id>/", views.product_detail_view, name="product_detail"),
]
