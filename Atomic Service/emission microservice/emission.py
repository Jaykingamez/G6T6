from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# Example emission factors (kg CO2 per km)
EMISSION_FACTORS = {
    "car": 0.292,
    "bus": 0.181,
    "train": 0.041,
}

@app.route('/emission', methods=['GET'])
def get_emission():
    """
    Calculate CO2 emissions based on transport mode and distance.
    ---
    parameters:
      - name: mode
        in: query
        type: string
        required: true
        description: Transport mode (e.g., car, bus, train)
      - name: distance
        in: query
        type: number
        required: true
        description: Distance traveled in kilometers
    responses:
      200:
        description: Successful response
        schema:
          type: object
          properties:
            mode:
              type: string
              description: Transport mode
            distance_km:
              type: number
              description: Distance in kilometers
            emission_kg_co2:
              type: number
              description: CO2 emissions in kg
      400:
        description: Bad request (invalid input)
      500:
        description: Server error
    """
    try:
        mode = request.args.get("mode", "").lower()
        distance = request.args.get("distance", type=float)

        # Validate inputs
        if not mode or mode not in EMISSION_FACTORS:
            return jsonify({"error": "Invalid or missing 'mode' parameter"}), 400

        if distance is None or distance <= 0:
            return jsonify({"error": "'distance' must be a positive number"}), 400

        # Calculate emissions
        emission = EMISSION_FACTORS[mode] * distance

        return jsonify({
            "mode": mode,
            "distance_km": distance,
            "emission_kg_co2": round(emission, 4)
        })

    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@app.route('/emission', methods=['POST'])
def calculate_route_emissions():
    """
    Calculate CO2 emissions for all routes in a directions response.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          description: Google Directions API response format
    responses:
      200:
        description: Successful response with emissions for all routes
      400:
        description: Bad request (invalid input)
      500:
        description: Server error
    """
    try:
        # Extract directions data from request body
        directions_data = request.json
        
        # Validate input
        if not directions_data or not isinstance(directions_data, dict):
            return jsonify({"error": "Invalid directions data format"}), 400
            
        # Extract routes from the directions data
        routes = directions_data.get('routes', [])
        if not routes:
            return jsonify({"error": "No routes found in directions data"}), 400
        
        # Process each route to get emissions
        emissions_results = []
        for route_index, route in enumerate(routes):
            route_emissions = []
            total_emissions = 0
            
            # Process each leg and step in the route
            for leg in route.get("legs", []):
                for step in leg.get("steps", []):
                    # Get travel mode and distance
                    travel_mode = step.get("travel_mode", "").lower()
                    
                    # Extract distance in meters and convert to kilometers
                    distance_m = step.get("distance", {}).get("value", 0)
                    distance_km = distance_m / 1000
                    
                    # Skip steps with zero distance
                    if distance_km <= 0:
                        continue
                    
                    # Determine the actual mode of transport
                    if travel_mode == "transit":
                        transit_details = step.get("transit_details", {})
                        line_info = transit_details.get("line", {})
                        vehicle_type = line_info.get("vehicle", {}).get("type", "").lower()
                        
                        # Map Google's vehicle types to supported modes
                        if vehicle_type in ["bus", "bus_service"]:
                            mode = "bus"
                        elif vehicle_type in ["subway", "train", "heavy_rail", "commuter_train", "rail"]:
                            mode = "train"
                        else:
                            # Default to bus for other transit types
                            mode = "bus"
                    else:
                        # Map non-transit modes to supported emission modes
                        if travel_mode == "driving":
                            mode = "car"
                        elif travel_mode == "walking" or travel_mode == "bicycling":
                            # Skip walking/cycling as they have zero emissions
                            continue
                        else:
                            # Default to bus for unknown modes
                            mode = "bus"
                    
                    # Calculate emissions for this segment
                    if mode in EMISSION_FACTORS:
                        emission_kg_co2 = round(EMISSION_FACTORS[mode] * distance_km, 4)
                        
                        # Create segment data
                        segment_data = {
                            'mode': mode,
                            'distance_km': distance_km,
                            'emission_kg_co2': emission_kg_co2
                        }
                        
                        route_emissions.append(segment_data)
                        total_emissions += emission_kg_co2
            
            # Create a summary for this route
            route_summary = {
                'routeIndex': route_index,
                'totalEmissions': round(total_emissions, 4),
                'segments': route_emissions
            }
            
            emissions_results.append(route_summary)
        
        return jsonify({"routeEmissions": emissions_results})
            
    except Exception as e:
        return jsonify({"error": f"Error processing emissions data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)