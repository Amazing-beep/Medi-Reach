from flask import Flask, url_for, render_template, request
from api import api_bp
from db import init_medicine_table, init_orders_table, seed_medicines
from auth import auth_bp
from order import order_bp
from contact import contact_bp  # ✅ new import

app = Flask(__name__)
app.secret_key = "replace_with_a_secure_random_key"

# ✅ Register blueprints
app.register_blueprint(api_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(order_bp)
app.register_blueprint(contact_bp)  # includes /contact and /admin/messages

# ✅ Initialize database and seed data
init_medicine_table()
init_orders_table()
seed_medicines()

# ✅ Simple navigation bar function
def nav():
    return (
        f'<nav style="display:flex;gap:12px;padding:12px 0;">'
        f'<a href="{url_for("home")}">Home</a>'
        f'<a href="{url_for("medicines")}">Medicines</a>'
        f'<a href="{url_for("order.order")}">Order</a>'
        f'<a href="{url_for("contact.contact")}">Contact</a>'
        f'</nav><hr/>'
    )

# ✅ Home route
@app.route("/", endpoint="home")
def home():
    return (
        nav()
        + "<h1>Medi-Reach</h1>"
        + "<p>Welcome. Use the navigation to browse medicines, place an order, or contact us.</p>"
    )

# ✅ Medicines page
@app.route("/medicines")
def medicines():
    return render_template("medicines.html")

# ✅ Tracking route (you can keep this)
@app.route("/track", methods=["GET"])
def track():
    order_id = request.args.get("order_id", "")
    status = None
    if order_id:
        # Mock status logic
        status = "Out for delivery" if order_id == "123" else "Order not found. Try 123."
    return render_template("track.html", order_id=order_id, status=status)

# ✅ Run app
if __name__ == "__main__":
    app.run(debug=True)
