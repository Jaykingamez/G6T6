from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os
import uuid
import requests

app = Flask(__name__)
CORS(app)

# MongoDB configuration
mongodb_host = os.environ.get('MONGODB_HOST', 'localhost')
mongodb_port = int(os.environ.get('MONGODB_PORT', '27017'))
mongodb_name = os.environ.get('MONGODB_NAME', 'journey_planning')
mongodb_collection = os.environ.get('MONGODB_COLLECTION', 'saved_routes')

# Connect to MongoDB
try:
    client = MongoClient(host=mongodb_host, port=mongodb_port, serverSelectionTimeoutMS=5000)
    db = client[mongodb_name]
    routes_collection = db[mongodb_collection]
    client.server_info()  # Force connection check
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

# # Create an index on user_id for faster queries
# routes_collection.create_index("user_id")

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "saved-routes-atomic"}), 200

# Save a route
@app.route("/saved_routes", methods=["POST"])
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
                
        # Create a new route document
        route_document = {
            "id": str(uuid.uuid4()),
            "user_id": data['user_id'],
            "route_name": data['route_name'],
            "route_data": data['route_data'],  # Store the Google Maps JSON data as is
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Insert into MongoDB
        result = routes_collection.insert_one(route_document)
        
        if result.inserted_id:
            route_document['_id'] = str(result.inserted_id)
            
            return jsonify({
                "code": 201,
                "message": "Route saved successfully",
                "data": route_document
            }), 201
        
        return jsonify({
            "code": 500,
            "message": "Failed to save route."
        }), 500
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred saving the route: {str(e)}"
        }), 500

# Get routes by user ID
@app.route("/saved_routes/user/<string:user_id>", methods=["GET"])
def get_routes_by_user(user_id):
    try:
        routes = list(routes_collection.find({"user_id": user_id}))
        
        # Convert ObjectId to string for JSON serialization
        for route in routes:
            if '_id' in route:
                route['_id'] = str(route['_id'])
                
        if routes:
            return jsonify({
                "code": 200,
                "data": routes,
                "count": len(routes)
            })
        return jsonify({
            "code": 200,
            "message": f"No saved routes found for user ID {user_id}",
            "data": []
        }), 200
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred retrieving routes: {str(e)}"
        }), 500

# Get route by ID
@app.route("/saved_routes/<string:route_id>", methods=["GET"])
def get_route_by_id(route_id):
    try:
        route = routes_collection.find_one({"id": route_id})
        
        if route:
            # Convert ObjectId to string for JSON serialization
            if '_id' in route:
                route['_id'] = str(route['_id'])
                
            return jsonify({
                "code": 200,
                "data": route
            })
        return jsonify({
            "code": 404,
            "message": f"Route with ID {route_id} not found."
        }), 404
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred retrieving the route: {str(e)}"
        }), 500

# Delete route
@app.route("/saved_routes/<string:route_id>", methods=["DELETE"])
def delete_route(route_id):
    try:
        # Check if route exists
        existing_route = routes_collection.find_one({"id": route_id})
        
        if not existing_route:
            return jsonify({
                "code": 404,
                "message": f"Route with ID {route_id} not found."
            }), 404
            
        # Delete from MongoDB
        result = routes_collection.delete_one({"id": route_id})
        
        if result.deleted_count:
            return jsonify({
                "code": 200,
                "message": f"Route with ID {route_id} deleted successfully."
            })
            
        return jsonify({
            "code": 500,
            "message": "Failed to delete route."
        }), 500
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred deleting the route: {str(e)}"
        }), 500

# Update route name
@app.route("/saved_routes/<string:route_id>", methods=["PUT"])
def update_route(route_id):
    try:
        data = request.get_json()
        
        if not data or 'route_name' not in data:
            return jsonify({
                "code": 400,
                "message": "Invalid request: No route_name provided."
            }), 400
            
        # Check if route exists
        existing_route = routes_collection.find_one({"id": route_id})
        
        if not existing_route:
            return jsonify({
                "code": 404,
                "message": f"Route with ID {route_id} not found."
            }), 404
            
        # Update in MongoDB
        result = routes_collection.update_one(
            {"id": route_id},
            {"$set": {
                "route_name": data['route_name'],
                "updated_at": datetime.now()
            }}
        )
        
        if result.modified_count:
            updated_route = routes_collection.find_one({"id": route_id})
            if '_id' in updated_route:
                updated_route['_id'] = str(updated_route['_id'])
                
            return jsonify({
                "code": 200,
                "message": "Route updated successfully",
                "data": updated_route
            })
            
        return jsonify({
            "code": 200,
            "message": "No changes made to the route."
        })
    
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred updating the route: {str(e)}"
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5006, debug=True)