from flask import Blueprint, request, jsonify
from utils.decorators import admin_required
from db.db import db
from db.models import ParkingLot, ParkingSpot, Booking, User
from sqlalchemy import func, desc, or_
from datetime import datetime, timedelta


bp = Blueprint('admin', __name__, url_prefix='/admin')


# =================================================================
# GET ALL REGISTERED USERS (ENHANCED)
# =================================================================
@bp.route("/users", methods=["GET"])
@admin_required()
def get_all_users():
    """
    Fetches a list of all non-admin users with aggregated booking statistics.
    """
    try:
        # EFFICIENT AGGREGATION QUERY
        # This subquery calculates the total amount spent and counts for each user.
        booking_stats = db.session.query(
            Booking.user_id,
            func.count(Booking.id).label('total_bookings'),
            # Coalesce handles users who have never spent money (SUM would be NULL)
            func.coalesce(func.sum(Booking.total_cost),
                          0).label('total_spent'),
            # Count active bookings (not yet released)
            func.count(Booking.id).filter(
                Booking.release_time == None).label('active_bookings')
        ).group_by(Booking.user_id).subquery()

        # MAIN QUERY
        # We LEFT JOIN the users table with our statistics subquery.
        # This ensures all users are returned, even those with no bookings.
        users_with_stats = db.session.query(
            User,
            # Coalesce ensures we get 0 instead of None for users with no booking stats
            func.coalesce(booking_stats.c.total_bookings, 0),
            func.coalesce(booking_stats.c.active_bookings, 0),
            func.coalesce(booking_stats.c.total_spent, 0)
        ).outerjoin(
            booking_stats, User.id == booking_stats.c.user_id
        ).filter(
            User.role == 'user'
        ).order_by(User.id).all()

        results = []
        for user, total_bookings, active_bookings, total_spent in users_with_stats:
            results.append({
                "id": user.id,
                "email": user.email,
                "fullName": user.full_name,
                "address": user.address,
                "pinCode": user.pin_code,

                "totalBookings": total_bookings,
                "activeBookings": active_bookings,
                "totalSpent": float(total_spent)  # Ensure it's a float
            })

        return jsonify(results), 200

    except Exception as e:
        print(f"Error fetching registered users with stats: {e}")
        return jsonify({"message": "An error occurred while fetching users."}), 500


# =================================================================
# FETCH ALL PARKING LOTS - (Read)
# =================================================================
@bp.route("/lots", methods=["GET"])
@admin_required()
def get_all_lots():
    """
    Fetches all parking lots with detailed spot information.
    This is designed to provide all data needed for the dashboard view in one call.
    """
    try:
        lots = ParkingLot.query.order_by(ParkingLot.id).all()
        results = []
        for lot in lots:
            occupied_count = ParkingSpot.query.filter_by(
                lot_id=lot.id, status='Occupied').count()

            # Fetch limited spot details for the grid view
            spots_data = [{
                'id': spot.id,
                'lot_id': spot.lot_id,
                'status': spot.status
            } for spot in lot.spots]

            results.append({
                'id': lot.id,
                'name': lot.name,
                'address': lot.address,
                'pin_code': lot.pin_code,
                'price_per_hour': lot.price_per_hour,
                'total_spots': lot.total_spots,
                'occupied_spots_count': occupied_count,
                'spots': spots_data
            })
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"message": "An error occurred fetching lots.", "error": str(e)}), 500


