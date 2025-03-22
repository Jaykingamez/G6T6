from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class SelectedRoute(db.Model):
    __tablename__ = 'SelectedRoute'

    RouteID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    BusStopCode = db.Column(db.Integer, nullable=False)
    BusID = db.Column(db.String(11), nullable=False)
    UserID = db.Column(db.Integer, nullable=False)

    def __init__(self, BusStopCode, BusID, UserID, RouteID=None):
        self.BusStopCode = BusStopCode
        self.BusID = BusID
        self.UserID = UserID
        if RouteID:
            self.RouteID = RouteID

    def json(self):
        return {
            "RouteID": self.RouteID,
            "BusStopCode": self.BusStopCode,
            "BusID": self.BusID,
            "UserID": self.UserID
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

# Create a new selected route
@app.route("/selectedroute", methods=['POST'])
def create_route():
    data = request.get_json()
    route = SelectedRoute(**data)
    
    try:
        db.session.add(route)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred creating the route: {str(e)}"
            }
        ), 500
    
    return jsonify(
        {
            "code": 201,
            "data": route.json()
        }
    ), 201

# Update a selected route
@app.route("/selectedroute/<int:RouteID>", methods=['PUT'])
def update_route(RouteID):
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
        
    data = request.get_json()
    
    if 'BusStopCode' in data:
        route.BusStopCode = data['BusStopCode']
    if 'BusID' in data:
        route.BusID = data['BusID']
    if 'UserID' in data:
        route.UserID = data['UserID']
    
    try:
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": f"An error occurred updating the route: {str(e)}"
            }
        ), 500
    
    return jsonify(
        {
            "code": 200,
            "data": route.json()
        }
    )

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
    app.run(port=5301, debug=True)
