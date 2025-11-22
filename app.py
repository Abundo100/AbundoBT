# app.py — FULLY FIXED VERSION

import os
import secrets
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Trip, Booking, User

app = Flask(__name__)

# -------------------------
# CONFIG
# -------------------------
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devkey123')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bus_booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# -------------------------
# INIT DATABASE
# -------------------------
with app.app_context():
    db.create_all()  # Creates tables based on current models


# ============================================
# HOME PAGE
# ============================================
@app.route('/')
def index():
    trips = Trip.query.order_by(Trip.id).all()
    return render_template('index.html', trips=trips)


# ============================================
# REGISTER
# ============================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']
        role = request.form.get('role', 'user')

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_pw, role=role)

        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can now log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# ============================================
# LOGIN
# ============================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for('login'))

        session['user_id'] = user.id
        session['user_name'] = user.name
        session['role'] = user.role

        flash(f"Welcome, {user.name}!", "success")
        return redirect(url_for('admin' if user.role == 'admin' else 'index'))

    return render_template('login.html')


# ============================================
# LOGOUT
# ============================================
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# ============================================
# BOOK TRIP
# ============================================
@app.route('/book/<int:trip_id>', methods=['GET', 'POST'])
def book(trip_id):
    if "user_id" not in session:
        flash("Log in first to book a trip.", "warning")
        return redirect(url_for('login'))

    trip = Trip.query.get_or_404(trip_id)

    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        seats = int(request.form['seats'])

        if seats <= 0 or seats > trip.seats_left:
            flash("Invalid seat count.", "danger")
            return redirect(url_for('book', trip_id=trip_id))

        booking = Booking(
            trip_id=trip.id,
            passenger_name=name,
            passenger_contact=contact,
            seats_booked=seats
        )

        trip.seats_left -= seats
        db.session.add(booking)
        db.session.commit()

        flash("Booking successful!", "success")
        return redirect(url_for('bookings'))

    return render_template('book.html', trip=trip)


# ============================================
# VIEW BOOKINGS
# ============================================
@app.route('/bookings')
def bookings():
    if "user_id" not in session:
        return redirect(url_for('login'))

    all_bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('bookings.html', bookings=all_bookings)


# ============================================
# ADMIN DASHBOARD
# ============================================
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.get("role") != "admin":
        flash("Admin access only.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            route = request.form['route']
            departure = request.form['departure']
            price = float(request.form['price'])
            seats = int(request.form['seats'])

            trip = Trip(route=route, departure=departure, price=price,
                        seats_total=seats, seats_left=seats)

            db.session.add(trip)
            db.session.commit()
            flash("Trip added!", "success")

        elif action == 'delete':
            trip_id = int(request.form['trip_id'])
            trip = Trip.query.get(trip_id)

            if trip:
                db.session.delete(trip)
                db.session.commit()
                flash("Trip deleted.", "info")

        return redirect(url_for('admin'))

    trips = Trip.query.order_by(Trip.id).all()
    return render_template('admin.html', trips=trips)


# ============================================
# USER PROFILE
# ============================================
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if "user_id" not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        new_name = request.form["name"].strip()
        new_email = request.form["email"].strip().lower()
        new_contact = request.form.get("contact", "").strip()

        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user.id:
            flash("Email already used.", "danger")
            return redirect(url_for('profile'))

        user.name = new_name
        user.email = new_email
        user.contact = new_contact

        db.session.commit()
        session["user_name"] = user.name

        flash("Profile updated!", "success")
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)


# ============================================
# CHANGE PASSWORD
# ============================================
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if "user_id" not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        old = request.form['old_password']
        new = request.form['new_password']
        confirm = request.form['confirm_password']

        if not check_password_hash(user.password, old):
            flash("Incorrect current password.", "danger")
            return redirect(url_for('change_password'))

        if new != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('change_password'))

        user.password = generate_password_hash(new)
        db.session.commit()

        flash("Password changed!", "success")
        return redirect(url_for('profile'))

    return render_template('change_password.html')


# ============================================
# FORGOT PASSWORD
# ============================================
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Email not found.", "danger")
            return redirect(url_for('forgot_password'))

        token = secrets.token_hex(16)
        user.reset_token = token
        db.session.commit()

        flash("Use this token to reset your password.", "info")
        return redirect(url_for('reset_password', token=token))

    return render_template('forgot_password.html')


# ============================================
# RESET PASSWORD WITH TOKEN
# ============================================
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        new = request.form['password']
        confirm = request.form['confirm_password']

        if new != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('reset_password', token=token))

        user.password = generate_password_hash(new)
        user.reset_token = None
        db.session.commit()

        flash("Password reset successful!", "success")
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


# ============================================
# RUN APP (LAN / PyCharm ready)
# ============================================
if __name__ == '__main__':
    # host=0.0.0.0 allows access from LAN
    # debug=True shows errors for development
    app.run(host='0.0.0.0', port=5000, debug=True)
