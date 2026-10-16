import json
import requests

city_name = input("Enter Name Of City: ")

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
all_restaurants = []
establishment_type= input('enter establishment type: ')

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
    for restaurant in  page_restaurants:
       if restaurant["type"] == "VENDOR":
            if restaurant["data"]["establishment"] == establishment_type.upper():
                 all_restaurants.append(restaurant["data"])

    print(f"Page {page}: received {len(page_restaurants)} items; ")
    print( f"total collected: {len(all_restaurants)}")
    

    if len(all_restaurants) >= total_count:
        break

    page += 1

with open("restaurants.json", "w", encoding="utf-8") as file:
    json.dump(all_restaurants, file, ensure_ascii=False, indent=4)

print("Saved items:", len(all_restaurants))