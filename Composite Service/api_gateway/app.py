from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
from flask_cors import CORS
import requests

# URLs for the microservices
BUS_STOP_LOOKUP_URL = "http://bus_stop_lookup:5002"  # Use the service name
DIRECTIONS_URL = "http://directions:5001"  # Use the service name

# Swagger configuration for the composite service
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
    "specs_route": "/apidocs/",
}

template = {
    "swagger": "2.0",
    "info": {
        "title": "Composite API Gateway",
        "description": "Combined API documentation for Bus Stop Lookup and Directions services",
        "version": "1.0",
        "contact": {
            "email": "support@example.com"
        }
    },
    "host": "localhost:5000",  # Port for the composite service
    "basePath": "/",
    "schemes": ["http"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "paths": {}  # Will be populated dynamically
}

# Initialize Flask app
app = Flask(__name__)
CORS(app)
swagger = Swagger(app, config=swagger_config, template=template)

@app.route("/")
def home():
    return "<h1>Welcome to the Composite API Gateway. Visit <a href='/apidocs'>/apidocs</a> for API documentation.</h1>"

@app.route("/bus_stop_lookup", methods=["POST"])
def bus_stop_lookup_proxy():
    """
    Proxy for the Bus Stop Lookup microservice
    ---
    tags:
      - Bus Stop Lookup
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            routes:
              type: array
              items:
                type: object
    responses:
      200:
        description: Transit details with nearest bus stop information
    """
    try:
        response = requests.post(f"{BUS_STOP_LOOKUP_URL}/bus_stop_lookup", json=request.json)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route("/directions", methods=["GET"])
def directions_proxy():
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
    try:
        response = requests.get(f"{DIRECTIONS_URL}/directions", params=request.args)
        response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)