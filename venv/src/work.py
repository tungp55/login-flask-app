from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.model import Work, db
from flasgger import swag_from

work = Blueprint("works", __name__, url_prefix="/api/v1/works/")


@work.route('/', methods=['POST', 'GET'])
@jwt_required()
def handle_works():
    current_user = get_jwt_identity()

    if request.method == 'POST':

        name = request.get_json().get('name', '')
        status = request.get_json().get('status', '')
        start_time = request.get_json().get('start_time', '')
        end_time = request.get_json().get('end_time', '')  

        if Work.query.filter_by(name=name).first():
            return jsonify({
                'error': 'Work already exists'
            }), HTTP_409_CONFLICT

        work = Work(name=name, start_time=start_time, status =status, end_time=end_time, user_id=current_user)
        db.session.add(work)
        db.session.commit()

        return jsonify({
            'id': work.id,
            'name': work.name,
            'status': work.status,
            'start_time': work.start_time,
            'end_time': work.end_time,
            'created_at': work.created_at,
            'updated_at': work.updated_at,
        }), HTTP_201_CREATED

    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        works = Work.query.filter_by(
            user_id=current_user).paginate(page=page, per_page=per_page)

        data = []

        for work in works.items:
            data.append({
                'id': work.id,
                'name': work.name,
                'status': work.status,
                'start_time': work.start_time,
                'end_time': work.end_time,
                'created_at': work.created_at,
                'updated_at': work.updated_at,
            })

        meta = {
            "page": works.page,
            'pages': works.pages,
            'total_count': works.total,
            'prev_page': works.prev_num,
            'next_page': works.next_num,
            'has_next': works.has_next,
            'has_prev': works.has_prev,

        }

        return jsonify({'data': data, "meta": meta}), HTTP_200_OK


@work.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()

    work = Work.query.filter_by(user_id=current_user, id=id).first()

    if not work:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
        'id': work.id,
        'name': work.name,
        'status': work.status,
        'start_time': work.start_time,
        'end_time': work.end_time,
        'created_at': work.created_at,
        'updated_at': work.updated_at,
    }), HTTP_200_OK


@work.delete("/<int:id>")
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()

    work = Work.query.filter_by(user_id=current_user, id=id).first()

    if not work:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    db.session.delete(work)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@work.put('/<int:id>')
@work.patch('/<int:id>')
@jwt_required()
def editbookmark(id):
    current_user = get_jwt_identity()

    work = Work.query.filter_by(user_id=current_user, id=id).first()

    if not work:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    name = request.get_json().get('name', '')
    status = request.get_json().get('status', '')
    start_time = request.get_json().get('start_time', '')
    end_time = request.get_json().get('end_time', '')  



    work.name = name
    work.status = status
    work.start_time = start_time
    work.end_time = end_time

    db.session.commit()

    return jsonify({
        'id': work.id,
        'name': work.name,
        'status': work.status,
        'start_time': work.start_time,
        'end_time': work.end_time,
        'created_at': work.created_at,
        'updated_at': work.updated_at,
    }), HTTP_200_OK


@work.get("/stats")
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()

    data = []

    items = Work.query.filter_by(user_id=current_user).all()

    for work in items:
        new_link = {
            'id': work.id,
            'name': work.name,
            'status': work.status,
            'start_time': work.start_time,
            'end_time': work.end_time,
            'created_at': work.created_at,
            'updated_at': work.updated_at,
        }

        data.append(new_link)

    return jsonify({'data': data}), HTTP_200_OK
