from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

USERS_FILE = 'data/users.json'
TRANSACTIONS_FILE = 'data/transactions.json'

# Helper functions
def load_json(file_path):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/transfer')
def transfer_page():
    return render_template('transfer.html')

@app.route('/transactions')
def txn_page():
    return render_template('transactions.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    users = load_json(USERS_FILE)
    user = next((u for u in users if u['username'] == data['username']), None)

    if user and check_password_hash(user['password'], data['password']):
        return jsonify({
            'status': 'success',
            'user': {
                'id': user['id'],
                'name': user['name'],
                'account_no': user['account_no'],
                'balance': user['balance']
            }
        })
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.json
    users = load_json(USERS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)

    from_user = next((u for u in users if u['id'] == data['from_user_id']), None)
    to_user = next((u for u in users if u['account_no'] == data['to_account']), None)

    if not from_user or not to_user:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    if from_user['balance'] < data['amount']:
        return jsonify({'status': 'error', 'message': 'Insufficient balance'}), 400

    from_user['balance'] -= data['amount']
    to_user['balance'] += data['amount']

    transactions.append({
        'user_id': from_user['id'],
        'type': 'debit',
        'amount': -data['amount'],
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    })
    transactions.append({
        'user_id': to_user['id'],
        'type': 'credit',
        'amount': data['amount'],
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    })

    save_json(users, USERS_FILE)
    save_json(transactions, TRANSACTIONS_FILE)

    return jsonify({'status': 'success', 'message': 'Transfer successful'})

@app.route('/api/transactions/<int:user_id>', methods=['GET'])
def get_transactions(user_id):
    transactions = load_json(TRANSACTIONS_FILE)
    user_txns = [t for t in transactions if t['user_id'] == user_id]
    user_txns.sort(key=lambda x: x['date'], reverse=True)
    return jsonify(user_txns)

# Initialize default user if file empty
@app.before_first_request
def setup():
    users = load_json(USERS_FILE)
    if not users:
        users.append({
            'id': 1,
            'username': 'rahul123',
            'password': generate_password_hash('1234'),
            'account_no': 'SB123456',
            'balance': 10000.0,
            'name': 'Rahul'
        })
        save_json(users, USERS_FILE)

    transactions = load_json(TRANSACTIONS_FILE)
    if not transactions:
        save_json([], TRANSACTIONS_FILE)

if __name__ == '__main__':
    app.run(debug=True)
