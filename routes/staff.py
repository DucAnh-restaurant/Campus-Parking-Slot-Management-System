import time

from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify
from models import db
from models.reservation import Reservation
from models.user import User
from models.vehicle import Vehicle
from models.parking_slot import ParkingSlot
from utils.decorators import staff_required
from extensions import limiter   # Rate limiter

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')


@staff_bp.route('/dashboard')
@staff_required
def dashboard():
    """Staff monitoring dashboard – read-only."""
    active_reservations = db.session.query(
        Reservation, User, Vehicle, ParkingSlot
    ).join(User, Reservation.user_id == User.user_id
    ).join(Vehicle, Reservation.vehicle_id == Vehicle.vehicle_id
    ).join(ParkingSlot, Reservation.slot_id == ParkingSlot.slot_id
    ).filter(Reservation.is_active == True
    ).order_by(Reservation.created_at.desc()).all()

    return render_template('dashboard/staff.html', reservations=active_reservations)


@staff_bp.route('/api/search')
@staff_required
def search_vehicle():
    """Search reservations by vehicle number."""
    query = request.args.get('q', '').strip().upper()
    if not query:
        return jsonify([])

    results = db.session.query(
        Reservation, User, Vehicle, ParkingSlot
    ).join(User, Reservation.user_id == User.user_id
    ).join(Vehicle, Reservation.vehicle_id == Vehicle.vehicle_id
    ).join(ParkingSlot, Reservation.slot_id == ParkingSlot.slot_id
    ).filter(
        Vehicle.vehicle_number.ilike(f'%{query}%'),
        Reservation.is_active == True
    ).all()

    return jsonify([{
        'reservation_id': r.reservation_id,
        'user_name': u.user_name,
        'email': u.email,
        'vehicle_number': v.vehicle_number,
        'vehicle_type': v.vehicle_type,
        'slot_location': s.slot_location,
        'reservation_date': r.reservation_date.isoformat(),
        'reservation_time': str(r.reservation_time),
    } for r, u, v, s in results])

# ==================== VULNERABLE ENDPOINT CHO CTF ====================
@staff_bp.route('/api/advanced-search', methods=['GET'])
@staff_required
@limiter.limit("8 per minute")          # Rate limit chặt để chống AI spam
def advanced_search():
    """Advanced Vehicle Search - BLIND SQLi (Dành cho CTF)"""
    q = request.args.get('q', '').strip()
    
    if not q or len(q) > 60:
        return jsonify({"results": [], "note": "Query too long or empty"})

    # === LIGHT WAF (làm khó AI/Claude tự động) ===
    blocked_keywords = [
        'information_schema', 'sleep(', 'benchmark', 'union select', 
        'db_name', 'user()', 'version()', 'schema()', 'extractvalue', 
        'updatexml', 'load_file'
    ]
    
    lowered = q.lower()
    if any(word in lowered for word in blocked_keywords):
        time.sleep(1.8)                     # Phạt delay khi AI dùng payload chuẩn
        return jsonify({"results": [], "note": "Invalid keyword detected"})

    # === VULNERABLE RAW SQL - BLIND SQLi ===
    sql = f"""
        SELECT v.vehicle_number, u.user_name, s.slot_location
        FROM vehicles v 
        JOIN users u ON v.user_id = u.user_id
        LEFT JOIN parking_slots s ON s.slot_id = (
            SELECT slot_id FROM reservations 
            WHERE vehicle_id = v.vehicle_id AND is_active = 1 LIMIT 1
        )
        WHERE v.vehicle_number LIKE '%{q}%' 
           OR u.user_name LIKE '%{q}%'
    """

    try:
        results = db.session.execute(text(sql)).fetchall()
        
        data = [{
            "vehicle_number": r[0],
            "owner": r[1],
            "slot": r[2],
            "noise": "debug_" + str(time.time())[-5:],   # Noise JSON chống OCR/AI
            "ts": int(time.time() * 1000) % 100000
        } for r in results]

        return jsonify({
            "results": data, 
            "count": len(data),
            "server_time": time.strftime("%H:%M:%S")
        })
    
    except Exception:
        # Silent fail → Blind SQLi
        return jsonify({"results": [], "count": 0, "note": "No results"})