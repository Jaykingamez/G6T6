# directions.py
# http://localhost:5001/apidocs/
from flask import Flask, request, jsonify
import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from flasgger import Swagger
from flask_cors import CORS

# Load environment variables from .env file
# load_dotenv()
# Load .env file from two directories up
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)

# Initialize Flask app
app = Flask(__name__)
CORS(app)


# Get the Google Maps API Key from environment variables (secure practice)
google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
print(google_maps_api_key)

if not google_maps_api_key:
    raise ValueError("Google Maps API Key not found. Please set the GOOGLE_MAPS_API_KEY environment variable.")

# Initialize Swagger for documentation
app.config['SWAGGER'] = {
    'title': 'Google Maps Directions Microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Gets directions between origin and destination using Google Maps Directions API',
    'tags': [
        {
            'name': 'Directions',
            'description': 'Endpoints related to getting directions'
        }
    ]
}
swagger = Swagger(app)

def get_google_maps_directions(origin, destination, **optional_params):
    """
    Calls the Google Maps Directions API with required and optional parameters.
    """
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    
    # Define required parameters
    params = {
        'origin': origin,
        'destination': destination,
        'key': google_maps_api_key,
    }
    
    # Include optional parameters
    params.update(optional_params)
    
    # Call the API
    response = requests.get(base_url, params=params)
    
    # If successful, return the directions
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Error fetching directions from Google Maps API", "status_code": response.status_code}

@app.route("/directions")
def get_directions():
    """
    Get directions between origin and destination
    ---
    tags:
      - Directions
    parameters:
        - name: origin
          in: query
          required: true
          description: The starting point for the directions
          schema:
            type: string
        - name: destination
          in: query
          required: true
          description: The destination point for the directions
          schema:
            type: string
        - name: mode
          in: query
          required: false
          description: The mode of transport (driving, walking, biking, transit)
          schema:
            type: string
            default: "transit"
        - name: departure_time
          in: query
          required: false
          description: The departure time (can be now, or a timestamp)
          schema:
            type: string
        - name: avoid
          in: query
          required: false
          description: Avoid certain routes (tolls, highways)
          schema:
            type: string
        - name: alternatives
          in: query
          required: false
          description: Specifies whether to return alternative routes (true or false)
          schema:
            type: string
            default: "true"
    responses:
        200:
            description: Directions retrieved successfully
        400:
            description: Bad request, missing parameters
        500:
            description: Internal server error
    """
    # Get query parameters
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    mode = request.args.get('mode', 'driving')  # Default to 'driving'
    departure_time = request.args.get('departure_time')
    avoid = request.args.get('avoid')
    alternatives = request.args.get('alternatives', 'true')  # Default to 'true'

    if not origin or not destination:
        return jsonify({"error": "Both origin and destination must be provided."}), 400
    
    # Build optional parameters dictionary
    optional_params = {}
    if mode:
        optional_params['mode'] = mode
    if departure_time:
        optional_params['departure_time'] = departure_time
    if avoid:
        optional_params['avoid'] = avoid
    
    # Add alternatives parameter (convert string to boolean for Google Maps API)
    if alternatives:
        optional_params['alternatives'] = 'true' if alternatives.lower() == 'true' else 'false'

    
    # Call the function to get directions
    directions = get_google_maps_directions(origin, destination, **optional_params)
    
    if 'error' in directions:
        return jsonify(directions), 500
    
    return jsonify(directions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)