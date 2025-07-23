import random
from datetime import datetime, timedelta
from faker import Faker
from app import app, db  # Import your Flask app instance and db object
from db.models import User, ParkingLot, ParkingSpot, Booking
from routes.auth import create_admin_user
import math
import os

# Initialize Faker for generating mock data
fake = Faker()

# Configuration
NUM_USERS = 25
NUM_LOTS = 10
MAX_NUM_PAST_BOOKINGS_PER_USER = 10


logged_str = ""
prev_group = None
seperator = "=" * 25


def log(message, group, only_log=False):
    """Utility function to log messages in terminal And store them in a global string."""
    global logged_str, prev_group

    if group == prev_group:
        logged_str += "\n" + message
    else:
        logged_str += f"\n\n{seperator} {group} {seperator}\n" + message
        prev_group = group

    if not only_log:
        print(message)  # Print to console for immediate feedback


def generate_random_time(start_date, end_date):
    """Generates a random datetime between two datetimes."""
    time_diff = end_date - start_date
    random_seconds = random.randint(0, int(time_diff.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)


def seed_data():
    """Main function to seed the database."""
    # The 'with app.app_context()' is crucial. It makes the Flask application
    # context available, so we can access extensions like SQLAlchemy (db).
    with app.app_context():
        log("Deleting old data...", "Database Cleanup")
        # A more robust way to delete in order, respecting foreign key constraints
        Booking.query.delete()
        ParkingSpot.query.delete()
        ParkingLot.query.delete()
        User.query.delete()
        db.session.commit()
        log("Old data deleted.", "Database Cleanup")

        # 1. Create Users
        log(f"Creating {NUM_USERS} users...", "User Creation")
        create_admin_user()  # Ensure admin user is created first

        users = []
        for _ in range(NUM_USERS):
            user = User(
                email=fake.unique.email(),
                full_name=fake.name(),
                address=fake.street_address(),
                pin_code=fake.postcode()
            )
            # Set a common password for all test users
            user.set_password('password123')
            users.append(user)

            # Log the creation of each user
            log(f"Created user: {user.email} | {user.full_name}",
                "User Creation", only_log=True)

        db.session.bulk_save_objects(users)
        db.session.commit()

        # We need the user IDs, so we re-query them after committing
        users = User.query.filter(User.role == 'user').all()
        log("Users created.", "User Creation")

        # 2. Create Parking Lots and Spots
        log(f"Creating {NUM_LOTS} parking lots...", "Parking Lot Creation")
        lots = []
        for i in range(NUM_LOTS):
            lot = ParkingLot(
                name=f"{fake.street_name()} Garage",
                address=fake.address(),
                pin_code=fake.postcode(),
                price_per_hour=round(random.uniform(1.5, 6.0), 2),
                total_spots=random.randint(20, 100)
            )
            lots.append(lot)

            log(f"Created lot: {lot.name} | {lot.address} | {lot.total_spots} spots",
                "Parking Lot Creation", only_log=True)

        db.session.bulk_save_objects(lots)
        db.session.commit()

        log("Parking lots created.", "Parking Lot Creation")

        # Re-query lots to get their IDs
        lots = ParkingLot.query.all()

        # Create spots for each lot
        log(f"Creating {sum(l.total_spots for l in lots)} parking spots...",
            "Parking Spot Creation")
        all_spots = []
        for lot in lots:
            for _ in range(lot.total_spots):
                all_spots.append(ParkingSpot(lot_id=lot.id))
        db.session.bulk_save_objects(all_spots)
        db.session.commit()
        log("Parking spots created.", "Parking Spot Creation")

        # Re-query all spots to get their IDs
        all_spots = ParkingSpot.query.all()

        # 3. Create Past Bookings
        log("Creating past bookings...", "Booking Creation")
        past_bookings = []
        now = datetime.utcnow()
        for user in users:
            NUM_PAST_BOOKINGS_PER_USER = random.randint(
                1, MAX_NUM_PAST_BOOKINGS_PER_USER)
            for _ in range(NUM_PAST_BOOKINGS_PER_USER):
                # Ensure the spot is available before creating a booking for it
                available_spots = [
                    s for s in all_spots if s.status == 'Available']
                if not available_spots:
                    continue  # Skip if no spots are left

                spot = random.choice(available_spots)
                spot.status = 'Occupied'  # Temporarily mark as occupied

                # Create realistic, time-relative past dates
                end_time = generate_random_time(
                    now - timedelta(days=90), now - timedelta(hours=1))
                start_time = end_time - timedelta(hours=random.randint(1, 10))

                duration_hours = math.ceil(
                    (end_time - start_time).total_seconds() / 3600)
                cost = duration_hours * spot.lot.price_per_hour

                past_bookings.append(Booking(
                    user_id=user.id,
                    spot_id=spot.id,
                    vehicle_number=f"{fake.license_plate()[:8]}",
                    # Booking before parking
                    booking_time=start_time -
                    timedelta(minutes=random.randint(5, 30)),
                    parking_time=start_time,
                    release_time=end_time,
                    total_cost=round(cost, 2)
                ))

                log(f"Created past booking for user {user.email} | Spot {spot.id} | Duration: {duration_hours} hours | Cost: ${cost:.2f}",
                    "Booking Creation", only_log=True)

                # Immediately mark the spot as available again for the next iteration
                spot.status = 'Available'

        db.session.bulk_save_objects(past_bookings)
        db.session.commit()
        log("Past bookings created.", "Booking Creation")

        # 4. Create Current (Reserved and Occupied) Bookings
        log("Creating current reserved and occupied bookings...", "Booking Creation")

        available_spots = [s for s in all_spots if s.status == 'Available']
        # Shuffle to randomize which spots get picked
        random.shuffle(available_spots)

        # Keep 30% spots available for future bookings
        if len(available_spots) > 10:
            available_spots = available_spots[:int(len(available_spots) * 0.7)]

        # 20% of remaining spots will be occupied
        num_occupied = int(len(available_spots) * 0.20)
        num_reserved = int(len(available_spots) * 0.10)  # 10% will be reserved

        # Create Occupied Bookings
        for i in range(num_occupied):
            if not available_spots:
                break
            spot = available_spots.pop()
            user = random.choice(users)

            spot.status = 'Occupied'
            parking_time = now - \
                timedelta(hours=random.randint(0, 5),
                          minutes=random.randint(0, 59))

            db.session.add(Booking(
                user_id=user.id,
                spot_id=spot.id,
                vehicle_number=f"{fake.license_plate()[:8]}",
                booking_time=parking_time -
                timedelta(minutes=random.randint(5, 30)),
                parking_time=parking_time
            ))

            log(f"Created occupied booking for user {user.email} | Spot {spot.id} | Parking Time: {parking_time}",
                "Booking Creation", only_log=True)

        # Create Reserved Bookings
        for i in range(num_reserved):
            if not available_spots:
                break
            spot = available_spots.pop()
            user = random.choice(users)

            spot.status = 'Occupied'
            booking_time = now - timedelta(minutes=random.randint(0, 59))

            db.session.add(Booking(
                user_id=user.id,
                spot_id=spot.id,
                vehicle_number=f"{fake.license_plate()[:8]}",
                booking_time=booking_time
            ))

            log(f"Created reserved booking for user {user.email} | Spot {spot.id} | Booking Time: {booking_time}",
                "Booking Creation", only_log=True)

        db.session.commit()
        log("Current bookings created.", "Booking Creation")
        log("\nDatabase seeding complete!", "Completion")


if __name__ == '__main__':
    seed_data()

    # Save the log to a file
    log_file_path = os.path.join(
        os.path.abspath(os.getcwd()), 'db', 'seed_log.txt')
    with open(log_file_path, 'w') as log_file:
        log_file.write(logged_str)
        log(f"Log saved to {log_file_path}", "Completion")
