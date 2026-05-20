from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from config.db import mysql
from middleware.auth_middleware import agency_required, user_required

tours_bp = Blueprint('tours', __name__)

# ─────────────────────────────────────────
#   GET /api/tours
#   Get all tours (with optional search & filter)
# ─────────────────────────────────────────
@tours_bp.route('/', methods=['GET'])
def get_all_tours():
    query    = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    sort     = request.args.get('sort', 'id')

    cur = mysql.connection.cursor()

    sql = """
        SELECT t.*, a.agency_name, a.phone as agency_phone,
               a.email as agency_email, a.verified as agency_verified
        FROM tours t
        JOIN agencies a ON t.agency_id = a.id
        WHERE 1=1
    """
    params = []

    if query:
        sql += " AND (t.name LIKE %s OR t.destination LIKE %s OR t.category LIKE %s)"
        like = f"%{query}%"
        params += [like, like, like]

    if category and category != 'All':
        sql += " AND t.category = %s"
        params.append(category)

    if sort == 'price_low':
        sql += " ORDER BY t.price ASC"
    elif sort == 'price_high':
        sql += " ORDER BY t.price DESC"
    elif sort == 'rating':
        sql += " ORDER BY t.rating DESC"
    else:
        sql += " ORDER BY t.id DESC"

    cur.execute(sql, params)
    tours = cur.fetchall()
    cur.close()

    # Parse highlights and itinerary
    for t in tours:
        t['highlights'] = t['highlights'].split(',') if t['highlights'] else []
        t['itinerary']  = t['itinerary'].split('|') if t['itinerary'] else []
        t['price']      = float(t['price'])
        t['rating']     = float(t['rating'])

    return jsonify({'tours': tours, 'count': len(tours)}), 200


# ─────────────────────────────────────────
#   GET /api/tours/<id>
#   Get single tour detail
# ─────────────────────────────────────────
@tours_bp.route('/<int:tour_id>', methods=['GET'])
def get_tour(tour_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT t.*, a.agency_name, a.owner_name, a.phone as agency_phone,
               a.email as agency_email, a.city as agency_city,
               a.verified as agency_verified, a.rating as agency_rating
        FROM tours t
        JOIN agencies a ON t.agency_id = a.id
        WHERE t.id = %s
    """, (tour_id,))
    tour = cur.fetchone()
    cur.close()

    if not tour:
        return jsonify({'error': 'Tour not found'}), 404

    tour['highlights'] = tour['highlights'].split(',') if tour['highlights'] else []
    tour['itinerary']  = tour['itinerary'].split('|') if tour['itinerary'] else []
    tour['price']      = float(tour['price'])
    tour['rating']     = float(tour['rating'])

    return jsonify({'tour': tour}), 200


# ─────────────────────────────────────────
#   POST /api/tours
#   Add new tour (agency only)
# ─────────────────────────────────────────
@tours_bp.route('/', methods=['POST'])
@agency_required
def add_tour():
    identity = get_jwt_identity()
    agency_id = identity['id']
    data = request.get_json()

    name        = data.get('name', '').strip()
    destination = data.get('destination', '').strip()
    duration    = data.get('duration', '').strip()
    price       = data.get('price', 0)
    category    = data.get('category', '').strip()
    group_size  = data.get('group_size', '2-10 people').strip()
    description = data.get('description', '').strip()
    highlights  = data.get('highlights', '')
    itinerary   = data.get('itinerary', '')
    is_hot      = data.get('is_hot', False)

    if not name or not destination or not price:
        return jsonify({'error': 'Name, destination and price are required'}), 400

    # Convert lists to strings for storage
    if isinstance(highlights, list):
        highlights = ','.join(highlights)
    if isinstance(itinerary, list):
        itinerary = '|'.join(itinerary)

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO tours (agency_id, name, destination, duration, price,
                           category, group_size, description, highlights, itinerary, is_hot)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (agency_id, name, destination, duration, price,
          category, group_size, description, highlights, itinerary, is_hot))
    mysql.connection.commit()
    tour_id = cur.lastrowid
    cur.close()

    return jsonify({
        'message': f'Tour "{name}" published successfully!',
        'tour_id': tour_id
    }), 201


# ─────────────────────────────────────────
#   PUT /api/tours/<id>
#   Update tour (agency only, own tours)
# ─────────────────────────────────────────
@tours_bp.route('/<int:tour_id>', methods=['PUT'])
@agency_required
def update_tour(tour_id):
    identity  = get_jwt_identity()
    agency_id = identity['id']
    data      = request.get_json()

    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM tours WHERE id = %s AND agency_id = %s", (tour_id, agency_id))
    if not cur.fetchone():
        return jsonify({'error': 'Tour not found or not authorized'}), 404

    fields = ['name', 'destination', 'duration', 'price',
              'category', 'group_size', 'description', 'highlights', 'itinerary', 'is_hot']
    updates, params = [], []

    for f in fields:
        if f in data:
            val = data[f]
            if f == 'highlights' and isinstance(val, list):
                val = ','.join(val)
            if f == 'itinerary' and isinstance(val, list):
                val = '|'.join(val)
            updates.append(f"{f} = %s")
            params.append(val)

    if not updates:
        return jsonify({'error': 'Nothing to update'}), 400

    params += [tour_id, agency_id]
    cur.execute(f"UPDATE tours SET {', '.join(updates)} WHERE id = %s AND agency_id = %s", params)
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Tour updated successfully'}), 200


# ─────────────────────────────────────────
#   DELETE /api/tours/<id>
#   Delete tour (agency only, own tours)
# ─────────────────────────────────────────
@tours_bp.route('/<int:tour_id>', methods=['DELETE'])
@agency_required
def delete_tour(tour_id):
    identity  = get_jwt_identity()
    agency_id = identity['id']

    cur = mysql.connection.cursor()
    cur.execute("SELECT id FROM tours WHERE id = %s AND agency_id = %s", (tour_id, agency_id))
    if not cur.fetchone():
        return jsonify({'error': 'Tour not found or not authorized'}), 404

    cur.execute("DELETE FROM tours WHERE id = %s AND agency_id = %s", (tour_id, agency_id))
    mysql.connection.commit()
    cur.close()

    return jsonify({'message': 'Tour deleted successfully'}), 200


# ─────────────────────────────────────────
#   GET /api/tours/agency/my-tours
#   Get all tours of logged-in agency
# ─────────────────────────────────────────
@tours_bp.route('/agency/my-tours', methods=['GET'])
@agency_required
def get_my_tours():
    identity  = get_jwt_identity()
    agency_id = identity['id']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tours WHERE agency_id = %s ORDER BY created_at DESC", (agency_id,))
    tours = cur.fetchall()
    cur.close()

    for t in tours:
        t['highlights'] = t['highlights'].split(',') if t['highlights'] else []
        t['itinerary']  = t['itinerary'].split('|') if t['itinerary'] else []
        t['price']      = float(t['price'])

    return jsonify({'tours': tours, 'count': len(tours)}), 200
