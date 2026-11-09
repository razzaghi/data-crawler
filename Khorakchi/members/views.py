from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import City, MenuItem


def search_view(request):
    cities = City.objects.all().order_by("rank")
    return render(request, "search.html", {"cities": cities})


def product_view(request):
    food = request.GET.get("food", "").strip()
    city = request.GET.get("city", "")

    products = MenuItem.objects.filter(
        is_active=True, title__icontains=food, restaurant__city__code=city
    ).select_related("restaurant", "restaurant__city")

    paginator = Paginator(products, 20)
    page_number = request.GET.get("page")
    products = paginator.get_page(page_number)

    return render(
        request, "products.html", {"products": products, "food": food, "city": city}
    )


def product_detail_view(request, product_id):
    product = get_object_or_404(
        MenuItem.objects.select_related("restaurant", "restaurant__city"),
        id=product_id,
        is_active=True,
    )
    return render(request, "product_detail.html", {"product": product})
