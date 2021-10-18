from flask_login import UserMixin
from datetime import datetime

from main_app import main_app, db

# db = SQLAlchemy(app)
# справочник ролей
class roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(128), nullable=False)
    describe = db.Column(db.String(255), nullable=False)
# связь пользоватеей и роли
# class roles (db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     id_users = db.Column(db.Integer, db.ForeignKey('users.id'))
#     id_roles_dir = db.Column(db.Integer, db.ForeignKey('roles_dir.id'))
# справочник метрик
class scope_dir (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    describe = db.Column(db.String(255), nullable=False)
    template = db.Column(db.String(255), nullable=False)
# заказы
class orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_users = db.Column(db.Integer, db.ForeignKey('users.id'))
    id_scope_dir = db.Column(db.Integer, db.ForeignKey('scope_dir.id'))
    parameters = db.Column(db.String(255), nullable=False)
    executors = db.Column(db.String(255), nullable=False)
    date_create = db.Column(db.DateTime, default=datetime.utcnow)
    date_change = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)
# пороговые значения
class thresholds(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_orders = db.Column(db.Integer, db.ForeignKey('orders.id'))
    minor_1 = db.Column(db.Float)
    minor_2 = db.Column(db.Float)
    minor_count = db.Column(db.Integer)
    minor_conditions = db.Column(db.String(25))
    warning_1 = db.Column(db.Float)
    warning_2 = db.Column(db.Float)
    warning_count = db.Column(db.Integer)
    warning_conditions = db.Column(db.String(25))
    critical_1 = db.Column(db.Float)
    critical_2 = db.Column(db.Float)
    critical_count = db.Column(db.Integer)
    critical_conditions = db.Column(db.String(25))
    telegram_token = db.Column(db.String(255))
    telegram_chatid = db.Column(db.Integer)
# параметры исполнения заказов
class scheduler_dir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_orders = db.Column(db.Integer, db.ForeignKey('orders.id'))
    job_frequency = db.Column(db.String(255), nullable=False)
    job_frequency_type = db.Column(db.String(255), nullable=False)
    job_script = db.Column(db.String, nullable=False)

# хранилище метрик
class scope_store (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_orders = db.Column(db.Integer, db.ForeignKey('orders.id'))
    value = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

class scheduler_log (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # id_orders = db.Column(db.Integer, db.ForeignKey('orders.id'))
    id_orders = db.Column(db.Integer)
    job_status = db.Column(db.String(128))
    job_start = db.Column(db.DateTime, default=datetime.utcnow)
    job_end = db.Column(db.DateTime, default=datetime.utcnow)
    job_log = db.Column(db.Text)

# db.create_all()
