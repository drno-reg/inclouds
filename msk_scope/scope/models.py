from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from scope import scope

db = SQLAlchemy(scope)
ma = Marshmallow(scope)

# class Users (db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     login = db.Column(db.String(128), nullable=False, unique=True)
#     password = db.Column(db.String(255), nullable=False)
#     name = db.Column(db.String(128), nullable=False)
#     surname = db.Column(db.String(128), nullable=False)
#     company = db.Column(db.String(128), nullable=False)
#     date = db.Column(db.DateTime, default=datetime.utcnow)
#
#     def __repr__(self):
#         return '<User %r>' % self.login

# Расписание
# class scheduler_log (db.Model):


# Справочник метрик на scope сервере
class scope_dir (db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(128), nullable=False)
   describe = db.Column(db.String(255), nullable=False)
   template = db.Column(db.String(255), nullable=False)

   def get_json(self):
      return {
         'id': self.id,
         'name': self.name,
         'describe': self.describe,
         'template': self.template
      }

   def __repr__(self):
      return '<scope_dir %r>' % self

class scope_dir_schema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ("id", "name", "describe", "template")

scope_dir__schema = scope_dir_schema()
scope_dir__schema_all = scope_dir_schema(many=True)

# Хранилище значений метрик на store сервере
class scope_store (db.Model):
   id = db.Column(db.Integer, primary_key=True)
   id_orders = db.Column(db.Integer, db.ForeignKey('orders.id'))
   value = db.Column(db.Integer, nullable=False)
   date = db.Column(db.DateTime, default=datetime.utcnow)

   def get_json(self):
      return {
         'id': self.id,
         'id_orders': self.id_orders,
         'value': self.value,
         'date': self.date
      }

   def __repr__(self):
      return '<scope_store %r>' % self

class scope_store_schema(ma.Schema):
   class Meta:
      # Fields to expose
      fields = ("id", "id_orders", "value", "date")

scope_store__schema = scope_store_schema()
scope_store__schema_all = scope_store_schema(many=True)

# заказы
class orders(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   id_users = db.Column(db.Integer)
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
class scheduler_dir (db.Model):
   id = db.Column(db.Integer, primary_key=True)
   id_orders = db.Column(db.Integer, db.ForeignKey('orders.id'))
   job_frequency = db.Column(db.String(128), nullable=False)
   job_frequency_type = db.Column(db.String(128), nullable=False)
   job_script = db.Column(db.String(1024), nullable=False)

class scheduler_log (db.Model):
   id = db.Column(db.Integer, primary_key=True)
   id_orders = db.Column(db.Integer, db.ForeignKey('orders.id'))
   job_status = db.Column(db.String(128))
   job_start = db.Column(db.DateTime, default=datetime.utcnow)
   job_end = db.Column(db.DateTime, default=datetime.utcnow)
   job_log = db.Column(db.Text)


db.create_all()
