# app.py — Bus Ticketing System (50% Complete Version with Login & Admin)
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Trip, Booking, User

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devkey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bus_booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create database on first run
with app.app_context():
    db.create_all()

# =====================
# HOME
# =====================
@app.route('/')
def index():
    trips = Trip.query.order_by(Trip.id).all()
    return render_template('index.html', trips=trips)


# =====================
# REGISTER
# =====================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        user = User(name=name, email=email, password=hashed_pw, role=role)
        db.session.add(user)
        db.session.commit()

        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# =====================
# LOGIN
# =====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['role'] = user.role
            flash(f'Welcome, {user.name}!', 'success')

            if user.role == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')


# =====================
# LOGOUT
# =====================
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


# =====================
# BOOK TRIP
# =====================
@app.route('/book/<int:trip_id>', methods=['GET', 'POST'])
def book(trip_id):
    if 'user_id' not in session:
        flash('Please log in first to book a trip.', 'warning')
        return redirect(url_for('login'))

    trip = Trip.query.get_or_404(trip_id)

    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        seats = int(request.form['seats'])

        if seats <= 0 or seats > trip.seats_left:
            flash('Invalid number of seats selected.', 'danger')
            return redirect(url_for('book', trip_id=trip_id))

        booking = Booking(trip_id=trip.id, passenger_name=name,
                          passenger_contact=contact, seats_booked=seats)
        trip.seats_left -= seats
        db.session.add(booking)
        db.session.commit()

        flash(f'Booking confirmed for {name}!', 'success')
        return redirect(url_for('bookings'))

    return render_template('book.html', trip=trip)


# =====================
# VIEW BOOKINGS
# =====================
@app.route('/bookings')
def bookings():
    if 'user_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    all_bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('bookings.html', bookings=all_bookings)


# =====================
# ADMIN DASHBOARD
# =====================
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.get('role') != 'admin':
        flash('Admins only.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            route = request.form['route']
            departure = request.form['departure']
            price = float(request.form['price'])
            seats = int(request.form['seats'])

            trip = Trip(route=route, departure=departure,
                        price=price, seats_total=seats, seats_left=seats)
            db.session.add(trip)
            db.session.commit()
            flash('Trip added successfully!', 'success')

        elif action == 'delete':
            trip_id = int(request.form['trip_id'])
            trip = Trip.query.get(trip_id)
            if trip:
                db.session.delete(trip)
                db.session.commit()
                flash('Trip deleted successfully.', 'info')

        return redirect(url_for('admin'))

    trips = Trip.query.order_by(Trip.id).all()
    return render_template('admin.html', trips=trips)


if __name__ == '__main__':
    app.run(debug=True)
