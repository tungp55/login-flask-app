from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.model import User, db
import validators
auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth.post('/register')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    
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
    
@auth.post('login')
def login():
    username = request.json['username']
    password = request.json['password']
    
    user = User.query.filter_by(username= username).first()
    if user:
        is_pass_correct = check_password_hash(user.password, password)
        if is_pass_correct:
            access_token = create_access_token(identity=user.id)
            print(access_token)
            print(user.id)
            return jsonify({
                'user':{
                    'access_token': access_token,
                    'email': user.email
                }
            }), HTTP_200_OK
    return jsonify({'error':"Wrong credentials"}), HTTP_401_UNAUTHORIZED


    
        

