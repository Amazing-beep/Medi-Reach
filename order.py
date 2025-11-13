from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from db import get_db_connection
import json

order_bp = Blueprint("order", __name__)


@order_bp.route("/order")
def order():
    """Display order form with available medicines."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM medicines ORDER BY name")
    medicines = [dict(row) for row in cursor.fetchall()]
    conn.close()

    user_id = session.get("user_id")
    user_name = session.get("user_name", "")

    return render_template("order.html", medicines=medicines, user_name=user_name)


@order_bp.route("/order/submit", methods=["POST"])
def submit_order():
    """Handle order submission and store in database."""
    try:
        medicine_id = request.form.get("medicine_id")
        quantity = request.form.get("quantity", "1")
        delivery_address = request.form.get("address", "").strip()
        customer_name = request.form.get("customer_name", "").strip()

        if not medicine_id:
            flash("Please select a medicine!", "error")
            return redirect(url_for("order.order"))

        if not delivery_address:
            flash("Delivery address is required!", "error")
            return redirect(url_for("order.order"))

        if not customer_name:
            flash("Your name is required!", "error")
            return redirect(url_for("order.order"))

        try:
            medicine_id = int(medicine_id)
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        except ValueError:
            flash("Invalid quantity!", "error")
            return redirect(url_for("order.order"))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, price FROM medicines WHERE id = ?", (medicine_id,))
        medicine = cursor.fetchone()

        if not medicine:
            conn.close()
            flash("Medicine not found!", "error")
            return redirect(url_for("order.order"))

        total_price = float(medicine["price"]) * quantity
        user_id = session.get("user_id")

        cursor.execute(
            """
            INSERT INTO orders (user_id, medicine_id, medicine_name, quantity, total_price, delivery_address, customer_name, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        """,
            (
                user_id,
                medicine_id,
                medicine["name"],
                quantity,
                total_price,
                delivery_address,
                customer_name,
            ),
        )

        order_id = cursor.lastrowid
        conn.commit()
        conn.close()

        flash("Order placed successfully!", "success")
        return redirect(url_for("order.confirm_order", order_id=order_id))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("order.order"))


@order_bp.route("/payment")
def payment():
    """Display payment page with cart items."""
    user_name = session.get("user_name", "")
    return render_template("payment.html", user_name=user_name)


@order_bp.route("/payment/create-draft-order", methods=["POST"])
def create_draft_order():
    """Create or update a draft order immediately when payment page loads."""
    try:
        data = request.get_json(silent=True) or {}
        cart = data.get("cart_data", [])
        order_id = data.get("order_id")

        if not order_id:
            return jsonify({"error": "Order ID is required"}), 400

        if not cart or len(cart) == 0:
            return jsonify({"error": "Cart is empty"}), 400

        try:
            order_id = int(order_id)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid order ID"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Calculate total price
        try:
            total_price = sum(float(item["price"]) * int(item["quantity"]) for item in cart)
        except (KeyError, TypeError, ValueError):
            conn.close()
            return jsonify({"error": "Invalid cart item data"}), 400

        # Create or update draft order with placeholder info
        user_id = session.get("user_id")
        cursor.execute("SELECT id FROM orders WHERE id = ?", (order_id,))
        existing_order = cursor.fetchone()

        if existing_order:
            cursor.execute(
                """
                UPDATE orders
                SET total_price = ?, delivery_address = ?, customer_name = ?, status = 'pending'
                WHERE id = ?
            """,
                (total_price, "Pending address", "Pending customer", order_id),
            )
            cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        else:
            cursor.execute(
                """
                INSERT INTO orders (id, user_id, total_price, delivery_address, customer_name, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """,
                (
                    order_id,
                    user_id,
                    total_price,
                    "Pending address",
                    "Pending customer",
                ),
            )

        # Insert order items
        for item in cart:
            cursor.execute(
                """
                INSERT INTO order_items (order_id, medicine_id, medicine_name, quantity, price)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    order_id,
                    item.get("id"),
                    item.get("name"),
                    item.get("quantity"),
                    item.get("price"),
                ),
            )

        conn.commit()
        conn.close()

        return jsonify({"order_id": order_id, "success": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@order_bp.route("/payment/process", methods=["POST"])
def process_payment():
    """Process payment and update existing draft order."""
    try:
        customer_name = request.form.get("customer_name", "").strip()
        delivery_address = request.form.get("delivery_address", "").strip()
        order_id = request.form.get("order_id", "")
        cart_data = request.form.get("cart_data", "[]")

        if not customer_name:
            flash("Your name is required!", "error")
            return redirect(url_for("order.payment"))

        if not delivery_address:
            flash("Delivery address is required!", "error")
            return redirect(url_for("order.payment"))

        if not order_id:
            flash("Order ID is missing!", "error")
            return redirect(url_for("order.payment"))

        try:
            order_id = int(order_id)
        except ValueError:
            flash("Invalid order ID!", "error")
            return redirect(url_for("order.payment"))

        try:
            cart = json.loads(cart_data) if cart_data else []
        except json.JSONDecodeError:
            cart = []

        conn = get_db_connection()
        cursor = conn.cursor()

        # Recalculate total based on submitted cart data (if provided)
        total_price = None
        if cart:
            try:
                total_price = sum(float(item["price"]) * int(item["quantity"]) for item in cart)
            except (KeyError, TypeError, ValueError):
                total_price = None

        # Check if order exists
        cursor.execute("SELECT id FROM orders WHERE id = ?", (order_id,))
        existing_order = cursor.fetchone()

        if not existing_order:
            # Create order if it doesn't exist yet
            if not cart:
                flash("Unable to locate order. Please refresh and try again.", "error")
                conn.close()
                return redirect(url_for("order.payment"))

            cursor.execute(
                """
                INSERT INTO orders (id, user_id, total_price, delivery_address, customer_name, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            """,
                (
                    order_id,
                    session.get("user_id"),
                    total_price or 0,
                    delivery_address,
                    customer_name,
                ),
            )
        else:
            cursor.execute(
                """
                UPDATE orders 
                SET delivery_address = ?, customer_name = ?, total_price = COALESCE(?, total_price)
                WHERE id = ?
            """,
                (delivery_address, customer_name, total_price, order_id),
            )

        # Refresh order items if cart data is available
        if cart:
            cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            for item in cart:
                cursor.execute(
                    """
                    INSERT INTO order_items (order_id, medicine_id, medicine_name, quantity, price)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        order_id,
                        item.get("id"),
                        item.get("name"),
                        item.get("quantity"),
                        item.get("price"),
                    ),
                )

        conn.commit()
        conn.close()

        flash("Order placed successfully!", "success")
        return redirect(url_for("order.confirm_order", order_id=order_id))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for("order.payment"))


@order_bp.route("/payment/delete-draft-order", methods=["POST"])
def delete_draft_order():
    """Delete a draft order and its items."""
    try:
        data = request.get_json(silent=True) or {}
        order_id = data.get("order_id")

        if not order_id:
            return jsonify({"success": True}), 200  # Nothing to delete

        try:
            order_id = int(order_id)
        except (ValueError, TypeError):
            return jsonify({"success": False}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM order_items WHERE order_id = ?
        """,
            (order_id,),
        )
        cursor.execute(
            """
            DELETE FROM orders WHERE id = ?
        """,
            (order_id,),
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True}), 200

    except Exception:
        return jsonify({"success": False}), 500


@order_bp.route("/order/confirm/<int:order_id>")
def confirm_order(order_id):
    """Display order confirmation with order ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, total_price, delivery_address, customer_name, status, created_at
        FROM orders WHERE id = ?
    """,
        (order_id,),
    )
    order = cursor.fetchone()

    if not order:
        conn.close()
        flash("Order not found!", "error")
        return redirect(url_for("order.payment"))

    # Get order items
    cursor.execute(
        """
        SELECT medicine_name, quantity, price
        FROM order_items WHERE order_id = ?
    """,
        (order_id,),
    )
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()

    order_dict = dict(order)
    order_dict["items"] = items

    return render_template("order_confirm.html", order=order_dict)

