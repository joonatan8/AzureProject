import os
import bson
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
from flask.json import JSONEncoder

# Custom JSON Encoder
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Load environment variables and connect to MongoDB
load_dotenv()
connection_string = os.environ.get("CONNECTION_STRING")
mongo_client = MongoClient(connection_string)
db = mongo_client.FlightManagementDB

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

# API to get all data for displaying
@app.route('/api/airlines')
def get_airlines():
    airlines = list(db.Airlines.find({}, {'_id': 0}))
    return jsonify(airlines)

@app.route('/api/airports')
def get_airports():
    airports = db.Airports.find({}, {'_id': 0})
    airports_list = []
    for airport in airports:
        # Ensure the location object exists and has the coordinates
        if 'location' in airport and 'coordinates' in airport['location']:
            # Format coordinates as "latitude, longitude"
            airport['coordinates'] = f"{airport['location']['coordinates'][1]}, {airport['location']['coordinates'][0]}"
        else:
            airport['coordinates'] = "Not available"  # Handle missing coordinates
        airports_list.append(airport)
    return jsonify(airports_list)

@app.route('/api/flights')
def get_flights():
    flights = db.Flights.find({})
    flights_list = []
    for flight in flights:
        # Resolve airline_id to airline name
        airline = db.Airlines.find_one({"_id": flight['airline_id']})
        airline_name = airline['name'] if airline else "Unknown Airline"  # Fallback if airline not found

        flight_data = {
            'flight_number': flight.get('flight_number', 'N/A'),
            'departure_airport': flight.get('departure_airport', 'N/A'),
            'arrival_airport': flight.get('arrival_airport', 'N/A'),
            'departure_time': flight.get('departure_time', 'N/A').isoformat() if flight.get('departure_time') else 'N/A',
            'arrival_time': flight.get('arrival_time', 'N/A').isoformat() if flight.get('arrival_time') else 'N/A',
            'airline': airline_name
        }
        flights_list.append(flight_data)

    return jsonify(flights_list)

# CRUD Operations for Airlines
@app.route('/api/airlines', methods=['GET', 'POST'])
def airlines():
    if request.method == 'POST':
        airline = request.json
        db.Airlines.insert_one(airline)
        return jsonify(airline), 201
    else:
        airlines = list(db.Airlines.find({}, {'_id': 0}))
        return jsonify(airlines)

@app.route('/api/airlines/<id>', methods=['GET', 'PUT', 'DELETE'])
def airline(id):
    if request.method == 'GET':
        airline = db.Airlines.find_one({"_id": bson.ObjectId(id)})
        if airline:
            airline['_id'] = str(airline['_id'])
            return jsonify(airline)
        else:
            return jsonify({"error": "Airline not found"}), 404
    elif request.method == 'PUT':
        updated_data = request.json
        result = db.Airlines.update_one({"_id": bson.ObjectId(id)}, {"$set": updated_data})
        if result.modified_count:
            return jsonify({"msg": "Airline updated successfully"})
        else:
            return jsonify({"error": "Nothing was updated"}), 404
    elif request.method == 'DELETE':
        result = db.Airlines.delete_one({"_id": bson.ObjectId(id)})
        if result.deleted_count:
            return jsonify({"msg": "Airline deleted successfully"})
        else:
            return jsonify({"error": "Airline not found"}), 404

# CRUD Operations for Airports
@app.route('/api/airports', methods=['GET', 'POST'])
def airports():
    if request.method == 'POST':
        airport = request.json
        db.Airports.insert_one(airport)
        return jsonify(airport), 201
    else:
        airports = list(db.Airports.find({}, {'_id': 0}))
        return jsonify(airports)

@app.route('/api/airports/<id>', methods=['GET', 'PUT', 'DELETE'])
def airport(id):
    if request.method == 'GET':
        airport = db.Airports.find_one({"_id": bson.ObjectId(id)})
        if airport:
            airport['_id'] = str(airport['_id'])
            return jsonify(airport)
        else:
            return jsonify({"error": "Airport not found"}), 404
    elif request.method == 'PUT':
        updated_data = request.json
        result = db.Airports.update_one({"_id": bson.ObjectId(id)}, {"$set": updated_data})
        if result.modified_count:
            return jsonify({"msg": "Airport updated successfully"})
        else:
            return jsonify({"error": "Nothing was updated"}), 404
    elif request.method == 'DELETE':
        result = db.Airports.delete_one({"_id": bson.ObjectId(id)})
        if result.deleted_count:
            return jsonify({"msg": "Airport deleted successfully"})
        else:
            return jsonify({"error": "Airport not found"}), 404

# CRUD Operations for Flights
@app.route('/api/flights', methods=['GET', 'POST'])
def flights():
    if request.method == 'POST':
        flight = request.json
        db.Flights.insert_one(flight)
        return jsonify(flight), 201
    else:
        flights = list(db.Flights.find({}, {'_id': 0}))
        return jsonify(flights)

@app.route('/api/flights/<id>', methods=['GET', 'PUT', 'DELETE'])
def flight(id):
    if request.method == 'GET':
        flight = db.Flights.find_one({"_id": bson.ObjectId(id)})
        if flight:
            flight['_id'] = str(flight['_id'])
            return jsonify(flight)
        else:
            return jsonify({"error": "Flight not found"}), 404
    elif request.method == 'PUT':
        updated_data = request.json
        result = db.Flights.update_one({"_id": bson.ObjectId(id)}, {"$set": updated_data})
        if result.modified_count:
            return jsonify({"msg": "Flight updated successfully"})
        else:
            return jsonify({"error": "Nothing was updated"}), 404
    elif request.method == 'DELETE':
        result = db.Flights.delete_one({"_id": bson.ObjectId(id)})
        if result.deleted_count:
            return jsonify({"msg": "Flight deleted successfully"})
        else:
            return jsonify({"error": "Flight not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)