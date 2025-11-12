
from flask import Flask, url_for, render_template, request
from api import api_bp
from db import init_medicine_table, init_orders_table, seed_medicines
from auth import auth_bp
from order import order_bp

app = Flask(__name__)
app.secret_key = "replace_with_a_secure_random_key"

# Register blueprints
app.register_blueprint(api_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(order_bp)

# Initialize DB and seed medicines
init_medicine_table()
init_orders_table()
seed_medicines()

@app.route("/", endpoint="home")
def home():
    return render_template("index.html")

@app.route("/medicines")
def medicines():
    return render_template("medicines.html")

@app.route("/cart")
def cart():
    return render_template("cart.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/track", methods=["GET"])
def track():
    order_id = request.args.get("order_id", "")
    status = None
    order_data = None
    
    if order_id:
        try:
            from db import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, medicine_name, quantity, total_price, delivery_address, 
                       customer_name, status, created_at
                FROM orders WHERE id = ?
                """,
                (order_id,)
            )
            order = cursor.fetchone()
            conn.close()
            
            if order:
                order_data = dict(order)
                status = order_data.get('status', 'pending').title()
                if status == 'Pending':
                    status = 'Order is being processed'
                elif status == 'Out For Delivery' or status == 'In Transit':
                    status = 'Out for delivery'
                elif status == 'Delivered':
                    status = 'Order delivered successfully'
                else:
                    status = f'Status: {status}'
            else:
                status = None
        except Exception as e:
            print(f"Error fetching order: {e}")
            status = None
    else:
        # If no order_id provided, check if there's a demo order
        status = None
    
    return render_template("track.html", order_id=order_id, status=status, order_data=order_data)

if __name__ == "__main__":
    app.run(debug=True)