from flask import Flask, jsonify, request, send_from_directory, abort
import json
import os

app = Flask(__name__)

# Paths to JSON data files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
ACCOUNTS_FILE = os.path.join(BASE_DIR, 'accounts.json')
TRANSACTIONS_FILE = os.path.join(BASE_DIR, 'transactions.json')

# Utility functions to load and save JSON data
def load_data(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# Serve frontend index.html at root
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

# Serve other frontend static files (css, js)
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)

# Example API: Get all users
@app.route('/api/users', methods=['GET'])
def get_users():
    users = load_data(USERS_FILE)
    return jsonify(users)

# Example API: Create a new user
@app.route('/api/users', methods=['POST'])
def create_user():
    users = load_data(USERS_FILE)
    new_user = request.json
    users.append(new_user)
    save_data(USERS_FILE, users)
    return jsonify(new_user), 201

# Example API: Get account details by account id
@app.route('/api/accounts/<account_id>', methods=['GET'])
def get_account(account_id):
    accounts = load_data(ACCOUNTS_FILE)
    account = next((acc for acc in accounts if acc['id'] == account_id), None)
    if account:
        return jsonify(account)
    else:
        abort(404, description="Account not found")

# Example API: Get transactions for account
@app.route('/api/accounts/<account_id>/transactions', methods=['GET'])
def get_transactions(account_id):
    transactions = load_data(TRANSACTIONS_FILE)
    filtered = [t for t in transactions if t['account_id'] == account_id]
    return jsonify(filtered)

# Example API: Fund transfer (simplified)
@app.route('/api/transfer', methods=['POST'])
def transfer_funds():
    data = request.json
    from_acc_id = data.get('from_account')
    to_acc_id = data.get('to_account')
    amount = float(data.get('amount', 0))

    accounts = load_data(ACCOUNTS_FILE)
    transactions = load_data(TRANSACTIONS_FILE)

    from_acc = next((acc for acc in accounts if acc['id'] == from_acc_id), None)
    to_acc = next((acc for acc in accounts if acc['id'] == to_acc_id), None)

    if not from_acc or not to_acc:
        abort(404, description="Account not found")
    if from_acc['balance'] < amount:
        abort(400, description="Insufficient funds")

    from_acc['balance'] -= amount
    to_acc['balance'] += amount

    # Log transactions
    transactions.append({
        "id": str(len(transactions) + 1),
        "account_id": from_acc_id,
        "type": "debit",
        "amount": amount,
        "description": f"Transfer to {to_acc_id}"
    })
    transactions.append({
        "id": str(len(transactions) + 1),
        "account_id": to_acc_id,
        "type": "credit",
        "amount": amount,
        "description": f"Transfer from {from_acc_id}"
    })

    save_data(ACCOUNTS_FILE, accounts)
    save_data(TRANSACTIONS_FILE, transactions)

    return jsonify({"message": "Transfer successful"})

if __name__ == '__main__':
    app.run(debug=True)
