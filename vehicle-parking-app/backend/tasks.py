from celery import shared_task
from datetime import datetime, timedelta
from db.models import User, Booking, ParkingLot, ParkingSpot
from db.db import db
import csv
import io  # Used to generate CSV in-memory
import os


email_file_path = os.getenv('EMAIL_FILE_PATH', 'emails.txt')

# This is a placeholder for a real email sending function


def send_email(to, subject, body):
    str = f"""
{"="*50}
SIMULATING EMAIL SEND
TO: {to}
SUBJECT: {subject}
BODY:
    {body.strip().replace('\n', '\n' + ' ' * 4)}
{"="*50}
"""

    with open(email_file_path, 'a') as f:
        f.write(str + "\n\n")


@shared_task(ignore_result=True)
def send_daily_reminders():
    """
    Finds users who haven't parked in the last 3 days and sends a reminder.
    """
    print(f"[{datetime.utcnow()}] Running daily reminder task...")
    three_days_ago = datetime.utcnow() - timedelta(days=3)

    # Find users who have NOT made a booking in the last 3 days

    # A simpler approach for this project: Find all users.
    all_users = User.query.filter_by(role='user').all()
    for user in all_users:
        last_booking = Booking.query.filter_by(user_id=user.id).order_by(
            Booking.booking_time.desc()).first()
        if not last_booking or last_booking.booking_time < three_days_ago:
            subject = "We Miss You at Vehicle Parking System!"
            body = f"Hi {user.full_name or user.email},\n\nIt's been a while! Don't forget to book your spot with us for a hassle-free parking experience.\n\nBest,\nThe VPS Team"
            send_email(user.email, subject, body)
            print(f"Sent reminder to {user.email}")
    return "Daily reminders sent."


@shared_task(ignore_result=True)
def send_monthly_reports():
    """
    Generates and sends a monthly activity report to each user.
    """
    print(f"[{datetime.utcnow()}] Running monthly report task...")
    all_users = User.query.filter_by(role='user').all()

    # Logic to define the previous month would go here
    # For demonstration, we'll just generate a dummy report
    for user in all_users:
        subject = f"Your Parking Summary for " + \
            f"{(datetime.utcnow() - timedelta(days=30)).strftime('%B %Y')}"

        # Fetch user-specific data
        total_sessions = Booking.query.filter_by(user_id=user.id).filter(
            Booking.booking_time >= datetime.utcnow() - timedelta(days=30)).count()
        total_spent = Booking.query.filter_by(user_id=user.id).filter(
            Booking.booking_time >= datetime.utcnow() - timedelta(days=30)
        ).with_entities(
            db.func.sum(Booking.total_cost)).scalar() or 0.0

        body = f"Hi {user.full_name or user.email},\n\nHere's your monthly parking report:\n- Total Sessions: {total_sessions}\n- Total Spent: ${total_spent}\n\nThanks for parking with us!\n"
        send_email(user.email, subject, body)
        print(f"Sent monthly report to {user.email}")
    return "Monthly reports sent."


# Set to False so we can track its status if needed
@shared_task(ignore_result=False)
def export_user_bookings_to_csv(user_id: int):
    """
    Fetches all bookings for a user, generates a CSV, and 'emails' it.
    """
    print(f"Starting CSV export for user_id: {user_id}")
    user = User.query.get(user_id)
    if not user:
        return f"User with ID {user_id} not found."

    bookings = Booking.query.filter_by(user_id=user_id).order_by(
        Booking.booking_time.desc()).all()

    if not bookings:
        body = "You have no booking history to export."
        send_email(user.email, "Your Booking Export", body)
        return "No bookings to export."

    # Use io.StringIO to create a CSV file in memory without writing to disk
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    header = ['Booking ID', 'Vehicle Number', 'Lot Name',
              'Booking Time', 'Parking Time', 'Release Time', 'Total Cost ($)']
    writer.writerow(header)

    # Write data rows
    for booking in bookings:
        # We need to manually fetch the lot name for each booking
        spot = ParkingSpot.query.get(booking.spot_id)
        lot_name = ParkingLot.query.get(
            spot.lot_id).name if spot else "Unknown Lot"

        writer.writerow([
            booking.id,
            booking.vehicle_number,
            lot_name,
            booking.booking_time,
            booking.parking_time,
            booking.release_time,
            booking.total_cost
        ])

    csv_data = output.getvalue()
    subject = "Your Parking History Export is Ready"
    body = f"Hi {user.full_name or user.email},\n\nPlease find your booking history attached.\n\nCSV Data:\n\n{csv_data}"

    send_email(user.email, subject, body)
    print(f"CSV data generated and sent for user {user.email}")
    return "Export successful."
