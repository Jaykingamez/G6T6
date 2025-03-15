#!/usr/bin/env python3

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simulated user data
users = [
    {"id": 1, "name": "John Doe", "email": "john@example.com"},
    {"id": 2, "name": "Jane Doe", "email": "jane@example.com"}
]

# CREATE
@app.route("/users", methods=['POST'])
def createUser():
    if request.is_json:
        user = request.get_json()
        result = processCreateUser(user)
        return jsonify(result), result["code"]
    else:
        data = request.get_data()
        print("Received an invalid user:")
        print(data)
        return jsonify({"code": 400,
                        "data": str(data),
                        "message": "User should be in JSON."}), 400

# READ
@app.route("/users", methods=['GET'])
def getUsers():
    return jsonify(users), 200

# UPDATE
@app.route("/users/<int:user_id>", methods=['PUT'])
def updateUser(user_id):
    if request.is_json:
        user = request.get_json()
        result = processUpdateUser(user_id, user)
        return jsonify(result), result["code"]
    else:
        data = request.get_data()
        print("Received an invalid user update:")
        print(data)
        return jsonify({"code": 400,
                        "data": str(data),
                        "message": "User update should be in JSON."}), 400

# DELETE
@app.route("/users/<int:user_id>", methods=['DELETE'])
def deleteUser(user_id):
    result = processDeleteUser(user_id)
    return jsonify(result), result["code"]


def processCreateUser(user):
    print("Creating a new user:")
    print(user)
    # Simulate success
    code = 201
    message = 'Simulated success in user creation.'
    users.append(user)
    return {
        'code': code,
        'data': user,
        'message': message
    }

def processUpdateUser(user_id, user):
    print("Updating a user:")
    print(user)
    # Find the user to update
    for u in users:
        if u['id'] == user_id:
            u['name'] = user['name']
            u['email'] = user['email']
            code = 200
            message = 'Simulated success in user update.'
            return {
                'code': code,
                'data': u,
                'message': message
            }
    code = 404
    message = 'User not found.'
    return {
        'code': code,
        'data': None,
        'message': message
    }

def processDeleteUser(user_id):
    print("Deleting a user:")
    print(user_id)
    # Find the user to delete
    for u in users:
        if u['id'] == user_id:
            users.remove(u)
            code = 200
            message = 'Simulated success in user deletion.'
            return {
                'code': code,
                'data': None,
                'message': message
            }
    code = 404
    message = 'User not found.'
    return {
        'code': code,
        'data': None,
        'message': message
    }

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          ": user management ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
