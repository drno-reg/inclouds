from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
# импорт своего

# from main_app.authorization.env_change import env_change

# env_change.os_pythonpath_change()

# импорт моделей
from main_app.authorization.models import Users, db


from main_app.views import main_app, logging

# объявление модели
authorization_blueprint = Blueprint('authorization_blueprint', __name__)


@authorization_blueprint.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = Users.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            # next_page = request.args.get('next')
            #
            # return redirect(next_page)
            # orders = [{
            #     "name": "ping",
            #     "parameter": "inclouds.bizml.ru"
            # },
            #     {
            #         "name": "http_get",
            #         "parameter": "https://inclouds.bizml.ru"
            #     }
            # ]
            # result=[]
            #
            # metrics = ["ping - inclouds.bizml.ru","http_get - https://inclouds.bizml.ru"]
            #
            # return render_template('main.html', user=Users.query.filter_by(login=login).first(), metrics=metrics, orders=result)
            result=db.session.execute('select o.id, sd.name, sd.describe, o.parameters, o.executors from orders o inner join scope_dir sd on sd.id=o.id_scope_dir inner join users us on us.id=o.id_users where us.login= :value1',{'value1': login})
            result=[dict(row) for row in result]
            # print("result: ", result)

            metrics = ["ping - inclouds.bizml.ru","http_get - https://inclouds.bizml.ru"]

            return render_template('main.html', user=Users.query.filter_by(login=login).first(), metrics=metrics, orders=result)
        else:
            flash('Ошибка в логине или пароле')
    else:
        flash('Пожалуйста заполните поля учетной записи и пароля')

    return render_template('index.html')


@authorization_blueprint.route('/register', methods=['GET', 'POST'])
def register_page():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    name = request.form.get('name')
    surname = request.form.get('surname')
    company = request.form.get('company')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Пожалуйста заполните все поля!')
        elif password != password2:
            flash('Пароль не совпадают!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = Users(login=login, password=hash_pwd, name=name, surname=surname, company=company)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('index_start'))

    return render_template('register.html')


@authorization_blueprint.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index_start'))


@authorization_blueprint.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('authorization_blueprint.login_page') + '?next=' + request.url)

    return response