# =================================================================
# ADD A NEW PARKING LOT - (Create)
# =================================================================
@bp.route("/lots", methods=["POST"])
@admin_required()
def add_parking_lot():
    """
    Creates a new parking lot and automatically generates its parking spots.
    """
    data = request.get_json()

    # Validation
    required_fields = ['name', 'address',
                       'pin_code', 'price_per_hour', 'total_spots']
    if not all(field in data for field in required_fields):
        return jsonify({"message": "Missing required fields"}), 400

    if not isinstance(data['total_spots'], int) or data['total_spots'] <= 0:
        return jsonify({"message": "Total spots must be a positive integer"}), 400

    # Database Transaction
    try:
        # 1. Create the ParkingLot
        new_lot = ParkingLot(
            name=data['name'],
            address=data['address'],
            pin_code=data['pin_code'],
            price_per_hour=data['price_per_hour'],
            total_spots=data['total_spots']
        )
        db.session.add(new_lot)

        # We need the new_lot.id for the spots, so we flush the session.
        # This sends the INSERT to the DB and assigns an ID without committing the transaction.
        db.session.flush()

        # 2. Create the associated ParkingSpots
        spots_to_add = [
            ParkingSpot(lot_id=new_lot.id, status='Available')
            for _ in range(data['total_spots'])
        ]
        # More efficient than adding one by one
        db.session.bulk_save_objects(spots_to_add)

        db.session.commit()
        return jsonify({"message": "Parking lot created successfully", "lot_id": new_lot.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to create parking lot.", "error": str(e)}), 500


# =================================================================
# EDIT AN EXISTING PARKING LOT - (Update)
# =================================================================
@bp.route("/lots/<int:lot_id>", methods=["PUT"])
@admin_required()
def edit_parking_lot(lot_id):
    """
    Updates the details of a specific parking lot.
    The number of spots cannot be changed.
    """
    lot = ParkingLot.query.get_or_404(lot_id)
    data = request.get_json()

    # Update fields if they exist in the request data
    lot.name = data.get('name', lot.name)
    lot.address = data.get('address', lot.address)
    lot.pin_code = data.get('pin_code', lot.pin_code)
    lot.price_per_hour = data.get('price_per_hour', lot.price_per_hour)

    # Note: We deliberately ignore `total_spots` as per requirements.

    try:
        db.session.commit()
        # Return the updated object
        return jsonify({
            'id': lot.id,
            'name': lot.name,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'price_per_hour': lot.price_per_hour,
            'total_spots': lot.total_spots,
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to update parking lot.", "error": str(e)}), 500


# =================================================================
# DELETE A PARKING LOT - (Delete)
# =================================================================

@bp.route("/lots/<int:lot_id>", methods=["DELETE"])
@admin_required()
def delete_parking_lot(lot_id):
    """
    Deletes a parking lot only if all of its spots are available.
    """
    lot = ParkingLot.query.get_or_404(lot_id)

    # Validation: Check if any spots are occupied
    occupied_spot = ParkingSpot.query.filter_by(
        lot_id=lot.id, status='Occupied').first()
    if occupied_spot:
        return jsonify({"message": "Cannot delete lot: one or more spots are currently occupied."}), 400

    try:
        # The `cascade="all, delete-orphan"` on the model relationship
        # will automatically delete all associated ParkingSpot records.
        db.session.delete(lot)
        db.session.commit()
        return jsonify({"message": f"Parking lot '{lot.name}' and its {lot.total_spots} spots were deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Failed to delete parking lot.", "error": str(e)}), 500


# =================================================================
# GET ADMIN SUMMARY DASHBOARD DATA
# =================================================================
@bp.route("/summary", methods=["GET"])
@admin_required()
def get_admin_summary():

    # 1. KPI Cards Data
    total_lots = db.session.query(func.count(ParkingLot.id)).scalar()
    total_users = db.session.query(func.count(User.id)).filter(
        User.role == 'user').scalar()

    spots_stats = db.session.query(
        func.count(ParkingSpot.id).label('total_spots'),
        func.count(ParkingSpot.id).filter(ParkingSpot.status.in_(
            ['Occupied', 'Reserved'])).label('active_spots')
    ).one()

    total_revenue = db.session.query(func.coalesce(
        func.sum(Booking.total_cost), 0)).scalar()

    # 2. Revenue Over Time (Last 30 Days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_revenue = Booking.query.filter(Booking.release_time >= thirty_days_ago)\
        .with_entities(
            func.strftime('%Y-%m-%d', Booking.release_time).label('day'),
            func.sum(Booking.total_cost).label('total')
    ).group_by('day').order_by('day').all()

    # 3. Top 5 Most Active Lots (by recent bookings)
    top_lots = db.session.query(
        ParkingLot,
        func.count(Booking.id).label('booking_count')
    ).join(ParkingSpot, ParkingLot.id == ParkingSpot.lot_id)\
        .join(Booking, ParkingSpot.id == Booking.spot_id)\
        .filter(Booking.booking_time >= thirty_days_ago)\
        .group_by(ParkingLot.id)\
        .order_by(desc('booking_count'))\
        .limit(5).all()

    top_lots_data = [{
        'id': lot.id,
        'name': lot.name,
        'booking_count': count
    } for lot, count in top_lots]

    # 4. Occupancy by Lot
    occupancy_data = db.session.query(
        ParkingLot.name,
        func.count(ParkingSpot.id).filter(ParkingSpot.status.in_(
            ['Occupied', 'Reserved'])).label('occupied'),
        func.count(ParkingSpot.id).filter(
            ParkingSpot.status == 'Available').label('available')
    ).join(ParkingSpot, ParkingLot.id == ParkingSpot.lot_id)\
        .group_by(ParkingLot.name).all()

    # Assemble final JSON payload
    summary_data = {
        "kpis": {
            "totalLots": total_lots,
            "totalUsers": total_users,
            "totalSpots": spots_stats.total_spots,
            "liveOccupancyPercent": (spots_stats.active_spots / spots_stats.total_spots * 100) if spots_stats.total_spots > 0 else 0,
            "totalRevenue": float(total_revenue)
        },
        "dailyRevenue": [{"day": r.day, "total": float(r.total)} for r in daily_revenue],
        "topLots": top_lots_data,
        "occupancyByLot": [{"name": lot.name, "occupied": lot.occupied, "available": lot.available} for lot in occupancy_data]
    }

    return jsonify(summary_data)


# =================================================================
# UNIFIED ADMIN SEARCH
# =================================================================
@bp.route("/search", methods=["GET"])
@admin_required()
def admin_search():
    """
    A unified search endpoint for admins.
    Accepts two query parameters:
    - 'type': one of ['lot', 'user', 'vehicle']
    - 'q': the search query string
    """
    search_type = request.args.get('type', 'lot')
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify([])  # Return empty list if query is empty

    results = []

    try:
        if search_type == 'lot':
            # Search lots by name, address, or pincode
            lots = ParkingLot.query.filter(
                or_(
                    ParkingLot.name.ilike(f"%{query}%"),
                    ParkingLot.address.ilike(f"%{query}%"),
                    ParkingLot.pin_code.ilike(f"%{query}%")
                )
            ).all()
            # We will reuse the same data structure as the main Admin Dashboard
            for lot in lots:
                occupied_count = ParkingSpot.query.filter_by(
                    lot_id=lot.id, status='Occupied').count()
                spots_data = [{'id': spot.id, 'status': spot.status}
                              for spot in lot.spots]
                results.append({
                    'id': lot.id, 'name': lot.name, 'total_spots': lot.total_spots,
                    'occupied_spots_count': occupied_count, 'spots': spots_data, 'address': lot.address,
                    # Add other fields needed by ParkingLotCard
                })

        elif search_type == 'user':
            # Search users by name or email
            users = User.query.filter(
                or_(
                    User.full_name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%")
                ),
                User.role == 'user'  # Exclude admin
            ).all()
            # We can reuse the same data structure as the Admin Users page
            for user in users:
                results.append({
                    "id": user.id, "email": user.email, "fullName": user.full_name,
                    "address": user.address, "pinCode": user.pin_code
                })

        elif search_type == 'vehicle':
            # Search for active bookings by vehicle number
            bookings = Booking.query.filter(
                Booking.vehicle_number.ilike(f"%{query}%"),
                Booking.release_time.is_(None)  # Only search active bookings
            ).all()
            # For each booking, we find its lot and format it like a lot result
            for booking in bookings:
                lot = booking.spot.lot
                occupied_count = ParkingSpot.query.filter_by(
                    lot_id=lot.id, status='Occupied').count()
                spots_data = [{'id': spot.id, 'status': spot.status}
                              for spot in lot.spots]
                # Add extra info to identify the specific vehicle
                lot_result = {
                    'id': lot.id, 'name': lot.name, 'total_spots': lot.total_spots,
                    'address': lot.address, 'pin_code': lot.pin_code,
                    'occupied_spots_count': occupied_count, 'spots': spots_data,
                    'searched_vehicle': {  # Add context about the vehicle search
                        'vehicle_number': booking.vehicle_number,
                        'spot_id': booking.spot_id
                    }
                }
                # Avoid adding duplicate lots if multiple searched vehicles are in the same lot
                if not any(r['id'] == lot.id for r in results):
                    results.append(lot_result)

        return jsonify(results), 200

    except Exception as e:
        print(f"Admin Search Error: {e}")
        return jsonify({"message": "An error occurred during search."}), 500
