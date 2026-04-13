from flask import Flask, jsonify, render_template, request
from security import SecurityEngine

app = Flask(__name__)

security = SecurityEngine()
PROTECTION_ENABLED = True

PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 50000},
    {"id": 2, "name": "Phone", "price": 20000},
    {"id": 3, "name": "Headphones", "price": 2000},
]

cart = []

@app.before_request
def firewall():
    global PROTECTION_ENABLED

    if request.path.startswith("/admin"):
        return None

    if not PROTECTION_ENABLED:
        return None

    # ✅ SUPPORT FAKE IP (for attack simulation)
    ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"

    allowed, msg = security.inspect(ip, request.path)

    if not allowed:
        return jsonify({"status": "blocked", "reason": msg}), 429

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/products")
def products_page():
    return render_template("products.html", products=PRODUCTS)

@app.route("/cart")
def cart_page():
    return render_template("cart.html", cart=cart)

@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    pid = data.get("product_id")

    for p in PRODUCTS:
        if p["id"] == pid:
            cart.append(p)
            return jsonify({"message": "Added to cart"})

    return jsonify({"error": "Invalid ID"}), 400

@app.route("/checkout")
def checkout():
    total = sum(p["price"] for p in cart)
    return jsonify({"total": total})

@app.route("/admin/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/admin/blocked")
def blocked():
    return jsonify({"blocked_ips": security.blocked_ips()})

@app.route("/admin/alerts")
def alerts():
    return jsonify({"alerts": security.alerts()})

@app.route("/admin/top-attackers")
def top_attackers():
    return jsonify({"attackers": security.top_attackers()})

@app.route("/admin/protection/on")
def enable_protection():
    global PROTECTION_ENABLED
    PROTECTION_ENABLED = True
    return jsonify({"status": "Protection Enabled"})

@app.route("/admin/protection/off")
def disable_protection():
    global PROTECTION_ENABLED
    PROTECTION_ENABLED = False
    return jsonify({"status": "Protection Disabled"})

@app.route("/admin/protection/status")
def protection_status():
    return jsonify({"enabled": PROTECTION_ENABLED})

if __name__ == "__main__":
    app.run(debug=True)