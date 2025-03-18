from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

express_buses = [
    '12e', '43e', '518', '518A', '10e', '14e', '174e', '196e', '30e', '506', '513', '850e', '851e', '89e'
]

fare_table = {
    'adult': {
        'trunk': [119, 129, 140, 150, 159, 166, 173, 177, 181, 185, 189, 193, 198, 202, 206, 210, 214, 217, 220, 223, 226, 228, 230, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247],
        'express': [179, 189, 200, 210, 219, 226, 233, 237, 241, 245, 249, 253, 258, 262, 266, 270, 274, 277, 280, 283, 286, 288, 290, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307]
    },
    'student': {
        # Extended student fare tables to match distance brackets
        'trunk': [52, 57, 63, 68, 71, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74],
        'express': [82, 87, 93, 98, 101, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104, 104]
    }
}

# Distance brackets in km
distance_brackets = [3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2, 10.2, 11.2, 12.2, 13.2, 14.2, 15.2, 16.2, 17.2, 18.2, 19.2, 20.2, 21.2, 22.2, 23.2, 24.2, 25.2, 26.2, 27.2, 28.2, 29.2, 30.2, 31.2, 32.2, 33.2, 34.2, 35.2, 36.2, 37.2, 38.2, 39.2, 40.2]

def get_fare(distance, passenger_type, is_express):
    # Input validation
    if passenger_type not in fare_table:
        raise ValueError(f"Invalid passenger type: {passenger_type}")
    
    category = 'express' if is_express else 'trunk'
    fare_array = fare_table[passenger_type][category]
    
    # For distances below the first bracket
    if distance <= distance_brackets[0]:
        return fare_array[0]
        
    # For distances that fall within brackets
    for i, limit in enumerate(distance_brackets):
        if distance <= limit:
            return fare_array[i]
    
    # For distances above the highest bracket
    return fare_array[-1]

@app.route('/bus-fare', methods=['GET'])
def bus_fare():
    try:
        # Check if all required parameters are provided
        required_params = ['distance', 'passengerType', 'busService']
        missing_params = []
        
        for param in required_params:
            if param not in request.args or not request.args.get(param):
                missing_params.append(param)
        
        if missing_params:
            return jsonify({
                'error': 'Missing required parameters',
                'missing': missing_params
            }), 400
        
        # Get and validate parameters
        try:
            distance = float(request.args.get('distance'))
        except ValueError:
            return jsonify({'error': 'Distance must be a valid number'}), 400
            
        passenger_type = request.args.get('passengerType', '').lower()
        bus_service = request.args.get('busService', '')
        
        # Validate values
        if distance < 0:
            return jsonify({'error': 'Distance cannot be negative'}), 400
            
        if passenger_type not in fare_table:
            return jsonify({
                'error': f'Invalid passenger type',
                'supported_types': list(fare_table.keys())
            }), 400
            
        if not bus_service.strip():
            return jsonify({'error': 'Bus service cannot be empty'}), 400

        # Check if the bus service exists in our express buses list
        is_express = any(bus_service.lower() == express_bus.lower() for express_bus in express_buses)
        fare = get_fare(distance, passenger_type, is_express)

        # Return response with more details
        return jsonify({
            'busService': bus_service,
            'isExpress': is_express,
            'distance': distance,
            'passengerType': passenger_type,
            'fare': fare,
            'currency': 'cents'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/fare-info', methods=['GET'])
def fare_info():
    """Endpoint to get information about the fare system"""
    return jsonify({
        'passengerTypes': list(fare_table.keys()),
        'expressBuses': express_buses,
        'maxDistance': distance_brackets[-1],
        'minFare': min(fare_table['adult']['trunk']),
        'maxFare': max(fare_table['adult']['express'])
    })

# Add a health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({'status': 'OK', 'version': '1.0.0'}), 200

# Add a catch-all route for undefined endpoints
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found. Please check API documentation.'}), 404

# Add a handler for invalid HTTP methods
@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed. Please check API documentation.'}), 405

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)