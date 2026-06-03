import requests
r = requests.get("https://roomifybackend.onrender.com/get_layouts")
print(r.text)
