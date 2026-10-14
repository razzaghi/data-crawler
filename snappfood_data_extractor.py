import json
import requests

city_name = input("enter name of city: ")

url = "https://snappfood.ir/mobile/v2/area/cities"
headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

response = requests.get(url, headers=headers)

lat = None
long = None

if response.status_code == 200:
    data = response.json()
    for city in data["data"]["cities"]:
        if city["title"] == city_name:
            lat = city["latitude"]
            long = city["longitude"]
            print(city["code"])
            print(lat)
            print(long)
else:
    print(response.status_code)


url = f"https://snappfood.ir/search/api/v1/desktop/vendors-list?latitude={lat}&longitude={long}"

response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)
print("Response:", response.text)

if response.status_code == 200:
    data = response.json()
    json_print = json.dumps(data, indent=4, ensure_ascii=False)
    with open('data.json', 'w', encoding='utf-8') as file:
        file.write(json_print)
