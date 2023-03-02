from flask import Blueprint, request
from flask.json import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from src.model import User, db
from src.constants.http_status_codes import *
import validators

users = Blueprint("users", __name__, url_prefix="/api/v1/users")


@users.get('me')
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        'username': user.username,
        'email': user.email,
        'create at': user.created_at
    }), HTTP_200_OK
    
@users.route('/', methods=['POST'])
@jwt_required()
def insert():
    current_user = get_jwt_identity()
    new_user = request.json['new_user']
    
    username = new_user['username']
    email = new_user['email']
    password = new_user['password']
    
    if len(password)<3:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST
    
    if User.query.filter_by(username=username,).first() is not None:
        return jsonify({'error': "username is taken"}), HTTP_409_CONFLICT
    
    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT
    pwd_hash = generate_password_hash(password)
    
    user = User(username=username, password=pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        'message': "User created",
        'user': {
            'username': username, 'email':email
        }
    }), HTTP_201_CREATED
    
    
@users.route('/', methods=['GET'])
@jwt_required()
def get_users():
    current_user = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 2, type=int)
    users = User.query.order_by(User.created_at).paginate(page=page, per_page=per_page)
    
    data = []
    
    for user in users.items:
        data.append({
            'username': user.username,
            'email': user.email
        })
    
    meta={
        "page": users.page,
        "pages": users.pages,
        'total_count': users.total,
        'prev_page': users.prev_num,
        'next_page': users.next_num,
        'has_next': users.has_next,
        'has_prev': users.has_prev,
    }
    return jsonify({'data': data, 'meta': meta}), HTTP_200_OK
    
@users.route('/<string:id>', methods=['GET'])
# @jwt_required()
def get_user(id):
    # current_user = get_jwt_identity()
    user = User.query.filter_by(username=id).first()
    if user is not None:
        return jsonify({
                'username': user.username,
                'email': user.email
            }), HTTP_200_OK
    else:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND
    
@users.route('/<string:id>', methods=['DELETE'])
# @jwt_required()
def del_user(id):
    # current_user = get_jwt_identity()
    user = User.query.filter_by(username=id).first()
    if user is not None:
        db.session.delete(user)
        db.session.commit()
        return jsonify({}), HTTP_204_NO_CONTENT
    else:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND
    
    
@users.route('/<string:id>', methods=['PUT'])
@users.route('/<string:id>', methods=['PATCH'])
@jwt_required()
def edit_user(id):
    current_user = get_jwt_identity()
    new_user = request.json['user']
    
    # username = new_user['new_username']
    email = new_user['new_email']
    password = new_user['new_password']
    print(password)
    user = User.query.filter_by(username= id).first()
    if len(password)<3:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST
    
    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT
    
    pwd_hash = generate_password_hash(password)
    # user.username = username
    user.password = pwd_hash,
    user.password = user.password[0]
    user.email = email
    db.session.commit()
    return jsonify({
        'message': "User changed",
        'user': {
            'username': user.username, 'email':email
        }
    }), HTTP_200_OK
