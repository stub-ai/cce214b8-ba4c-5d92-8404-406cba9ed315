from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Change this!

db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __init__(self, name):
        self.name = name

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class RoleSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')

role_schema = RoleSchema()
roles_schema = RoleSchema(many=True)

@app.route('/api/users', methods=['POST'])
def add_user():
    username = request.json['username']
    password = request.json['password']
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

@app.route('/api/users', methods=['GET'])
def get_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result)

@app.route('/api/users/<id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

@app.route('/api/users/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    username = request.json['username']
    password = request.json['password']
    user.username = username
    user.password = generate_password_hash(password)
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/api/users/<id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)

@app.route('/api/roles', methods=['POST'])
def add_role():
    name = request.json['name']
    new_role = Role(name)
    db.session.add(new_role)
    db.session.commit()
    return role_schema.jsonify(new_role)

@app.route('/api/roles', methods=['GET'])
def get_roles():
    all_roles = Role.query.all()
    result = roles_schema.dump(all_roles)
    return jsonify(result)

@app.route('/api/roles/<id>', methods=['GET'])
def get_role(id):
    role = Role.query.get(id)
    return role_schema.jsonify(role)

@app.route('/api/roles/<id>', methods=['PUT'])
def update_role(id):
    role = Role.query.get(id)
    name = request.json['name']
    role.name = name
    db.session.commit()
    return role_schema.jsonify(role)

@app.route('/api/roles/<id>', methods=['DELETE'])
def delete_role(id):
    role = Role.query.get(id)
    db.session.delete(role)
    db.session.commit()
    return role_schema.jsonify(role)

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    else:
        return jsonify({"msg": "Bad username or password"}), 401

if __name__ == '__main__':
    app.run(debug=True)