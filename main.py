from flask import Flask, url_for, render_template, make_response, abort, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session

from data.products import Products
from data.user import User

from forms.loginForm import LoginForm
from forms.registrationForm import Register


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_project_key'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init('db/blogs.db')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
def start_page():
    db_sess = db_session.create_session()
    products = db_sess.query(Products).all()
    params = {
        'title': "ВерстNET",
        'now_tab': 1,
        'lst': products
    }
    print(list(params['lst']))
    return render_template('main.html', **params)


@app.route('/<int:idProd>', methods=['GET', 'POST'])
def product_page(idProd):
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


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')