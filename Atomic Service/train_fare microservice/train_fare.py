from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

fare_table = {
    'adult': {
        'peak': [119, 129, 140, 150, 159, 166, 173, 177, 181, 185, 189, 193, 198, 202, 206, 210, 214, 217, 220, 223, 226, 228, 230, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247],
        'off_peak': [69, 79, 90, 100, 109, 116, 123, 127, 131, 135, 139, 143, 148, 152, 156, 160, 164, 167, 170, 173, 176, 178, 180, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197]
    },
    'student': {
        'peak': [52, 57, 63, 68, 71, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74, 74],
        'off_peak': [2, 7, 13, 18, 21, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24]
    }
}

distance_brackets = [3.2, 4.2, 5.2, 6.2, 7.2, 8.2, 9.2, 10.2, 11.2, 12.2, 13.2, 14.2, 15.2, 16.2, 17.2, 18.2, 19.2, 20.2, 21.2, 22.2, 23.2, 24.2, 25.2, 26.2, 27.2, 28.2, 29.2, 30.2, 31.2, 32.2, 33.2, 34.2, 35.2, 36.2, 37.2, 38.2, 39.2, 40.2]

def get_fare(distance, passenger_type, peak_hour):
    if passenger_type not in fare_table:
        raise ValueError(f"Invalid passenger type: {passenger_type}")
    
    fare_array = fare_table[passenger_type]['peak' if peak_hour else 'off_peak']
    
    if distance <= distance_brackets[0]:
        return fare_array[0]
    
    for i, limit in enumerate(distance_brackets):
        if distance <= limit:
            return fare_array[i]
    
    return fare_array[-1]

@app.route('/train-fare', methods=['GET'])
def train_fare():
    try:
        required_params = ['distance', 'passengerType', 'peakHour']
        missing_params = [param for param in required_params if param not in request.args]
        
        if missing_params:
            return jsonify({'error': 'Missing required parameters', 'missing': missing_params}), 400
        
        try:
            distance = float(request.args.get('distance'))
        except ValueError:
            return jsonify({'error': 'Distance must be a valid number'}), 400
        
        passenger_type = request.args.get('passengerType', '').lower()
        peak_hour = request.args.get('peakHour', '').lower() in ['true', '1']
        
        if distance < 0:
            return jsonify({'error': 'Distance cannot be negative'}), 400
        
        if passenger_type not in fare_table:
            return jsonify({'error': 'Invalid passenger type', 'supported_types': list(fare_table.keys())}), 400
        
        fare = get_fare(distance, passenger_type, peak_hour)
        
        return jsonify({
            'distance': distance,
            'passengerType': passenger_type,
            'peakHour': peak_hour,
            'fare': fare,
            'currency': 'cents'
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5004, debug=True)
