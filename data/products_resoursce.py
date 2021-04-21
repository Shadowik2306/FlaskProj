from flask_restful import reqparse, abort, Api, Resource
import flask
from flask import Flask
from . import db_session
from .products import Products
from flask import jsonify, request


def abort_if_user_not_found(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(Products).get(user_id)
    if not user:
        abort(404, message=f'User {user_id} not found')


parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('image', required=True)
parser.add_argument('cost', required=True)
parser.add_argument('description', required=True)


class ProductResource(Resource):
    def get(self, products_id):
        abort_if_user_not_found(products_id)
        db_sess = db_session.create_session()
        product = db_sess.query(Products).get(products_id)
        return jsonify(
            {'users': product.to_dict()}
        )

    def delete(self, products_id):
        abort_if_user_not_found(products_id)
        db_sess = db_session.create_session()
        product = db_sess.query(Products).get(products_id)
        db_sess.delete(product)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class ProductsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        products = session.query(Products).all()
        return jsonify({'products': [item.to_dict() for item in products]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        products = Products(
            name=args['name'],
            image=args['image'],
            cost=args['cost'],
        )
        session.add(products)
        session.commit()
        return jsonify({'success': 'OK'})