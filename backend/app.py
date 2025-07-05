from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'customers.json'

# Load data from the JSON file
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Save data to the JSON file
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Home route to serve the HTML page
@app.route('/')
def index():
    return open('index.html').read()

# API endpoint to get all customers
@app.route('/api/customers', methods=['GET'])
def get_customers():
    return jsonify(load_data())

# API endpoint to add a new customer
@app.route('/api/customers', methods=['POST'])
def add_customer():
    customer = request.json
    data = load_data()
    customer['id'] = len(data) + 1  # Simple auto-increment ID
    data.append(customer)
    save_data(data)
    return jsonify({'message': 'Customer added'}), 201

# API endpoint to update an existing customer
@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    updated_data = request.json
    data = load_data()
    for customer in data:
        if customer['id'] == customer_id:
            customer.update(updated_data)
            save_data(data)
            return jsonify({'message': 'Customer updated'})
    return jsonify({'message': 'Customer not found'}), 404

# API endpoint to delete a customer
@app.route('/api/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    data = load_data()
    data = [customer for customer in data if customer['id'] != customer_id]
    save_data(data)
    return jsonify({'message': 'Customer deleted'})

if __name__ == '__main__':
    app.run(debug=True)
