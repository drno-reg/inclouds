from flask_login import UserMixin
from datetime import datetime

from main_app import main_app, db

# db = SQLAlchemy(app)
# справочник ролей
class roles_dir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(128), nullable=False)
    describe = db.Column(db.String(255), nullable=False)
# связь пользоватеей и роли
class roles (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_users = db.Column(db.Integer, db.ForeignKey('users.id'))
    id_roles_dir = db.Column(db.Integer, db.ForeignKey('roles_dir.id'))
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
    date = db.Column(db.DateTime, default=datetime.utcnow)

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

# db.create_all()
