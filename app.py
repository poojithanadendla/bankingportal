from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'super_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    account_no = db.Column(db.String(20), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    name = db.Column(db.String(100), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(20))
    amount = db.Column(db.Float)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({
            'status': 'success',
            'user': {
                'id': user.id,
                'name': user.name,
                'account_no': user.account_no,
                'balance': user.balance
            }
        })
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'name': user.name,
            'account_no': user.account_no,
            'balance': user.balance
        })
    return jsonify({'message': 'User not found'}), 404

@app.route('/api/transfer', methods=['POST'])
def transfer():
    data = request.json
    from_user = User.query.get(data['from_user_id'])
    to_user = User.query.filter_by(account_no=data['to_account']).first()

    if not to_user:
        return jsonify({'status': 'error', 'message': 'Recipient not found'}), 404
    if from_user.balance < data['amount']:
        return jsonify({'status': 'error', 'message': 'Insufficient balance'}), 400

    from_user.balance -= data['amount']
    to_user.balance += data['amount']
    db.session.add(Transaction(user_id=from_user.id, type='transfer', amount=-data['amount']))
    db.session.add(Transaction(user_id=to_user.id, type='transfer', amount=data['amount']))
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Transfer successful'})

@app.route('/api/transactions/<int:user_id>', methods=['GET'])
def get_transactions(user_id):
    txns = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    return jsonify([
        {
            'date': t.date.strftime('%Y-%m-%d %H:%M'),
            'type': t.type,
            'amount': t.amount
        } for t in txns
    ])

@app.before_first_request
def init_db():
    db.create_all()
    # Add a default user if none exists (for testing)
    if not User.query.filter_by(username='rahul123').first():
        hashed_pw = generate_password_hash('1234')
        user = User(username='rahul123', password=hashed_pw, account_no='SB123456', balance=10000.0, name='Rahul')
        db.session.add(user)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
