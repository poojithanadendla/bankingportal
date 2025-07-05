from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

USERS_FILE = 'users.json'          # Stores users: username, password, profile info
ACCOUNTS_FILE = 'accounts.json'    # Stores accounts: username -> balance
TRANSACTIONS_FILE = 'transactions.json'  # Stores transactions per user

def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# --- Authentication ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    users = load_json(USERS_FILE)
    if username in users and users[username]['password'] == password:
        return jsonify({'message': 'Login successful', 'username': username})
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

# --- CRUD on Users (admin functions) ---

@app.route('/api/users', methods=['GET'])
def get_all_users():
    users = load_json(USERS_FILE)
    # Don't send passwords in response
    safe_users = {u: {k:v for k,v in data.items() if k != 'password'} for u,data in users.items()}
    return jsonify(safe_users)

@app.route('/api/users/<username>', methods=['GET'])
def get_user(username):
    users = load_json(USERS_FILE)
    if username in users:
        data = users[username].copy()
        data.pop('password', None)  # hide password
        return jsonify(data)
    return jsonify({'message': 'User not found'}), 404

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    profile = data.get('profile', {})
    users = load_json(USERS_FILE)
    accounts = load_json(ACCOUNTS_FILE)

    if username in users:
        return jsonify({'message': 'User already exists'}), 400

    users[username] = {'password': password, 'profile': profile}
    accounts[username] = {"balance": 0}
    save_json(USERS_FILE, users)
    save_json(ACCOUNTS_FILE, accounts)
    return jsonify({'message': 'User added'})

@app.route('/api/users/<username>', methods=['PUT'])
def update_user(username):
    data = request.json
    users = load_json(USERS_FILE)
    if username not in users:
        return jsonify({'message': 'User not found'}), 404

    # Update password if provided
    if 'password' in data:
        users[username]['password'] = data['password']
    # Update profile if provided
    if 'profile' in data:
        users[username]['profile'] = data['profile']
    save_json(USERS_FILE, users)
    return jsonify({'message': 'User updated'})

@app.route('/api/users/<username>', methods=['DELETE'])
def delete_user(username):
    users = load_json(USERS_FILE)
    accounts = load_json(ACCOUNTS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)

    if username not in users:
        return jsonify({'message': 'User not found'}), 404

    users.pop(username)
    accounts.pop(username, None)
    transactions.pop(username, None)

    save_json(USERS_FILE, users)
    save_json(ACCOUNTS_FILE, accounts)
    save_json(TRANSACTIONS_FILE, transactions)

    return jsonify({'message': 'User deleted'})

# --- Account info ---

@app.route('/api/account/<username>', methods=['GET'])
def get_account(username):
    accounts = load_json(ACCOUNTS_FILE)
    users = load_json(USERS_FILE)
    if username in accounts and username in users:
        account = accounts[username].copy()
        account['profile'] = users[username].get('profile', {})
        return jsonify(account)
    else:
        return jsonify({'message': 'Account not found'}), 404

# --- Fund transfer ---

@app.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.json
    from_user = data.get('from_user')
    to_user = data.get('to_user')
    amount = float(data.get('amount'))

    accounts = load_json(ACCOUNTS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)

    if from_user not in accounts or to_user not in accounts:
        return jsonify({'message': 'Invalid user(s)'}), 400

    if accounts[from_user]['balance'] < amount:
        return jsonify({'message': 'Insufficient balance'}), 400

    accounts[from_user]['balance'] -= amount
    accounts[to_user]['balance'] += amount

    # Record transaction for both users
    transactions.setdefault(from_user, []).append({'type': 'debit', 'amount': amount, 'to': to_user})
    transactions.setdefault(to_user, []).append({'type': 'credit', 'amount': amount, 'from': from_user})

    save_json(ACCOUNTS_FILE, accounts)
    save_json(TRANSACTIONS_FILE, transactions)

    return jsonify({'message': 'Transfer successful'})

# --- Transaction history ---

@app.route('/api/transactions/<username>', methods=['GET'])
def get_transactions(username):
    transactions = load_json(TRANSACTIONS_FILE)
    return jsonify(transactions.get(username, []))

if __name__ == '__main__':
    app.run(debug=True)
