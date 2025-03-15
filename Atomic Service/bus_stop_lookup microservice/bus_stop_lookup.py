# bus_stop_lookup.py
# http://localhost:5002/apidocs
import redis
import json
import time
from flask import Flask, request, jsonify
import os
import math
from flasgger import Swagger, swag_from
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/" 
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "Bus Stop Lookup API",
        "description": "API to find the nearest bus stop based on Google Maps Directions data",
        "version": "1.0",
        "contact": {
            "email": "support@example.com"
        }
    },
    "host": "localhost:5002",
    "basePath": "/",
    "schemes": ["http"],
    "consumes": ["application/json"],
    "produces": ["application/json"]
}

swagger = Swagger(app, config=swagger_config, template=template)

# Redis connection
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", 6379))
client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Sample Bus Stop Data
bus_stops = {
    "value": [
        {
            "BusStopCode": "01012",
            "RoadName": "Victoria St",
            "Description": "Hotel Grand Pacific",
            "Latitude": 1.29684825487647,
            "Longitude": 103.85253591654006
        },
        {
            "BusStopCode": "01013",
            "RoadName": "Victoria St",
            "Description": "St. Joseph's Ch",
            "Latitude": 1.29770970610083,
            "Longitude": 103.8532247463225
        }
    ]
}

# Wait for Redis to be ready
def wait_for_redis():
    for attempt in range(10):  # Try 10 times
        try:
            print(f"Connection attempt {attempt+1}/10 to Redis at {redis_host}:{redis_port}")
            if client.ping():
                print(f"✅ Redis is ready at {redis_host}:{redis_port}!")
                # Check if data exists
                if client.exists("bus_stops"):
                    data = client.get("bus_stops")
                    print(f"Found bus_stops data in Redis ({len(data)} bytes)")
                else:
                    print("⚠️ No bus_stops data found in Redis")
                return
        except redis.ConnectionError as e:
            print(f"⏳ Waiting for Redis to be ready... Error: {str(e)}")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Unexpected error checking Redis: {str(e)}")
            time.sleep(2)
    raise Exception("❌ Redis did not start in time.")

# Auto-load Bus Stops into Redis
def load_bus_stops():
    if not client.exists("bus_stops"):  # Only load if empty
        print("🔄 Loading bus stops into Redis...")
        client.set("bus_stops", json.dumps(bus_stops))
        print("✅ Bus stops loaded!")
    else:
        print("✅ Bus stops already exist in Redis.")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def find_nearest_bus_stop(lat, lng):
    stored_bus_stops = json.loads(client.get("bus_stops"))
    lta_bus_stops = stored_bus_stops["value"]
    
    if not lta_bus_stops:
        print("No bus stops available for search.")
        return None
    nearest_stop = min(lta_bus_stops, key=lambda stop: haversine(lat, lng, stop["Latitude"], stop["Longitude"]))
    return nearest_stop

def extract_first_transit_details(routes):
    extracted_details = []
    
    for route in routes:
        for leg in route.get("legs", []):
            for step in leg.get("steps", []):
                if "transit_details" in step:
                    transit = step["transit_details"]
                    transport_mode = step.get("travel_mode", "").lower()
                    
                    if transport_mode == "transit":
                        first_transport = {}
                        line_name = transit["line"]["name"]
                        
                        if transit["line"].get("vehicle", {}).get("type", "").lower() == "bus":
                            dep_lat = transit["departure_stop"]["location"]["lat"]
                            dep_lng = transit["departure_stop"]["location"]["lng"]
                            nearest_stop = find_nearest_bus_stop(dep_lat, dep_lng)
                            
                            first_transport["BusStopCode"] = nearest_stop["BusStopCode"] if nearest_stop else "Unknown"
                            first_transport["Description"] = transit["departure_stop"]["name"]
                            first_transport["BusNumber"] = line_name
                        else:
                            first_transport["TrainLine"] = line_name
                        
                        extracted_details.append(first_transport)
                        break  # Only extract the first public transport step in the route
    
    return extracted_details

# Wait for Redis & Load Data
wait_for_redis()
load_bus_stops()

@app.route("/")
def notify():
    return "<h1>Hey visit http://localhost:5002/apidocs></a> for api docs</h1>"

@app.route("/bus_stop_lookup", methods=["POST"])
@swag_from({
    "summary": "Find nearest bus stop from Google Directions API (Note: It takes the entire JSON response))",
    "tags": ["Bus Stops"],
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "routes": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        },
                        "description": "Google Directions API routes array"
                    }
                }
            }
        }
    ],
    "responses": {
        "200": {
            "description": "Transit details with nearest bus stop information"
        },
        "400": {
            "description": "No public transport step found in route"
        }
    }
})
def bus_stop_lookup():
    data = request.get_json()
    routes = data.get("routes", [])

    transit_details = extract_first_transit_details(routes)
    
    if not transit_details:
        return jsonify({"error": "No public transport steps found"}), 400
    
    return jsonify({"transit_details": transit_details})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)