from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection
import re

contact_bp = Blueprint("contact", __name__)

@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        # ✅ Server-side validation
        if not name or not email or not message:
            flash("Please fill in all fields!", "error")
            return redirect(url_for("contact.contact"))

        # ✅ Simple email format check
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address!", "error")
            return redirect(url_for("contact.contact"))

        # ✅ Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute(
            "INSERT INTO contact_messages (name, email, message) VALUES (?, ?, ?)",
            (name, email, message)
        )
        conn.commit()
        conn.close()

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for("contact.contact"))

    return render_template("contact.html")


@contact_bp.route("/admin/messages")
def admin_messages():
    """Optional admin page to view stored contact messages"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, email, message, created_at
        FROM contact_messages
        ORDER BY created_at DESC
    """)
    messages = cursor.fetchall()
    conn.close()
    return render_template("messages.html", messages=messages)
