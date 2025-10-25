# models.py — Database Models (50% Complete Version)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ======================
# USER MODEL
# ======================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), default='user')  # 'user' or 'admin'

    def __repr__(self):
        return f'<User {self.name}>'


# ======================
# TRIP MODEL
# ======================
class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(100), nullable=False)
    departure = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    seats_total = db.Column(db.Integer, nullable=False)
    seats_left = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Trip {self.route}>'


# ======================
# BOOKING MODEL
# ======================
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    passenger_name = db.Column(db.String(100), nullable=False)
    passenger_contact = db.Column(db.String(100), nullable=False)
    seats_booked = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trip = db.relationship('Trip', backref=db.backref('bookings', lazy=True))
