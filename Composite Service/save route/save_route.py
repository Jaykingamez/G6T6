from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json

app = Flask(__name__)
CORS(app)

# Service URLs from environment variables with defaults for local development
USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://localhost:5003/users')
SAVED_ROUTES_SERVICE_URL = os.environ.get('SAVED_ROUTES_SERVICE_URL', 'http://localhost:5002/saved_routes')

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "get-saved-routes-composite"}), 200

# Save a route - triggered when user clicks save button
@app.route("/routes/save", methods=["POST"])
def save_route():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "code": 400,
                "message": "Invalid request: No data provided."
            }), 400
            
        # Validate required fields
        required_fields = ['user_id', 'route_data', 'route_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "code": 400,
                    "message": f"Missing required field: {field}"
                }), 400
        
        # Step 1: Verify user exists
        try:
            user_response = requests.get(f"{USER_SERVICE_URL}/{data['user_id']}")
            user_response.raise_for_status()  # Raise exception for non-2xx responses
            
            user_data = user_response.json()
            if 'code' in user_data and user_data['code'] != 200:
                return jsonify({
                    "code": 404,
                    "message": f"User with ID {data['user_id']} not found."
                }), 404
                
        except requests.exceptions.RequestException as e:
            return jsonify({
                "code": 500,
                "message": f"Error communicating with user service: {str(e)}"
            }), 500
        
        # Step 2: Save the route using the saved_routes microservice
        try:
            save_response = requests.post(
                SAVED_ROUTES_SERVICE_URL,
                json={
                    "user_id": data['user_id'],
                    "route_name": data['route_name'],
                    "route_data": data['route_data']  # Pass Google Maps JSON as is
                }
            )
            save_response.raise_for_status()
            
            # Return the response from the saved_routes service
            return jsonify(save_response.json()), save_response.status_code
            
        except requests.exceptions.RequestException as e:
            return jsonify({
                "code": 500,
                "message": f"Error saving route: {str(e)}"
            }), 500
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# Get user's saved routes with user details - triggered when viewing saved routes
@app.route("/routes/user/<string:user_id>", methods=["GET"])
def get_user_routes(user_id):
    try:
        # Step 1: Get user information
        try:
            user_response = requests.get(f"{USER_SERVICE_URL}/{user_id}")
            
            if user_response.status_code == 404:
                return jsonify({
                    "code": 404,
                    "message": f"User with ID {user_id} not found."
                }), 404
                
            user_response.raise_for_status()
            user_data = user_response.json().get('data', {})
            
        except requests.exceptions.RequestException as e:
            return jsonify({
                "code": 500,
                "message": f"Error retrieving user information: {str(e)}"
            }), 500
        
        # Step 2: Get user's saved routes
        try:
            routes_response = requests.get(f"{SAVED_ROUTES_SERVICE_URL}/user/{user_id}")
            routes_response.raise_for_status()
            routes_data = routes_response.json()
            
            # Combine user and routes data
            result = {
                "code": 200,
                "data": {
                    "user": user_data,
                    "routes": routes_data.get('data', [])
                },
                "count": len(routes_data.get('data', []))
            }
            
            return jsonify(result)
            
        except requests.exceptions.RequestException as e:
            return jsonify({
                "code": 500,
                "message": f"Error retrieving saved routes: {str(e)}"
            }), 500
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# Get details for a specific saved route
@app.route("/routes/<string:route_id>/details", methods=["GET"])
def get_route_details(route_id):
    try:
        # Get route information
        try:
            route_response = requests.get(f"{SAVED_ROUTES_SERVICE_URL}/{route_id}")
            
            if route_response.status_code == 404:
                return jsonify({
                    "code": 404,
                    "message": f"Route with ID {route_id} not found."
                }), 404
                
            route_response.raise_for_status()
            route_data = route_response.json().get('data', {})
            
            # Get associated user information
            user_id = route_data.get('user_id')
            if user_id:
                try:
                    user_response = requests.get(f"{USER_SERVICE_URL}/{user_id}")
                    user_response.raise_for_status()
                    user_data = user_response.json().get('data', {})
                    
                    # Combine route and user data
                    result = {
                        "code": 200,
                        "data": {
                            "route": route_data,
                            "user": user_data
                        }
                    }
                    
                    return jsonify(result)
                    
                except requests.exceptions.RequestException:
                    # If user service fails, still return route data
                    return jsonify({
                        "code": 200,
                        "data": {
                            "route": route_data,
                            "user": {"id": user_id, "error": "Unable to retrieve user details"}
                        }
                    })
            
            # If no user_id in route data
            return jsonify({
                "code": 200,
                "data": {"route": route_data}
            })
            
        except requests.exceptions.RequestException as e:
            return jsonify({
                "code": 500,
                "message": f"Error retrieving route details: {str(e)}"
            }), 500
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

# Delete a saved route
@app.route("/routes/<string:route_id>", methods=["DELETE"])
def delete_route(route_id):
    try:
        # Delete the route using the saved_routes microservice
        try:
            delete_response = requests.delete(f"{SAVED_ROUTES_SERVICE_URL}/{route_id}")
            
            # Return the response from the saved_routes service
            return jsonify(delete_response.json()), delete_response.status_code
            
        except requests.exceptions.RequestException as e:
            return jsonify({
                "code": 500,
                "message": f"Error deleting route: {str(e)}"
            }), 500
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)