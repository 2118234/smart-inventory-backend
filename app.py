from flask_cors import CORS
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Initialize the Flask app
app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# Configurations
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['JWT_SECRET_KEY'] = 'your-jwt-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from datetime import timedelta

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)


# Initialize extensions
jwt = JWTManager(app)
db = SQLAlchemy(app)

# -------------------------- MODELS --------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Create the database tables (only once at the beginning)
with app.app_context():
    db.create_all()

# -------------------------- ROUTES --------------------------

# Register route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists!"}), 400

    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": f"User {username} registered successfully!"}), 201

# Login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message="Invalid credentials"), 401

# Protected route
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify(message=f"Welcome, user {current_user_id}! This is a protected route.")

# Add a product
@app.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        quantity=data['quantity'],
        price=data['price']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added successfully!"}), 201

# Get all products
@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    products = Product.query.all()
    result = [
        {"id": p.id, "name": p.name, "quantity": p.quantity, "price": p.price}
        for p in products
    ]
    return jsonify(result), 200

# Update a product
@app.route('/products/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    data = request.get_json()
    product.name = data.get('name', product.name)
    product.quantity = data.get('quantity', product.quantity)
    product.price = data.get('price', product.price)

    db.session.commit()
    return jsonify({"message": "Product updated successfully!"}), 200

# Delete a product
@app.route('/products/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully!"}), 200

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
