from flask_restful import reqparse, abort, Api, Resource
import flask
from flask import Flask
from . import db_session
from .comments import Comments
from .user import User
from flask import jsonify, request


def abort_if_user_not_found(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(Comments).get(user_id)
    if not user:
        abort(404, message=f'User {user_id} not found')


parser = reqparse.RequestParser()
parser.add_argument('user_id', required=True)
parser.add_argument('text', required=True)


class CommentResource(Resource):
    def get(self, comments_id):
        abort_if_user_not_found(comments_id)
        db_sess = db_session.create_session()
        comment = db_sess.query(Comments).get(comments_id)
        return jsonify(
            {'users': comment.to_dict()}
        )

    def delete(self, comments_id):
        abort_if_user_not_found(comments_id)
        db_sess = db_session.create_session()
        comment = db_sess.query(Comments).get(comments_id)
        db_sess.delete(comment)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class CommentListResource(Resource):
    def get(self):
        session = db_session.create_session()
        comments = session.query(Comments).all()
        return jsonify({'products': [item.to_dict() for item in comments]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        lst = [i.id for i in session.query(User).all()]
        if args['user_id'] not in lst:
            abort(404)
        products = Comments(
            user_id=args['user_id'],
            text=args['text']
        )
        session.add(products)
        session.commit()
        return jsonify({'success': 'OK'})