from flask_restful import reqparse, abort, Api, Resource
import flask
from flask import Flask
from . import db_session
from .user import User
from flask import jsonify, request
from werkzeug.security import generate_password_hash
from datetime import datetime


def abort_if_user_not_found(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        abort(404, message=f'User {user_id} not found')


parser = reqparse.RequestParser()
parser.add_argument('surname', required=True)
parser.add_argument('name', required=True)
parser.add_argument('email', required=True)
parser.add_argument('hashed_password', required=True)


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        db_sess = db_session.create_session()
        users = db_sess.query(User).get(user_id)
        return jsonify(
            {'users': users.to_dict()}
        )

    def delete(self, users_id):
        abort_if_user_not_found(users_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(users_id)
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        user = session.query(User).all()
        return jsonify({'user': [item.to_dict() for item in user]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        news = User(
            surname=args['surname'],
            name=args['name'],
            email=args['email'],
            hashed_password=(args['hashed_password']),
        )
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})