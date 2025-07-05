from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# File to store customer data
CUSTOMERS_FILE = 'customers.json'

# Load customer data from customers.json
def load_customers():
    if os.path.exists(CUSTOMERS_FILE):
        with open(CUSTOMERS_FILE, 'r') as file:
            return json.load(file)
    return []

# Save customer data to customers.json
def save_customers(customers):
    with open(CUSTOMERS_FILE, 'w') as file:
        json.dump(customers, file, indent=4)

# API endpoint to get all customers
@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = load_customers()
    return jsonify(customers)

# API endpoint to add a new customer
@app.route('/api/customers', methods=['POST'])
def add_customer():
    new_customer = request.get_json()
    customers = load_customers()
    new_customer['id'] = len(customers) + 1  # Simple auto-increment ID
    customers.append(new_customer)
    save_customers(customers)
    return jsonify(new_customer), 201

# API endpoint to update a customer
@app.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    updated_data = request.get_json()
    customers = load_customers()
    for customer in customers:
        if customer['id'] == id:
            customer.update(updated_data)
            save_customers(customers)
            return jsonify(customer)
    return jsonify({"error": "Customer not found"}), 404

# API endpoint to delete a customer
@app.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    customers = load_customers()
    customers = [customer for customer in customers if customer['id'] != id]
    save_customers(customers)
    return '', 204

# Serving the index.html template
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
