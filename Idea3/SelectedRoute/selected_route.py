from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from dotenv import load_dotenv
from flask_cors import CORS  # Add this import

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://is213@host.docker.internal:3306/selectedroute"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class SelectedRoute(db.Model):
    __tablename__ = 'SelectedRoute'

    RouteID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    BusStopCode = db.Column(db.Integer, nullable=False)
    BusID = db.Column(db.String(11), nullable=False)
    UserID = db.Column(db.Integer, nullable=False)
    RouteName = db.Column(db.String(30), nullable=False)

    def __init__(self, BusStopCode, BusID, UserID, RouteName, RouteID=None):
        self.BusStopCode = BusStopCode
        self.BusID = BusID
        self.UserID = UserID
        self.RouteName = RouteName
        if RouteID:
            self.RouteID = RouteID

    def json(self):
        return {
            "RouteID": self.RouteID,
            "BusStopCode": self.BusStopCode,
            "BusID": self.BusID,
            "UserID": self.UserID,
            "RouteName": self.RouteName
        }

# Get all selected routes
@app.route("/selectedroute")
def get_all():
    routelist = db.session.scalars(db.select(SelectedRoute)).all()
    if len(routelist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "routes": [route.json() for route in routelist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no selected routes."
        }
    ), 404

# Get selected route by RouteID
@app.route("/selectedroute/<int:RouteID>")
def find_by_routeid(RouteID):
    route = db.session.scalar(
        db.select(SelectedRoute).filter_by(RouteID=RouteID)
    )
    if route:
        return jsonify(
            {
                "code": 200,
                "data": route.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Route not found."
        }
    ), 404

# Get all routes for a specific user
@app.route("/selectedroute/user/<int:UserID>")
def find_by_userid(UserID):
    routelist = db.session.scalars(
        db.select(SelectedRoute).filter_by(UserID=UserID)
    ).all()
    
    if len(routelist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "routes": [route.json() for route in routelist],
                    "count": len(routelist)
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": f"No routes found for UserID {UserID}."
        }
    ), 404

# Get all routes by RouteName
@app.route("/selectedroute/route/<string:RouteName>")
def find_by_routename(RouteName):
    routelist = db.session.scalars(
        db.select(SelectedRoute).filter_by(RouteName=RouteName)
    ).all()
    
    if len(routelist):
        return jsonify({
            "code": 200,
            "data": {
                "routes": [route.json() for route in routelist],
                "count": len(routelist)
            }
        })
    return jsonify({
        "code": 404,
        "message": f"No routes found with name {RouteName}."
    }), 404

# Create a new selected route
@app.route("/selectedroute", methods=['POST'])
def create_route():
    data = request.get_json()
    
    # Check if required fields are present
    required_fields = ['BusStopCode', 'BusID', 'UserID', 'RouteName']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "code": 400,
                "message": f"Missing required field: {field}"
            }), 400
    
    route = SelectedRoute(**data)
    
    try:
        db.session.add(route)
        db.session.commit()
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred creating the route: {str(e)}"
        }), 500
    
    return jsonify({
        "code": 201,
        "data": route.json()
    }), 201

# Update a selected route
@app.route("/selectedroute/<int:RouteID>", methods=['PUT'])
def update_route(RouteID):
    route = db.session.scalar(
        db.select(SelectedRoute).filter_by(RouteID=RouteID)
    )
    
    if not route:
        return jsonify({
            "code": 404,
            "message": "Route not found."
        }), 404
        
    data = request.get_json()
    
    if 'BusStopCode' in data:
        route.BusStopCode = data['BusStopCode']
    if 'BusID' in data:
        route.BusID = data['BusID']
    if 'UserID' in data:
        route.UserID = data['UserID']
    if 'RouteName' in data:
        route.RouteName = data['RouteName']
    
    try:
        db.session.commit()
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred updating the route: {str(e)}"
        }), 500
    
    return jsonify({
        "code": 200,
        "data": route.json()
    })

# Delete a selected route
@app.route("/selectedroute/<int:RouteID>", methods=['DELETE'])
def delete_route(RouteID):
    route = db.session.scalar(
        db.select(SelectedRoute).filter_by(RouteID=RouteID)
    )
    
    if not route:
        return jsonify(
            {
                "code": 404,
                "message": "Route not found."
            }
        ), 404
    
    try:
        db.session.delete(route)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred deleting the route: {str(e)}"
            }
        ), 500
    
    return jsonify(
        {
            "code": 200,
            "message": f"Route {RouteID} deleted successfully"
        }
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5301, debug=True)

