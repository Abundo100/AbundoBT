# models.py — FIXED VERSION with user_id foreign key

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'   # keep same name so your DB + SQL PRAGMA works

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), default='user')

    contact = db.Column(db.String(50), nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)

    # Relationship for convenience
    bookings = db.relationship("Booking", backref="user", lazy=True)

class Trip(db.Model):
    __tablename__ = "trip"

    id = db.Column(db.Integer, primary_key=True)
    route = db.Column(db.String(200), nullable=False)
    departure = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    seats_total = db.Column(db.Integer, nullable=False)
    seats_left = db.Column(db.Integer, nullable=False)

    bookings = db.relationship("Booking", backref="trip", lazy=True)


class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)

    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # ← ADDED THIS!

    passenger_name = db.Column(db.String(150), nullable=False)
    passenger_contact = db.Column(db.String(150), nullable=False)

    seats_booked = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)