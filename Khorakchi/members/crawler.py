from .models import City, Restaurant, MenuItem
import asyncio
import aiohttp


headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
}


async def get_city(session):
    cities_url = "https://snappfood.ir/mobile/v2/area/cities"
    async with session.get(cities_url, headers=headers) as response:
        response.raise_for_status()
        cities_data = await response.json()
    return cities_data["data"]["cities"]


async def save_city_data(session):
    cities = await get_city(session)
    for city in cities:
        await City.objects.aupdate_or_create(
            source_id=city["id"],
            defaults={
                "code": city["code"],
                "title": city["title"],
                "latitude": city["latitude"],
                "longitude": city["longitude"],
                "rank": city["rank"],
            },
        )


async def get_restaurants(session, city):
    url = "https://snappfood.ir/search/api/v4/restaurant/vendors-list"

    page = 0
    page_size = 50
    all_restaurants = []

    while True:
        params = {
            "lat": city.latitude,
            "long": city.longitude,
            "city_name": city.code,
            "page": page,
            "page_size": page_size,
        }

        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            data = await response.json()
        data = data["data"]
        page_restaurants = data["finalResult"]

        if not page_restaurants:
            break

        for restaurant in page_restaurants:
            if restaurant["type"] == "VENDOR":
                all_restaurants.append(restaurant["data"])

        page += 1

    return all_restaurants


async def save_restaurants(session):
    cities = City.objects.all()

    async for city in cities:
        restaurants = await get_restaurants(session, city)
        for restaurant in restaurants:
            lat = restaurant.get("lat")
            lon = restaurant.get("lon")

            if lat is None or lon is None:
                continue

            await Restaurant.objects.aupdate_or_create(
                vendor_code=restaurant["vendorCode"],
                defaults={
                    "source_id": restaurant["id"],
                    "title": restaurant["title"],
                    "address": restaurant.get("address", ""),
                    "city": city,
                    "rate": restaurant["rate"],
                    "menu_url": f"https://snappfood.ir/restaurant/menu/{restaurant['vendorCode']}/",
                    "is_open": restaurant["isOpen"],
                    "establishment": restaurant["establishment"],
                    "lat": restaurant["lat"],
                    "lon": restaurant["lon"],
                },
            )


async def get_restaurant_menu(session, restaurant):
    menu_url = f"https://apigw.snappfood.ir/menu-read-model/{restaurant.vendor_code}"

    async with session.get(menu_url, headers=headers) as response:
        response.raise_for_status()
        response_data = await response.json()
    menu_data = response_data.get("menu", response_data)

    data = menu_data.get("data") or {}
    menu_categories = data.get("menuCategories") or []

    if not menu_categories:
        return []

    all_foods = []

    for category in menu_categories:
        for product in category["products"]:
            images = product.get("images", [])
            image_url = images[0].get("src", "") if images else ""

            variations = product.get("variations", [])

            for variation in variations:
                food_item = {
                    "source_alias": str(variation["id"]),
                    "title": product["title"],
                    "description": (product.get("description") or "").strip(),
                    "price": variation["price"],
                    "is_active": variation["active"],
                    "rate": variation.get("rate", product.get("rate")),
                    "image_url": image_url,
                }

                all_foods.append(food_item)

    return all_foods


async def save_restaurant_menu(session, restaurant):
    try:
        foods = await get_restaurant_menu(session, restaurant)
        if not foods:
            print(f"Skipped empty menu: {restaurant.title}")
            return

        for food in foods:
            if not foods:
                print(f"Empty menu: {restaurant.title}")
                return
            await MenuItem.objects.aupdate_or_create(
                source_alias=food["source_alias"],
                restaurant=restaurant,
                defaults={
                    "title": food["title"],
                    "description": food["description"],
                    "price": food["price"],
                    "is_active": food["is_active"],
                    "rate": food["rate"],
                    "image_url": food["image_url"],
                },
            )
    except aiohttp.ClientResponseError as e:
        if e.status == 500:
            print(f"Skipped server error: {restaurant.title}")
            return
        raise


async def save_all_restaurant_menus(session):
    restaurants = Restaurant.objects.all()

    tasks = []

    async for restaurant in restaurants:
        tasks.append(save_restaurant_menu(session, restaurant))

        if len(tasks) == 5:
            await asyncio.gather(*tasks)
            tasks = []

    if tasks:
        await asyncio.gather(*tasks)


async def run_async_crawler():
    timeout = aiohttp.ClientTimeout(total=30)

    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        await save_city_data(session)
        await save_restaurants(session)
        await save_all_restaurant_menus(session)
