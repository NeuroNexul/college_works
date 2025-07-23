# /backend/db/models.py

from datetime import datetime
from flask import current_app
from .db import db  # Import the 'db' instance from db.py


class User(db.Model):
    """
    User model for storing user details and credentials.
    Includes both regular users and the admin.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # Using 'email' as the username, as shown in the wireframe login form
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    pin_code = db.Column(db.String(10), nullable=True)
    # Enum ensures the role can only be 'user' or 'admin'
    role = db.Column(db.Enum('user', 'admin', name='role_enum'),
                     nullable=False, default='user')

    # Relationship to Bookings
    # cascade="all, delete-orphan" means if a user is deleted, their bookings are also deleted.
    bookings = db.relationship(
        'Booking', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashes the password and stores it."""
        # We use current_app to access the bcrypt instance configured in app.py
        bcrypt = current_app.config['BCRYPT']
        self.password_hash = bcrypt.generate_password_hash(
            password).decode('utf-8')

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        bcrypt = current_app.config['BCRYPT']
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class ParkingLot(db.Model):
    """
    ParkingLot model represents a physical parking facility.
    """
    __tablename__ = 'parking_lots'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    price_per_hour = db.Column(db.Float, nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)

    # Relationship to ParkingSpots
    # Deleting a lot will delete all its associated spots.
    spots = db.relationship('ParkingSpot', backref='lot',
                            lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ParkingLot {self.name}>'


class ParkingSpot(db.Model):
    """
    ParkingSpot model represents an individual spot within a ParkingLot.
    """
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey(
        'parking_lots.id'), nullable=False)
    # Enum for status ensures data consistency.
    status = db.Column(db.Enum('Available', 'Occupied',
                       name='spot_status_enum'), nullable=False, default='Available')

    # Relationship to Bookings
    # bookings = db.relationship('Booking', backref='spot', lazy=True)

    def __repr__(self):
        return f'<ParkingSpot {self.id} (Lot {self.lot_id}) - {self.status}>'


class Booking(db.Model):
    """
    Booking model represents a reservation of a parking spot by a user.
    This corresponds to the "Reserve parking spot" terminology.
    """
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    spot_id = db.Column(db.Integer, nullable=False)

    vehicle_number = db.Column(db.String(20), nullable=False)
    booking_time = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    # Set when user physically parks
    parking_time = db.Column(db.DateTime, nullable=True)
    release_time = db.Column(db.DateTime, nullable=True)  # Null until released
    # Null until calculated at release
    total_cost = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Booking {self.id} by User {self.user_id} for Spot {self.spot_id}>'
