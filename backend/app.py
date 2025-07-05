from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DATA_PATH = "backend"

def read_json(file):
    with open(os.path.join(DATA_PATH, file), 'r') as f:
        return json.load(f)

def write_json(file, data):
    with open(os.path.join(DATA_PATH, file), 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    users = read_json('users.json')
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username]['password'] == password:
        return jsonify({'success': True, 'username': username})
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/account/<username>', methods=['GET'])
def account(username):
    accounts = read_json('accounts.json')
    if username in accounts:
        return jsonify(accounts[username])
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.json
    from_user = data['from']
    to_user = data['to']
    amount = float(data['amount'])

    accounts = read_json('accounts.json')
    transactions = read_json('transactions.json')

    if from_user not in accounts or to_user not in accounts:
        return jsonify({'error': 'Invalid users'}), 400

    if accounts[from_user]['balance'] < amount:
        return jsonify({'error': 'Insufficient funds'}), 400

    # Update balances
    accounts[from_user]['balance'] -= amount
    accounts[to_user]['balance'] += amount

    # Add transaction
    transactions.append({
        'from': from_user,
        'to': to_user,
        'amount': amount
    })

    write_json('accounts.json', accounts)
    write_json('transactions.json', transactions)

    return jsonify({'success': True})

@app.route('/api/transactions/<username>', methods=['GET'])
def get_transactions(username):
    transactions = read_json('transactions.json')
    user_txns = [txn for txn in transactions if txn['from'] == username or txn['to'] == username]
    return jsonify(user_txns)

if __name__ == '__main__':
    app.run(debug=True)
