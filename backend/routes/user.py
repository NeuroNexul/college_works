from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from db.models import ParkingLot, ParkingSpot, Booking, User
from db.db import db
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, desc
from utils.decorators import cache
from tasks import export_user_bookings_to_csv

bp = Blueprint("user", __name__)


@bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """
    Fetches the profile and aggregated stats for the currently logged-in user.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get_or_404(user_id)

        # Aggregate stats for this specific user
        stats = db.session.query(
            func.count(Booking.id).label('total_bookings'),
            func.coalesce(func.sum(Booking.total_cost),
                          0).label('total_spent'),
            func.count(Booking.id).filter(
                Booking.release_time == None).label('active_bookings')
        ).filter_by(user_id=user_id).one()

        profile_data = {
            "id": user.id,
            "email": user.email,
            "fullName": user.full_name,
            "role": user.role,
            "address": user.address,
            "pinCode": user.pin_code,
            "totalBookings": stats.total_bookings,
            "activeBookings": stats.active_bookings,
            "totalSpent": float(stats.total_spent)
        }
        return jsonify(profile_data), 200

    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return jsonify({"message": "An error occurred fetching profile."}), 500


@bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Allows the logged-in user to update their own profile information.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get_or_404(user_id)
        data = request.get_json()

        if not data:
            return jsonify({"message": "No data provided"}), 400

        # Update fields if they are present and not empty strings
        if 'fullName' in data and isinstance(data['fullName'], str):
            user.full_name = data['fullName'].strip()

        if 'address' in data and isinstance(data['address'], str):
            user.address = data['address'].strip()

        if 'pinCode' in data and isinstance(data['pinCode'], str):
            user.pin_code = data['pinCode'].strip()

        db.session.commit()

        # Return the updated profile data as confirmation
        return get_profile()

    except Exception as e:
        db.session.rollback()
        print(f"Error updating user profile: {e}")
        return jsonify({"message": "An error occurred during update."}), 500


@bp.route("/lots", methods=["GET"])
@jwt_required()
@cache(minutes=5)
def get_all_lots_for_user():
    """
    Fetches a simplified list of all parking lots for the user dashboard.
    This route is optimized to not send the full spot list, only the counts
    needed for the user to make a decision.
    """
    try:
        # Order by name for a consistent default list on the frontend
        lots = ParkingLot.query.order_by(ParkingLot.name).all()
        results = []

        for lot in lots:
            # For each lot, we perform a quick count of its occupied spots.
            # While this is an N+1 query pattern, it's perfectly acceptable and readable
            # for the scale of this project. For thousands of lots, this could be
            # optimized with a single, more complex SQL query.
            occupied_count = ParkingSpot.query.filter_by(
                lot_id=lot.id, status='Occupied').count()

            results.append({
                'id': lot.id,
                'name': lot.name,
                'address': lot.address,
                'pin_code': lot.pin_code,
                'price_per_hour': lot.price_per_hour,
                'total_spots': lot.total_spots,
                'occupied_spots_count': occupied_count,
            })

        return jsonify(results), 200

    except Exception as e:
        # In a real app, you would log this error.
        print(f"Error fetching lots for user: {e}")
        return jsonify({"message": "An error occurred while fetching parking lots."}), 500


@bp.route("/bookings", methods=["GET"])
@jwt_required()
@cache(minutes=5)
def get_user_bookings():
    """
    Fetches all past and present bookings for the authenticated user.
    """
    try:
        user_id = int(get_jwt_identity())

        # 1. Get all bookings for the user
        user_bookings = Booking.query.filter_by(
            user_id=user_id).order_by(Booking.booking_time.desc()).all()
        if not user_bookings:
            return jsonify([]), 200

        # 2. Collect all unique spot and lot IDs needed
        spot_ids = {b.spot_id for b in user_bookings}
        spots = ParkingSpot.query.filter(ParkingSpot.id.in_(spot_ids)).all()
        lot_ids = {s.lot_id for s in spots}
        lots = ParkingLot.query.filter(ParkingLot.id.in_(lot_ids)).all()

        # 3. Create mapping dictionaries for fast lookups
        spots_map = {s.id: s for s in spots}
        lots_map = {l.id: l for l in lots}

        # Format the Results
        results = []
        for booking in user_bookings:
            spot = spots_map.get(booking.spot_id)
            if not spot:
                continue  # Should not happen, but a good safeguard

            lot = lots_map.get(spot.lot_id)
            if not lot:
                continue

            results.append({
                'id': booking.id,
                # Use .isoformat() to convert datetime objects to ISO 8601 strings
                'booking_time': booking.booking_time,
                'parking_time': booking.parking_time if booking.parking_time else None,
                'release_time': booking.release_time if booking.release_time else None,
                'total_cost': booking.total_cost,
                'vehicle_number': booking.vehicle_number,
                'spot': {
                    'id': spot.id,
                },
                'lot': {
                    'id': lot.id,
                    'name': lot.name,
                    'address': lot.address,
                }
            })

        return jsonify(results), 200

    except Exception as e:
        # In a real app, you would log this error.
        print(f"Error fetching user bookings: {e}")
        return jsonify({"message": "An error occurred while fetching your bookings.", "err": e}), 500


@bp.route("/booking/<int:spot_id>", methods=["GET"])
@jwt_required()
@cache(minutes=5)
def get_booking_details(spot_id):
    """
    Fetches detailed information about a specific booking for the authenticated user.
    """
    try:
        # Get the booking by spot_id
        booking = Booking.query.filter_by(spot_id=spot_id).first()

        spot = ParkingSpot.query.get(spot_id)

        if not booking or not spot:
            return jsonify({"message": "Booking not found."}), 404

        # Format the response
        response = {
            'id': booking.id,
            'user_id': booking.user_id,
            'booking_time': booking.booking_time,
            'parking_time': booking.parking_time,
            'release_time': booking.release_time,
            'total_cost': booking.total_cost,
            'vehicle_number': booking.vehicle_number,
            'user': {
                'id': booking.user.id,
                'full_name': booking.user.full_name,
                'email': booking.user.email,
                'address': booking.user.address
            },
            'spot': {
                'id': spot.id,
                'status': spot.status,
                'lot': {
                    'id': spot.lot.id,
                    'name': spot.lot.name,
                    'address': spot.lot.address,
                    'price_per_hour': spot.lot.price_per_hour,
                }
            }
        }

        return jsonify(response), 200
    except Exception as e:
        # In a real app, you would log this error.
        print(f"Error fetching booking details for spot {spot_id}: {e}")
        return jsonify({"message": "An error occurred while fetching booking details.", "err": f"{e}"}), 500


@bp.route("/reserve", methods=["POST"])
@jwt_required()
def reserve_spot():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    lot_id = data.get('lot_id')
    vehicle_number = data.get('vehicle_number')

    if not lot_id or not vehicle_number:
        return jsonify({"message": "Lot ID and vehicle number are required"}), 400

    # Find the first available spot in the chosen lot
    spot = ParkingSpot.query.filter_by(
        lot_id=lot_id, status='Available').first()
    if not spot:
        return jsonify({"message": "No available spots in this lot."}), 404

    try:
        spot.status = 'Occupied'
        new_booking = Booking(
            user_id=user_id, spot_id=spot.id, vehicle_number=vehicle_number)
        db.session.add(new_booking)
        db.session.commit()
        return jsonify({"message": "Spot reserved successfully!", "booking_id": new_booking.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to reserve spot.", "error": str(e)}), 500


@bp.route("/park/<int:booking_id>", methods=["POST"])
@jwt_required()
def park_car(booking_id):
    user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)
    spot = ParkingSpot.query.get_or_404(booking.spot_id)

    # Security check: ensure the booking belongs to the user
    if booking.user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    # Logic check: can only park if the spot is 'Reserved'
    if spot.status != 'Occupied' or booking.parking_time is not None:
        return jsonify({"message": "This booking is not in a reservable state."}), 400

    # Check if user has any other active parking session with the same vehicle
    active_bookings = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.vehicle_number == booking.vehicle_number,
        Booking.parking_time.isnot(None),
        Booking.release_time.is_(None)
    ).all()

    if active_bookings:
        return jsonify({"message": "You already have an active parking session."}), 400

    try:
        booking.parking_time = datetime.utcnow()
        spot.status = 'Occupied'
        db.session.commit()
        return jsonify({"message": "Parking session started."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to start parking session.", "error": str(e)}), 500


@bp.route("/release/<int:booking_id>", methods=["POST"])
@jwt_required()
def release_spot(booking_id):
    user_id = int(get_jwt_identity())
    booking = Booking.query.get_or_404(booking_id)
    spot = ParkingSpot.query.get_or_404(booking.spot_id)

    if booking.user_id != user_id:
        return jsonify({"message": "Unauthorized"}), 403

    # Logic check: Spot must be occupied and have a parking_time
    if spot.status != 'Occupied' or not booking.parking_time:
        return jsonify({"message": "This booking is not active."}), 400

    try:
        booking.release_time = datetime.utcnow()

        # Calculate duration based on parking_time
        duration_seconds = (booking.release_time -
                            booking.parking_time).total_seconds()
        # Round up to the next hour
        duration_hours = (duration_seconds / 3600)

        price_per_hour = spot.lot.price_per_hour
        booking.total_cost = duration_hours * price_per_hour

        spot.status = 'Available'
        db.session.commit()

        return jsonify({
            "message": "Parking session ended.",
            "total_cost": booking.total_cost,
            "duration_hours": duration_hours
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to end parking session.", "error": str(e)}), 500


@bp.route("/summary", methods=["GET"])
@jwt_required()
@cache(minutes=5)
def get_user_summary():
    try:
        user_id = int(get_jwt_identity())

        # Base query for all completed bookings by the user
        base_query = Booking.query.filter(
            Booking.user_id == user_id,
            Booking.release_time.isnot(None)
        )

        # 1. KPI Cards Data (No change needed here as it only uses Booking)
        kpi_stats = base_query.with_entities(
            func.count(Booking.id).label('total_sessions'),
            func.coalesce(func.sum(Booking.total_cost),
                          0).label('total_spent'),
            func.avg(Booking.total_cost).label('avg_cost_per_session')
        ).one_or_none()

        if kpi_stats is None:  # Handle case where user has no past bookings
            kpi_stats = {'total_sessions': 0,
                         'total_spent': 0, 'avg_cost_per_session': 0}

        # 2. Most Used Lot (Refactored with explicit joins)
        favorite_lot_query = base_query.join(
            ParkingSpot, Booking.spot_id == ParkingSpot.id
        ).join(
            ParkingLot, ParkingSpot.lot_id == ParkingLot.id
        ).with_entities(
            ParkingLot.name,
            func.count(Booking.id).label('visit_count')
        ).group_by(
            ParkingLot.name
        ).order_by(
            desc('visit_count')
        ).first()

        # 3. Spending Per Month (No change needed)
        six_months_ago = datetime.utcnow() - relativedelta(months=6)
        monthly_spending = base_query.filter(Booking.release_time >= six_months_ago)\
            .with_entities(
                func.strftime('%Y-%m', Booking.release_time).label('month'),
                func.sum(Booking.total_cost).label('total')
        ).group_by('month').order_by('month').all()

        # 4. Parking by Day of Week (No change needed)
        day_of_week_map = {0: 'Sun', 1: 'Mon', 2: 'Tue',
                           3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}
        day_of_week_stats = base_query\
            .with_entities(func.strftime('%w', Booking.release_time).label('dow'), func.count(Booking.id))\
            .group_by('dow').all()

        day_of_week_data = {day: 0 for day in day_of_week_map.values()}
        for dow, count in day_of_week_stats:
            day_name = day_of_week_map[int(dow)]
            day_of_week_data[day_name] = count

        # Assemble final JSON payload
        summary_data = {
            "kpis": {
                "totalSessions": kpi_stats.total_sessions,
                "totalSpent": float(kpi_stats.total_spent),
                "avgCost": float(kpi_stats.avg_cost_per_session or 0)
            },
            "favoriteLot": {
                "name": favorite_lot_query.name if favorite_lot_query else "N/A",
                "visits": favorite_lot_query.visit_count if favorite_lot_query else 0
            },
            "monthlySpending": [{"month": r.month, "total": float(r.total)} for r in monthly_spending],
            "dayOfWeekParking": day_of_week_data
        }

        return jsonify(summary_data)

    except Exception as e:
        print(f"Error fetching user summary: {e}")
        return jsonify({"message": "An error occurred while fetching your summary."}), 500


@bp.route("/export-bookings", methods=["POST"])
@jwt_required()
def trigger_export():
    """
    API endpoint for the user to trigger their CSV export job.
    """
    user_id = int(get_jwt_identity())

    # Use .delay() to execute the task asynchronously via Celery
    export_user_bookings_to_csv.delay(user_id)

    # Return an immediate response to the user
    return jsonify({"message": "Your booking export has started. You will receive an email shortly with your data."}), 202
