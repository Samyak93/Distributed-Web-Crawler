import requests

data = requests.get("http://orchestrator:8000/get_urls")

print(data.json())
print(data.json()["urls"][1])
print(type(data.json()["urls"]))