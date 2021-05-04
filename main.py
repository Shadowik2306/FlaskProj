from flask import Flask, url_for, render_template, jsonify, make_response, abort, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
import datetime

from data.bag import Bag
from data.user_resource import *
from data.products_resoursce import *
from data.commentResource import *

from forms.loginForm import LoginForm
from forms.registrationForm import Register
from forms.write_commForm import CommForm
from forms.bagForm import BagForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_project_key'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init('db/blogs.db')
api = Api(app)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'})), 404


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def get_time():
    time = datetime.now().year * 31536000 + datetime.now().month * 2419200 + datetime.now().day * 86400 + datetime.now().hour * 3600 + datetime.now().minute * 60 + datetime.now().second
    return time


@app.route('/')
def start_page():
    db_sess = db_session.create_session()
    products_real = list(db_sess.query(Products).filter(Products.sold))
    products_sold = list(db_sess.query(Products).filter(Products.sold == 0))
    l = 0
    for i in range(len(products_real)):
        try:
            if int(products_real[i - l].time) >= get_time():
                products_sold.append(products_real[i - l])
                del products_real[i - l]
                l += 1
        except Exception:
            break
    params = {
        'title': "ВерстNET",
        'now_tab': 1,
        'lst': products_real if list(products_real) else False,
        'lst_of_sold': products_sold if list(products_sold) else False
    }
    return render_template('main.html', **params)


@app.route('/<int:idProd>', methods=['GET', 'POST'])
def product_page(idProd):
    if request.method == 'POST':
        if current_user.is_authenticated:
            db_sess = db_session.create_session()
            user_bag = db_sess.query(Bag).filter(Bag.user_id == current_user.id)
            print(int(request.form['num']))
            if not list(user_bag):
                bag = Bag(
                    user_id=current_user.id,
                    lst=f'{idProd}: {request.form["num"]}'
                )
                db_sess.add(bag)
                db_sess.commit()
            else:
                user_bag[0].lst += f', {idProd}: {request.form["num"]}'
                db_sess.commit()
            db_sess = db_session.create_session()
            prod = db_sess.query(Products).get(idProd)
            prod.sold = 0
            db_sess.commit()
            return redirect('/')
        else:
            return redirect('/login')
    db_sess = db_session.create_session()
    products = db_sess.query(Products).get(idProd)
    params = {
        'title': "ВерстNET",
        'now_tab': 0,
        'product': products
    }
    return render_template('prod_page.html', **params)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form, now_tab=4)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        if not form.password.data == form.password_repeat.data:
            return render_template('register.html', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.login.data).first():
            return render_template('register.html', form=form,
                                   message="Такой пользователь уже есть")
        new_user = User(
            surname=form.surname.data,
            name=form.name.data,
            email=form.login.data,
        )
        new_user.set_password(form.password.data)
        db_sess.add(new_user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', form=form)


@app.route('/about_us')
def about_us():
    params = {
        'title': "ВерстNET",
        'now_tab': 2,
    }
    return render_template('about_us.html', **params)


@app.route('/comments', methods=['GET', 'POST'])
def comments():
    if request.method == 'POST':
        return redirect('/write_comment')
    db_sess = db_session.create_session()
    comm = db_sess.query(Comments).all()
    params = {
        'title': "ВерстNET",
        'now_tab': 3 ,
        'comments': comm
    }
    return render_template('comments.html', **params)


@app.route('/bag', methods=['GET', 'POST'])
@login_required
def bag():
    if request.method == 'POST':
        db_sess = db_session.create_session()
        k = list(db_sess.query(Bag).filter(Bag.user_id == current_user.id))[0]
        for i in k.lst.split(', '):
            db_sess.query(Products).get(i.split(': ')[0]).sold = 1
            db_sess.query(Products).get(i.split(': ')[0]).time = get_time() + int(i.split(': ')[1]) * 3600
        db_sess.delete(k)
        db_sess.commit()
        return redirect('/thanks')
    params = {
        'title': "ВерстNET",
        'now_tab': 6,
    }
    db_sess = db_session.create_session()
    k = list(db_sess.query(Bag).filter(Bag.user_id == current_user.id))
    error = ''
    dct = []
    summa = 0
    if k:
        k = k[0]
        dct = [(db_sess.query(Products).get(int(i.split(': ')[0])).name, db_sess.query(Products).get(int(i.split(': ')[0])).cost, int(i.split(': ')[1]))
               for i in set(k.lst.split(', '))]
        print(dct)
        summa = sum(i[1] * i[2] for i in dct)
    else:
        error = 'В корзине пусто'
    return render_template('bag.html', lst=dct, error=error, summa=summa, **params)


@app.route('/write_comment', methods=['GET', 'POST'])
@login_required
def write_comment():
    form = CommForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comments = Comments(
            user_id=current_user.id,
            text=form.text.data
        )
        db_sess.add(comments)
        db_sess.commit()
        return redirect('/comments')
    params = {
        'title': "ВерстNET",
    }
    return render_template('write_comment.html', form=form, **params)


@app.route('/thanks')
@login_required
def thanks():
    return render_template('thanks.html')


if __name__ == '__main__':
    api.add_resource(UsersListResource, '/api/users')
    api.add_resource(UserResource, '/api/users/<int:users_id>')
    api.add_resource(ProductsListResource, '/api/products')
    api.add_resource(ProductResource, '/api/products/<int:products_id>')
    api.add_resource(CommentResource, '/api/comments/<int:comments_id>')
    api.add_resource(CommentListResource, '/api/comments')
    app.run(port=8083, host='127.0.0.1')