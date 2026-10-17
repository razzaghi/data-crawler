import json
from pathlib import Path
import pandas as pd
import requests

city_name = input("enter name of city: ")

headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36",
}

cities_url = "https://snappfood.ir/mobile/v2/area/cities"
response = requests.get(cities_url, headers=headers)

if response.status_code != 200:
    print(response.status_code)
cities_data = response.json()
lat = None
long = None

for city in cities_data["data"]["cities"]:
    if city["code"].lower() == city_name.lower():
        lat = city["latitude"]
        long = city["longitude"]
        city_name = city["code"]
        break

if lat is None or long is None:
    print("City not found")

print("City:", city_name)
print("Latitude:", lat)
print("Longitude:", long)

url = "https://snappfood.ir/search/api/v4/restaurant/vendors-list"

page = 0
page_size = 50
total_count = None
all_data = []
establishment_set = set()

while True:
    params = {
        "lat": lat,
        "long": long,
        "city_name": city_name,
        "page": page,
        "page_size": page_size,
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        print("Request failed:", response.status_code)
        break

    data = response.json()
    data = data["data"]

    if total_count is None:
        total_count = data["count"]
        print("Total restaurants:", total_count)
        print("Open restaurants:", data["open_count"])
    page_restaurants = data["finalResult"]

    if not page_restaurants:
        print("No more results received.")
        break
    for restaurant in page_restaurants:
        if restaurant["type"] == "VENDOR":
            all_data.append(restaurant["data"])
            establishment_set.add(restaurant["data"]["establishment"])

    print(f"Page {page}: received {len(page_restaurants)} items; ")
    print(f"total collected: {len(all_data)}")

    if len(all_data) >= total_count:
        break

    page += 1

for establishment in sorted(establishment_set):
    print(establishment)

establishment_type = input("enter establishment type: ").upper()
filtered_data = []
for data in all_data:
    if data["establishment"] == establishment_type:
        filtered_data.append(data)

with open("data.json", "w", encoding="utf-8") as file:
    json.dump(filtered_data, file, ensure_ascii=False, indent=4)

print("Saved items:", len(filtered_data))

city_folder = Path("menus") / city_name / establishment_type.lower()
city_folder.mkdir(parents=True, exist_ok=True)

for vendor in filtered_data:
    vendor_code = vendor["vendorCode"]
    menu_url = f"https://apigw.snappfood.ir/menu-read-model/{vendor_code}"
    params = {"lat": vendor["lat"], "long": vendor["lon"]}

    response = requests.get(menu_url, params=params, headers=headers)
    if response.status_code != 200:
        print(response.status_code)
        continue
    menu_data = response.json()
    all_foods = []
    for category in menu_data["data"]["menuCategories"]:
        for product in category["products"]:
            images = product.get("images", [])
            variations = product.get("variations", [])
            image_url = images[0].get("src") if images else None
            for variation in variations:
                food_item = {
                    "food_title": product["title"],
                    "food_description": product["description"].strip(),
                    "food_price": variation["price"],
                    "is_active": variation["active"],
                    "image_url": image_url,
                }
                all_foods.append(food_item)


    df = pd.DataFrame(all_foods)
    file_path = city_folder / f"{vendor['title']}.csv"
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    print("Saved:", vendor["title"], "-", len(df), "foods")
