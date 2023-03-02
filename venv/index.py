from flask import Flask
from flask.json import jsonify
from flask_jwt_extended import JWTManager
from src.model import db
from src.users import users
from src.auth import auth
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
import os



app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get("SECRET_KEY"),
    SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
    SQLALCHEMY_DATABASE_TRACK_MODIFICATIONS=False,
    JWT_SECRET_KEY= os.environ.get("JWT_SECRET_KEY")
)
db.app = app
db.init_app(app)
JWTManager(app)
    
@app.route('/')
def home():
   return 'Hello !!!'
    
app.register_blueprint(auth)

app.register_blueprint(users)




# @app.errorhandler(HTTP_404_NOT_FOUND)
# def handler_404(e):
#     return jsonify({'error': 'Khong tim thay'}), HTTP_404_NOT_FOUND

# @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
# def handler_500(e):
#     return jsonify({'error': 'Co loi da xay ra'}), HTTP_500_INTERNAL_SERVER_ERROR

