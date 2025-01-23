import requests
import json

URL = "https://zenquotes.io/api/today"

response = requests.get(URL)

json_data = response.json()

print(json_data[0]['q'])
print(f"\t- {json_data[0]['a']}")