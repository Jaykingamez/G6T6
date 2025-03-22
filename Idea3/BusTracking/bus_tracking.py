import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# LTA API Configuration
LTA_API_URL = "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"
LTA_API_KEY = os.environ.get("LTA_API_KEY", "your_api_key_here")

def get_bus_arrival_info(bus_stop_code, service_no):
    """Call LTA API to get bus arrival information"""
    headers = {
        'AccountKey': LTA_API_KEY,
        'accept': 'application/json'
    }
    
    params = {
        'BusStopCode': bus_stop_code,
        'ServiceNo': service_no
    }
    
    try:
        response = requests.get(LTA_API_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling LTA API: {e}")
        return None

@app.route('/bus_arrival', methods=['GET'])
def bus_arrival():
    """Endpoint to get bus arrival information"""
    bus_stop_code = request.args.get('BusStopCode')
    service_no = request.args.get('BusID')
    
    if not bus_stop_code or not service_no:
        return jsonify({"error": "Missing required parameters"}), 400
    
    arrival_data = get_bus_arrival_info(bus_stop_code, service_no)
    
    if arrival_data:
        return jsonify(arrival_data), 200
    else:
        return jsonify({"error": "Failed to retrieve bus arrival information"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "BusTracking"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
