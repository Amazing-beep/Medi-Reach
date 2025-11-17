from flask import Flask, url_for, render_template, request  # Import Flask core and helpers
from api import api_bp  # Import API blueprint for REST endpoints
from db import init_medicine_table, init_orders_table, seed_medicines  # DB init and seed functions
from auth import auth_bp  # Auth routes blueprint
from order import order_bp  # Order routes blueprint

app = Flask(__name__)  # Create Flask app instance
app.secret_key = "replace_with_a_secure_random_key"  # Secret key for session/flash (replace in production)

# Register blueprints to attach route groups to the app
app.register_blueprint(api_bp)  # Attach /api endpoints
app.register_blueprint(auth_bp)  # Attach /auth, /login, /signup, /logout
app.register_blueprint(order_bp)  # Attach /order related endpoints

# Initialize DB and seed medicines at startup (idempotent)
init_medicine_table()  # Ensure medicines table exists
init_orders_table()  # Ensure orders table exists
seed_medicines()  # Insert demo medicines if table is empty

@app.route("/", endpoint="home")  # Home page route

def home():  # Handler for home page
    return render_template("index.html")  # Render landing page template

@app.route("/medicines")  # Medicines listing page route

def medicines():  # Handler for medicines page
    return render_template("medicines.html")  # Render medicines template

@app.route("/cart")  # Cart page route

def cart():  # Handler for cart page
    return render_template("cart.html")  # Render cart template

@app.route("/contact")  # Contact page route

def contact():  # Handler for contact page
    return render_template("contact.html")  # Render contact template

@app.route("/track", methods=["GET"])  # Order tracking page route

def track():  # Handler for tracking by order_id query param
    order_id = request.args.get("order_id", "")  # Read order_id from URL query string
    status = None  # Human-friendly status text to show
    order_data = None  # Full order dict for display
    
    if order_id:  # Only query DB if an order_id was provided
        try:
            from db import get_db_connection  # Import locally to avoid circular import
            conn = get_db_connection()  # Open DB connection
            cursor = conn.cursor()  # Create cursor for queries
            cursor.execute(  # Fetch order by id
                """
                SELECT id, medicine_name, quantity, total_price, delivery_address, 
                       customer_name, status, created_at
                FROM orders WHERE id = ?
                """,
                (order_id,)
            )
            order = cursor.fetchone()  # Get single matching row
            conn.close()  # Close connection
            
            if order:  # If order exists, transform and format status
                order_data = dict(order)  # Convert Row to dict for template
                status = order_data.get('status', 'pending').title()  # Normalize status
                if status == 'Pending':  # Map raw statuses to friendly text
                    status = 'Order is being processed'
                elif status == 'Out For Delivery' or status == 'In Transit':
                    status = 'Out for delivery'
                elif status == 'Delivered':
                    status = 'Order delivered successfully'
                else:
                    status = f'Status: {status}'
            else:
                status = None  # No order found
        except Exception as e:  # Log and fall back silently
            print(f"Error fetching order: {e}")  # Print error to console
            status = None  # Do not expose raw error to user
    else:
        status = None  # No order_id provided
    
    return render_template("track.html", order_id=order_id, status=status, order_data=order_data)  # Render tracking page

if __name__ == "__main__":  # Run only if invoked directly
    app.run(debug=True)  # Start dev server with auto-reload and debug