from flask import request, jsonify
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from endpoints.auth import login_required, verify_identity
from flask_jwt_extended import get_jwt_identity

# Pobieranie wszystkich harmonogramów posiłków
@login_required
def get_food_schedules():
    """
    Get all food schedules
    ---
    tags:
      - Food Schedules
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        description: Number of food schedules to return
        default: 10
      - in: query
        name: page
        type: integer
        description: Page number
        default: 1
    responses:
      200:
        description: A list of food schedules
        schema:
          type: object
          properties:
            food_schedules:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  meal_history_id:
                    type: integer
                  at:
                    type: string
                    format: date-time
                  user_id:
                    type: integer
            total:
              type: integer
            pages:
              type: integer
            current_page:
              type: integer
            page_size:
              type: integer
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        limit = request.args.get('limit', default=10, type=int)
        page = request.args.get('page', default=1, type=int)

        if limit < 1 or page < 1:
            return jsonify({"error": "Limit and page must be positive integers"}), 400

        offset = (page - 1) * limit

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT COUNT(*) FROM food_schedule')
        total = cursor.fetchone()['count']

        cursor.execute('''
            SELECT * FROM food_schedule
            ORDER BY id
            LIMIT %s OFFSET %s
        ''', (limit, offset))
        food_schedules = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "food_schedules": food_schedules,
            "total": total,
            "pages": (total // limit) + (1 if total % limit > 0 else 0),
            "current_page": page,
            "page_size": limit
        })
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

# Pobieranie harmonogramu posiłków według ID
@login_required
def get_food_schedule(schedule_id):
    """
    Get a food schedule by ID
    ---
    tags:
      - Food Schedules
    security:
      - Bearer: []
    parameters:
      - in: path
        name: schedule_id
        type: integer
        required: true
        description: The ID of the food schedule to retrieve
    responses:
      200:
        description: A food schedule object
        schema:
          type: object
          properties:
            id:
              type: integer
            meal_history_id:
              type: integer
            at:
              type: string
              format: date-time
            user_id:
              type: integer
      404:
        description: Food schedule not found
        schema:
          type: object
          properties:
            message:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM food_schedule WHERE id = %s', (schedule_id,))
        food_schedule = cursor.fetchone()

        cursor.close()
        conn.close()

        if food_schedule:
            return jsonify(food_schedule)
        else:
            return jsonify({"message": "Food schedule not found"}), 404
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

