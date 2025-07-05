from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

def load_json(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/login', methods=['POST'])
def login():
    creds = request.json
    users = load_json('backend/users.json')
    for user in users:
        if user['username'] == creds['username'] and user['password'] == creds['password']:
            return jsonify({"message": "success", "user": {"id": user['id'], "name": user['name'], "username": user['username']}})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/customers', methods=['GET', 'POST'])
def customers():
    filename = 'backend/customers.json'
    if request.method == 'GET':
        return jsonify(load_json(filename))
    elif request.method == 'POST':
        data = load_json(filename)
        new_customer = request.json
        new_customer['id'] = len(data) + 1
        data.append(new_customer)
        save_json(filename, data)
        return jsonify({"message": "Customer added"}), 201

@app.route('/api/customers/<int:cid>', methods=['PUT', 'DELETE'])
def customer_modify(cid):
    filename = 'backend/customers.json'
    data = load_json(filename)
    customer = next((c for c in data if c['id'] == cid), None)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    if request.method == 'PUT':
        update = request.json
        customer.update(update)
        save_json(filename, data)
        return jsonify({"message": "Customer updated"})
    elif request.method == 'DELETE':
        data = [c for c in data if c['id'] != cid]
        save_json(filename, data)
        return jsonify({"message": "Customer deleted"})

if __name__ == '__main__':
    app.run(debug=True)
