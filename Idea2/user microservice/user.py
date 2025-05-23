#!/usr/bin/env python3

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ
import os
import logging
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

CORS(app)

# Update the database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    environ.get("dbURL") or "mysql+mysqlconnector://is213@localhost:3306/users"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    __tablename__ = 'users'
    UserId = db.Column(db.Integer, primary_key=True)
    FullName = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    Password = db.Column(db.String(255), nullable=False)
    Phone = db.Column(db.String(20), unique=True)  # Made nullable since it's not required for authentication
    CreatedAt = db.Column(db.TIMESTAMP, server_default=db.func.now())
    UpdatedAt = db.Column(db.TIMESTAMP, server_default=db.func.now(), onupdate=db.func.now())

    def serialize(self):
        return {
            'UserId': self.UserId,
            'FullName': self.FullName,
            'Email': self.Email,
            'Phone': self.Phone,
            'CreatedAt': self.CreatedAt.isoformat(),
            'UpdatedAt': self.UpdatedAt.isoformat()
        }

    def check_password(self, password):
        return check_password_hash(self.Password, password)

# CREATE
@app.route("/users", methods=['POST'])
def createUser():
    if request.is_json:
        data = request.get_json()
        # Debug log the received data
        logger.debug(f"Received data for user creation: {data}")
        result = processCreateUser(data)
        return jsonify(result), result["code"]
    else:
        return jsonify({"code": 400, "message": "User should be in JSON."}), 400

# READ
@app.route("/users", methods=['GET'])
def getUsers():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route("/users/<int:user_id>", methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            return jsonify({
                "code": 200,
                "data": user.serialize(),
                "message": "User found"
            }), 200
        return jsonify({
            "code": 404,
            "data": None,
            "message": "User not found"
        }), 404
    except Exception as e:
        return jsonify({
            "code": 500,
            "data": None,
            "message": str(e)
        }), 500

# UPDATE
@app.route("/users/<int:user_id>", methods=['PUT'])
def updateUser(user_id):
    if request.is_json:
        data = request.get_json()
        result = processUpdateUser(user_id, data)
        return jsonify(result), result["code"]
    else:
        return jsonify({"code": 400, "message": "User update should be in JSON."}), 400

# DELETE
@app.route("/users/<int:user_id>", methods=['DELETE'])
def deleteUser(user_id):
    result = processDeleteUser(user_id)
    return jsonify(result), result["code"]

# Authentication
@app.route("/authenticate", methods=['POST'])
def authenticate():
    if not request.is_json:
        return jsonify({"code": 400, "message": "Authentication data should be in JSON."}), 400

    data = request.get_json()
    if not all(k in data for k in ["FullName", "Password"]):
        return jsonify({"code": 400, "message": "Both FullName and Password are required."}), 400

    try:
        user = User.query.filter_by(FullName=data['FullName']).first()
        if user and user.check_password(data['Password']):
            return jsonify({
                "code": 200,
                "data": user.serialize(),
                "message": "Authentication successful"
            }), 200
        else:
            return jsonify({
                "code": 401,
                "message": "Invalid credentials"
            }), 401
    except Exception as e:
        return jsonify({
            "code": 500,
            "message": str(e)
        }), 500

def processCreateUser(data):
    try:
        # Debug logging
        logger.debug(f"Processing user creation with data: {data}")
        
        # Validate required fields
        required_fields = ['FullName', 'Email', 'Password']
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing field: {field}")
                return {
                    'code': 400,
                    'data': None,
                    'message': f'Missing required field: {field}'
                }

        # Create new user with explicit fields
        new_user = User(
            FullName=data['FullName'],
            Email=data['Email'],
            Password=generate_password_hash(data['Password']),
            Phone=data.get('Phone')  # Optional field
        )
        
        # Add and commit to database
        db.session.add(new_user)
        db.session.commit()
        logger.debug("User created successfully")
        
        return {
            'code': 201,
            'data': new_user.serialize(),
            'message': 'User created successfully.'
        }
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.session.rollback()
        return {
            'code': 500,
            'data': None,
            'message': str(e)
        }

def processUpdateUser(user_id, data):
    try:
        # Debug logging
        print(f"Updating user {user_id} with data: {data}")
        
        user = User.query.get(user_id)
        if not user:
            return {
                'code': 404,
                'data': None,
                'message': f'User {user_id} not found.'
            }

        # Update only the provided fields
        if 'FullName' in data:
            user.FullName = data['FullName']
        if 'Email' in data:
            user.Email = data['Email']
        if 'Password' in data:
            user.Password = generate_password_hash(data['Password'])
        if 'Phone' in data:
            user.Phone = data['Phone']

        db.session.commit()
        
        return {
            'code': 200,
            'data': user.serialize(),
            'message': 'User updated successfully.'
        }

    except Exception as e:
        print(f"Error updating user: {str(e)}")
        db.session.rollback()
        return {
            'code': 500,
            'data': None,
            'message': str(e)
        }

def processDeleteUser(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return {
                'code': 200, 
                'data': None,
                'message': 'User deleted successfully.'
            }
        return {
            'code': 404,
            'data': None,
            'message': 'User not found.'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'code': 500,
            'data': None,
            'message': str(e)
        }

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    print("This is flask " + os.path.basename(__file__) + ": user management ...")
    app.run(host='0.0.0.0', port=5201, debug=True)
