from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Load data files
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

USERS_FILE = 'users.json'
ACCOUNTS_FILE = 'accounts.json'
TRANSACTIONS_FILE = 'transactions.json'

# Sample login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    users = load_data(USERS_FILE)
    user = users.get(username)

    if user and user['password'] == password:
        return jsonify({"success": True, "message": "Login successful", "user": user}), 200
    else:
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

# Get account details
@app.route('/api/accounts/<username>', methods=['GET'])
def get_account(username):
    accounts = load_data(ACCOUNTS_FILE)
    account = accounts.get(username)
    if account:
        return jsonify(account), 200
    else:
        return jsonify({"error": "Account not found"}), 404

# Transfer funds
@app.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.json
    from_user = data.get('from')
    to_user = data.get('to')
    amount = float(data.get('amount', 0))

    if amount <= 0:
        return jsonify({"error": "Invalid transfer amount"}), 400

    accounts = load_data(ACCOUNTS_FILE)

    from_account = accounts.get(from_user)
    to_account = accounts.get(to_user)

    if not from_account or not to_account:
        return jsonify({"error": "Invalid account(s)"}), 404

    if from_account['balance'] < amount:
        return jsonify({"error": "Insufficient funds"}), 400

    from_account['balance'] -= amount
    to_account['balance'] += amount

    accounts[from_user] = from_account
    accounts[to_user] = to_account

    save_data(ACCOUNTS_FILE, accounts)

    # Save transaction record
    transactions = load_data(TRANSACTIONS_FILE)
    transactions.setdefault(from_user, []).append({
        "type": "debit",
        "amount": amount,
        "to": to_user
    })
    transactions.setdefault(to_user, []).append({
        "type": "credit",
        "amount": amount,
        "from": from_user
    })
    save_data(TRANSACTIONS_FILE, transactions)

    return jsonify({"success": True, "message": "Transfer completed"}), 200

# Get transaction history for user
@app.route('/api/transactions/<username>', methods=['GET'])
def transactions(username):
    transactions = load_data(TRANSACTIONS_FILE)
    user_transactions = transactions.get(username, [])
    return jsonify(user_transactions), 200


if __name__ == '__main__':
    app.run(debug=True)
