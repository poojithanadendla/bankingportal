from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# Initialize the Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banking_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Define the User and Account models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    accounts = db.relationship('Account', backref='owner', lazy=True)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Create the database
@app.before_first_request
def create_tables():
    db.create_all()

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully!"}), 201

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Login successful!"}), 200
    return jsonify({"message": "Invalid credentials!"}), 401

# Route to view account details
@app.route('/account/<user_id>', methods=['GET'])
def view_account(user_id):
    user = User.query.get_or_404(user_id)
    accounts = Account.query.filter_by(user_id=user.id).all()
    
    account_details = []
    for account in accounts:
        account_details.append({
            'account_number': account.account_number,
            'balance': account.balance
        })
    
    return jsonify({"accounts": account_details})

# Route for fund transfer
@app.route('/transfer', methods=['POST'])
def transfer_funds():
    data = request.get_json()
    sender_account = data.get('sender_account')
    receiver_account = data.get('receiver_account')
    amount = data.get('amount')

    sender = Account.query.filter_by(account_number=sender_account).first()
    receiver = Account.query.filter_by(account_number=receiver_account).first()

    if sender and receiver and sender.balance >= amount:
        sender.balance -= amount
        receiver.balance += amount
        db.session.commit()
        return jsonify({"message": "Transfer successful!"}), 200
    return jsonify({"message": "Transfer failed. Check account details or balance."}), 400

# Route to view transaction history (for simplicity, this example just shows account balance change)
@app.route('/transaction_history/<user_id>', methods=['GET'])
def transaction_history(user_id):
    user = User.query.get_or_404(user_id)
    accounts = Account.query.filter_by(user_id=user.id).all()
    
    history = []
    for account in accounts:
        history.append({
            'account_number': account.account_number,
            'balance': account.balance
        })
    
    return jsonify({"transaction_history": history})

if __name__ == '__main__':
    app.run(debug=True)
