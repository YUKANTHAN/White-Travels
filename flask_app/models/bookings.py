try:
    from flask_app.config.mongodb_connection import connectToMongo
    from bson.objectid import ObjectId
except ImportError:
    # Fail-safe mock for local demo environments
    connectToMongo = None
    ObjectId = None

from flask import flash
import json
DATABASE = "white_travels_db"

class Booking:
    def __init__(self,data):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.type = data.get('type', 'General')
        self.created_at = data.get('created_at', "")
        self.updated_at = data.get('updated_at', "")
        # Store all other data as attributes
        for key, value in data.items():
            if key not in ['id', 'user_id', 'type', 'created_at', 'updated_at']:
                setattr(self, str(key), value)

    @classmethod
    def save(cls, data):
        try:
            if not connectToMongo:
                raise ImportError("No DB connection available")
            db = connectToMongo(DATABASE)
            bookings = db.get_collection("bookings")
            data['created_at'] = data.get('created_at', "")
            data['updated_at'] = data.get('updated_at', "")
            return str(bookings.insert_one(data).inserted_id)
        except Exception as e:
            # PRO-HACKATHON FALLBACK: Simulation Mode (JSON Logging)
            print(f"[SIMULATION] DB offline or inaccessible. Logging booking to local manifest...")
            with open('bookings_dump.json', 'a') as f:
                json.dump(data, f)
                f.write('\n')
            return "SIM-BOOKING-99"

    @staticmethod
    def validate(data_data):
        is_valid = True
        # Basic validation for general bookings
        if 'where_to' in data_data:
            if len(data_data['where_to']) < 2:
                is_valid = False
                flash("Where to must be at least 2 characters long", "err_where_to")
        if 'how_many' in data_data:
            if not data_data['how_many'] or int(data_data['how_many']) < 1:
                is_valid = False
                flash("How many field must be 1 guest or more", "err_how_many")
        return is_valid