# Tworzenie harmonogramu posiłków
@login_required
def create_food_schedule():
    """
    Create a new food schedule
    ---
    tags:
      - Food Schedules
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - meal_id
            - meal_version
            - at
          properties:
            meal_id:
              type: integer
              description: The ID of the meal
            meal_version:
              type: integer
              description: The version of the meal
            at:
              type: string
              format: date-time
              description: The time of the meal in 'HH:MM:SS DD-MM-YYYY' format
    responses:
      201:
        description: Food schedule created
        schema:
          type: object
          properties:
            message:
              type: string
            food_schedule_id:
              type: integer
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      404:
        description: Meal history not found
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
            message:
              type: string
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('meal_id') or not data.get('meal_version') or not data.get('at'):
            return jsonify({"error": "meal_id, meal_version, at, and user_id are required"}), 400

        user_id = get_jwt_identity()

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Validate meal_id and meal_version
        cursor.execute('SELECT * FROM meal_history WHERE meal_id = %s AND meal_version = %s', (data['meal_id'], data['meal_version']))
        meal_history = cursor.fetchone()
        if not meal_history:
            cursor.close()
            conn.close()
            return jsonify({"error": "Meal history not found for the given ID and version"}), 404

        # Validate 'at' is greater than current time
        at_time = datetime.strptime(data['at'], '%H:%M:%S %d-%m-%Y')
        if at_time <= datetime.utcnow():
            cursor.close()
            conn.close()
            return jsonify({"error": "'at' must be a future time"}), 400

        # Create new food schedule
        cursor.execute('''
            INSERT INTO food_schedule (meal_history_id, at, user_id)
            VALUES (%s, %s, %s)
            RETURNING id
        ''', (meal_history['id'], at_time, user_id))
        new_food_schedule_id = cursor.fetchone()['id']

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Food schedule created", "food_schedule_id": new_food_schedule_id}), 201
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

# Usuwanie harmonogramu posiłków
@login_required
def delete_food_schedule(schedule_id):
    """
    Delete a food schedule
    ---
    tags:
      - Food Schedules
    security:
      - Bearer: []
    parameters:
      - in: path
        name: schedule_id
        type: integer
        required: true
        description: The ID of the food schedule to delete
    responses:
      200:
        description: Food schedule deleted
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: Food schedule not found
        schema:
          type: object
          properties:
            message:
              type: string
      403:
        description: Unauthorized
        schema:
          type: object
          properties:
            error:
              type: string
            message:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM food_schedule WHERE id = %s', (schedule_id,))
        food_schedule = cursor.fetchone()
        
        if not food_schedule:
            cursor.close()
            conn.close()
            return jsonify({"message": "Food schedule not found"}), 404
        
        verifivation = verify_identity(food_schedule['user_id'], 'You can only delete food schedules you created')
        if verifivation is not None:
            cursor.close()
            conn.close()
            return verifivation

        cursor.execute('DELETE FROM food_schedule WHERE id = %s', (schedule_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Food schedule deleted"})
        
            
    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": str(e)}), 500

# Pobieranie zaplanowanych posiłków dla danego użytkownika
@login_required
def get_food_schedule_for_user(user_id):
    """
    Get food schedules for a user
    ---
    tags:
      - Food Schedules
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to retrieve food schedules for
    responses:
      200:
        description: A list of food schedules
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              meal_history_id:
                type: integer
              at:
                type: string
                format: date-time
              user_id:
                type: integer
              meal:
                type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('SELECT * FROM food_schedule WHERE user_id = %s', (user_id,))
        food_schedules = cursor.fetchall()

        result = []
        for schedule in food_schedules:
            cursor.execute('SELECT * FROM meal_history WHERE id = %s', (schedule['meal_history_id'],))
            meal_history = cursor.fetchone()
            if meal_history:
                schedule_details = dict(schedule)
                schedule_details['meal'] = meal_history['composition']['meal']
                result.append(schedule_details)

        cursor.close()
        conn.close()

        return jsonify(result)

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500

# Pobieranie zaplanowanych posiłków dla danego użytkownika z danego dnia
@login_required
def get_food_schedule_for_user_by_date(user_id, date):
    """
    Get food schedules for a user by date
    ---
    tags:
      - Food Schedules
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: The ID of the user to retrieve food schedules for
      - in: path
        name: date
        type: string
        required: true
        description: The date in 'DD-MM-YYYY' format
    responses:
      200:
        description: A list of food schedules
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              meal_history_id:
                type: integer
              at:
                type: string
                format: date-time
              user_id:
                type: integer
              meal:
                type: string
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Internal server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        start_date = datetime.strptime(date, '%d-%m-%Y')
        end_date = start_date + timedelta(days=1)

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute('''
            SELECT * FROM food_schedule
            WHERE user_id = %s AND at >= %s AND at < %s
        ''', (user_id, start_date, end_date))
        food_schedules = cursor.fetchall()

        result = []
        for schedule in food_schedules:
            cursor.execute('SELECT * FROM meal_history WHERE id = %s', (schedule['meal_history_id'],))
            meal_history = cursor.fetchone()
            if meal_history:
                schedule_details = dict(schedule)
                schedule_details['meal'] = meal_history['composition']['meal']
                result.append(schedule_details)

        cursor.close()
        conn.close()

        return jsonify(result)

    except ValueError:
        return jsonify({"error": "Invalid date format. Use 'DD-MM-YYYY'"}), 400

    except Exception as e:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        return jsonify({"error": "An unexpected error occurred", "message": str(e)}), 500