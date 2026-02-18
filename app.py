from flask import Flask, jsonify, request, session, g
from database import init_db, db_session
from models import User, Transaction, Category
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key' # Replace with a strong secret key
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True # Use for production over HTTPS

init_db()

# Custom decorator for authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if user_id is None:
            return jsonify({'message': 'Unauthorized'}), 401
        g.user = db_session.query(User).filter_by(id=user_id).first()
        if g.user is None:
            return jsonify({'message': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/register', methods=['POST'])
def register():
    # Only allow one user for simplicity for now
    if db_session.query(User).count() > 0:
        return jsonify({'message': 'User already registered'}), 400

    data = request.get_json()
    pin = data.get('pin')

    if not pin or not pin.isdigit() or len(pin) != 4:
        return jsonify({'message': 'Invalid PIN. Must be a 4-digit number.'}), 400

    new_user = User(pin)
    db_session.add(new_user)
    db_session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    pin = data.get('pin')

    user = db_session.query(User).first() # Assuming a single user for now

    if user and user.check_pin(pin):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid PIN'}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/')
@login_required
def index():
    return "ExpenseTrack Pro Backend - Authenticated"

if __name__ == '__main__':
    app.run(debug=True)
