from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Create Blueprint for auth routes
auth_bp = Blueprint('auth', __name__)

# Database configuration
DB_PATH = os.path.join('instance', 'medi_reach.db')

def get_db_connection():
    """Create and return a database connection"""
    # Create database directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with users table"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                address TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def add_user(name, phone, address, password):
    """Add a new user to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (name, phone, address, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, address, password_hash))
        
        conn.commit()
        print(f"User {name} registered successfully!")
        return True
        
    except sqlite3.IntegrityError:
        print(f"Phone number {phone} already exists!")
        return False
    except Exception as e:
        print(f"Error adding user: {e}")
        return False
    finally:
        conn.close()

def verify_user(phone, password):
    """Verify user credentials"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, name, phone, password_hash FROM users WHERE phone = ?
        ''', (phone,))
        
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            print(f"User {user['name']} logged in successfully!")
            return {
                'id': user['id'],
                'name': user['name'], 
                'phone': user['phone']
            }
        else:
            print(f"Login failed for phone: {phone}")
            return None
            
    except Exception as e:
        print(f"Error verifying user: {e}")
        return None
    finally:
        conn.close()

# Initialize database when this module is imported
init_db()

# Authentication Routes
@auth_bp.route('/auth')
def auth_page():
    """Display login/signup page"""
    return render_template('auth.html')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Handle user registration"""
    try:
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not all([name, phone, address, password, confirm_password]):
            flash('Please fill in all fields!', 'error')
            return redirect(url_for('auth.auth_page'))
        
        if len(phone) < 10:
            flash('Please enter a valid phone number!', 'error')
            return redirect(url_for('auth.auth_page'))
            
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('auth.auth_page'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return redirect(url_for('auth.auth_page'))
        
        # Add user to database
        if add_user(name, phone, address, password):
            # Auto-login after successful signup
            user = verify_user(phone, password)
            if user:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_phone'] = user['phone']
                session['logged_in'] = True
                flash(f'Welcome, {user["name"]}! Your account has been created.', 'success')
                return redirect(url_for('medicines'))
            else:
                flash('Account created, please login.', 'success')
                return redirect(url_for('auth.auth_page'))
        else:
            flash('Phone number already exists! Please use a different number.', 'error')
            return redirect(url_for('auth.auth_page'))
            
    except Exception as e:
        print(f"Signup error: {e}")
        flash('An error occurred during registration. Please try again.', 'error')
        return redirect(url_for('auth.auth_page'))

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle user login"""
    try:
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        
        if not phone or not password:
            flash('Please enter both phone number and password!', 'error')
            return redirect(url_for('auth.auth_page'))
        
        # Verify user credentials
        user = verify_user(phone, password)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_phone'] = user['phone']
            session['logged_in'] = True
            
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect('/medicines')
            
        else:
            flash('Invalid phone number or password!', 'error')
            return redirect(url_for('auth.auth_page'))
            
    except Exception as e:
        print(f"Login error: {e}")
        flash('An error occurred during login. Please try again.', 'error')
        return redirect(url_for('auth.auth_page'))

@auth_bp.route('/logout')
def logout():
    """Handle user logout"""
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('auth.auth_page'))