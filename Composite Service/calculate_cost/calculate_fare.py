# WIP
# Check if can handle multiple bus services / train for each route
# return multiple routes not just the first one
# Return total distance traveled by public transport only
# handle transfer cost 
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

BUS_FARE_SERVICE_URL = "http://localhost:5003/bus-fare"
TRAIN_FARE_SERVICE_URL = "http://localhost:5004/train-fare"

def get_fare(url, params):
    try:
        response = requests.get(url, params=params)
        response_data = response.json()
        return response_data.get("fare", 0)  # Ensure we only extract the fare value
    except Exception as e:
        return {"error": f"Failed to fetch fare: {str(e)}"}

@app.route('/calculate-fare', methods=['POST'])
def calculate_fare():
    try:
        data = request.json
        passenger_type = data.get("passengerType", "adult").lower()
        peak_hour = data.get("peakHour", False)
        
        if "routes" not in data or not isinstance(data["routes"], list) or len(data["routes"]) == 0:
            return jsonify({"error": "Invalid Google Directions response. No routes found."}), 400
        
        best_route = data["routes"][0]  # Assume first route is the best
        total_fare = 0
        fare_breakdown = []
        
        for leg in best_route.get("legs", []):
            for step in leg.get("steps", []):
                travel_mode = step.get("travel_mode", "").lower()
                distance_km = step.get("distance", {}).get("value", 0) / 1000  # Convert meters to km
                
                if travel_mode == "transit":
                    transit_details = step.get("transit_details", {})
                    line_info = transit_details.get("line", {})
                    line_type = line_info.get("vehicle", {}).get("type", "")
                    bus_number = line_info.get("name", "")
                    
                    if line_type == "BUS":
                        fare = get_fare(BUS_FARE_SERVICE_URL, {
                            "distance": distance_km,
                            "passengerType": passenger_type,
                            "busService": bus_number  # Ensure bus number is passed
                        })
                    elif line_type == "SUBWAY":  # Subway == Train in this case
                        fare = get_fare(TRAIN_FARE_SERVICE_URL, {
                            "distance": distance_km,
                            "passengerType": passenger_type,
                            "peakHour": str(peak_hour).lower()
                        })
                    else:
                        fare = 0  # Non-supported transit type
                    
                    if isinstance(fare, dict):  # Handle errors
                        return jsonify(fare), 500
                    
                    total_fare += fare
                    fare_breakdown.append({"mode": line_type, "bus_number": bus_number, "distance_km": distance_km, "fare": fare})
        
        return jsonify({
            "total_fare": total_fare,
            "currency": "cents",
            "fare_breakdown": fare_breakdown
        })
    
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5032, debug=True)
