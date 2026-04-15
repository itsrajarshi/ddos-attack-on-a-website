# ================= IMPORTS =================
from flask import Flask, jsonify, render_template, request
from security import SecurityEngine  # Custom security module

# ================= APP INITIALIZATION =================
app = Flask(__name__)

# Initialize security engine
security = SecurityEngine()

# Global flag to enable/disable protection
PROTECTION_ENABLED = True

# ================= SAMPLE PRODUCT DATA =================
PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 50000},
    {"id": 2, "name": "Phone", "price": 20000},
    {"id": 3, "name": "Headphones", "price": 2000},
]

# Cart storage (in-memory)
cart = []

# ================= FIREWALL (BEFORE EVERY REQUEST) =================
@app.before_request
def firewall():
    global PROTECTION_ENABLED

    # Skip protection for admin routes
    if request.path.startswith("/admin"):
        return None

    # Skip if protection is disabled
    if not PROTECTION_ENABLED:
        return None

    # Get client IP (supports fake IP for attack simulation)
    ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"

    # Inspect request using security engine
    allowed, msg = security.inspect(ip, request.path)

    # Block request if not allowed
    if not allowed:
        return jsonify({"status": "blocked", "reason": msg}), 429


# ================= ROUTES =================

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Products page
@app.route("/products")
def products_page():
    return render_template("products.html", products=PRODUCTS)


# Cart page
@app.route("/cart")
def cart_page():
    return render_template("cart.html", cart=cart)


# Add product to cart (POST request)
@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    # Get JSON data from request
    data = request.get_json()
    pid = data.get("product_id")

    # Find product by ID and add to cart
    for p in PRODUCTS:
        if p["id"] == pid:
            cart.append(p)
            return jsonify({"message": "Added to cart"})

    # Return error if product ID is invalid
    return jsonify({"error": "Invalid ID"}), 400


# Checkout route (calculate total price)
@app.route("/checkout")
def checkout():
    total = sum(p["price"] for p in cart)
    return jsonify({"total": total})


# ================= ADMIN ROUTES =================

# Dashboard page
@app.route("/admin/dashboard")
def dashboard():
    return render_template("dashboard.html")


# Get blocked IPs
@app.route("/admin/blocked")
def blocked():
    return jsonify({"blocked_ips": security.blocked_ips()})


# Get alert logs
@app.route("/admin/alerts")
def alerts():
    return jsonify({"alerts": security.alerts()})


# Get top attackers
@app.route("/admin/top-attackers")
def top_attackers():
    return jsonify({"attackers": security.top_attackers()})


# Enable protection
@app.route("/admin/protection/on")
def enable_protection():
    global PROTECTION_ENABLED
    PROTECTION_ENABLED = True
    return jsonify({"status": "Protection Enabled"})


# Disable protection
@app.route("/admin/protection/off")
def disable_protection():
    global PROTECTION_ENABLED
    PROTECTION_ENABLED = False
    return jsonify({"status": "Protection Disabled"})


# Get protection status
@app.route("/admin/protection/status")
def protection_status():
    return jsonify({"enabled": PROTECTION_ENABLED})


# ================= RUN APPLICATION =================
if __name__ == "__main__":
    # Run Flask app in debug mode
    app.run(debug=True)