# ================= IMPORTS =================
import requests   # For sending HTTP requests
import time       # For delay between requests
import random     # For selecting random paths


# ================= ROUTE LIST =================
# Different endpoints to simulate normal user behavior
paths = ["/", "/products", "/cart"]


# ================= NORMAL TRAFFIC LOOP =================
while True:
    # Randomly choose a path to request
    path = random.choice(paths)

    try:
        # Send GET request to selected path
        requests.get("http://127.0.0.1:5000" + path)

        # Print confirmation for each request
        print("Normal request")

    except:
        # Ignore errors and continue execution
        pass

    # Wait 1 second before next request (simulates real user behavior)
    time.sleep(1)