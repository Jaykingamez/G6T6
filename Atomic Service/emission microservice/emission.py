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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)