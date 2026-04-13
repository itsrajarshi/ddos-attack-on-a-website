import requests
import time
import random

paths = ["/", "/products", "/cart"]

while True:
    path = random.choice(paths)
    try:
        requests.get("http://127.0.0.1:5000" + path)
        print("Normal request")
    except:
        pass
    time.sleep(1)