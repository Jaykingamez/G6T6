from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# BUS_FARE_SERVICE_URL = "http://localhost:5003/bus-fare" <-- this does not work in Docker
# TRAIN_FARE_SERVICE_URL = "http://localhost:5004/train-fare" <-- this does not work in Docker

# ✅ Use Docker service names instead of localhost
BUS_FARE_SERVICE_URL = "http://bus_fare:5003/bus-fare"
TRAIN_FARE_SERVICE_URL = "http://train_fare:5004/train-fare"

def get_fare(url, params):
    try:
        response = requests.get(url, params=params)
        response_data = response.json()
        return response_data.get("fare", 0)
    except Exception as e:
        return {"error": f"Failed to fetch fare: {str(e)}"}

@app.route('/calculate-fare', methods=['POST'])
def calculate_fare():
    try:
        data = request.json
        
        # Handle query parameters if they exist (fall back to JSON body if not)
        query_params = request.args
        passenger_type = query_params.get("passengerType") or data.get("passengerType", "adult")
        peak_hour = query_params.get("peakHour") or data.get("peakHour", False)
        
        # Normalize the values
        passenger_type = str(passenger_type).lower()
        peak_hour = str(peak_hour).lower() == 'true' if isinstance(peak_hour, str) else bool(peak_hour)
        
        if "routes" not in data or not isinstance(data["routes"], list):
            return jsonify({"error": "Invalid Google Directions response. No routes found."}), 400
        
        all_routes = []
        
        for route in data["routes"]:
            route_fare = 0
            fare_breakdown = []
            
            for leg in route.get("legs", []):
                for step in leg.get("steps", []):
                    travel_mode = step.get("travel_mode", "").lower()
                    distance_m = step.get("distance", {}).get("value", 0)
                    distance_km = distance_m / 1000
                    
                    if travel_mode == "transit":
                        transit_details = step.get("transit_details", {})
                        line_info = transit_details.get("line", {})
                        line_type = line_info.get("vehicle", {}).get("type", "").upper()
                        bus_number = line_info.get("name", "")
                        
                        if line_type == "BUS":
                            fare = get_fare(BUS_FARE_SERVICE_URL, {
                                "distance": distance_km,
                                "passengerType": passenger_type,
                                "busService": bus_number
                            })
                        elif line_type in ["SUBWAY", "TRAIN", "HEAVY_RAIL", "COMMUTER_TRAIN"]:
                            fare = get_fare(TRAIN_FARE_SERVICE_URL, {
                                "distance": distance_km,
                                "passengerType": passenger_type,
                                "peakHour": str(peak_hour).lower()
                            })
                        else:
                            fare = 0
                        
                        if isinstance(fare, dict):
                            return jsonify(fare), 500
                        
                        route_fare += fare
                        fare_breakdown.append({
                            "mode": line_type,
                            "service_number": bus_number,
                            "distance_km": distance_km,
                            "fare": fare
                        })
            
            all_routes.append({
                "total_fare": route_fare,
                "fare_breakdown": fare_breakdown
            })
        
        return jsonify({
            "all_routes": all_routes,
            "currency": "cents",
            "parameters_used": {
                "passengerType": passenger_type,
                "peakHour": peak_hour
            }
        })
    
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5032, debug=True)