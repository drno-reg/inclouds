from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
#свои
import app_configs
# engine = create_engine('sqlite:///db/msk_scope.db', echo=True)

app_configs=app_configs.load_configs()

engine = create_engine(app_configs.get('SQLALCHEMY_DATABASE_URI'), echo=True)

metadata = MetaData()


# db = SQLAlchemy(scope)

# Справочник метрик на scope сервере
scope_dir = Table(
   'scope_dir', metadata,
   # Column('id', Integer, primary_key=True),
   Column('id', Integer),
   Column('name', String),
   Column('describe', String),
   Column('template', String)
)

# заказы
orders = Table(
    'orders', metadata,
    # Column('id', Integer, nullable=False),
    # Column('id', Integer, primary_key=True),
    Column('id', Integer),
    Column('id_users', Integer, nullable=False),
    Column('id_scope_dir', Integer, ForeignKey("scope_dir.id"), nullable=False),
    Column('parameters', String),
    Column('executors', String),
    Column('date', DateTime, default=datetime.utcnow),
)

scheduler_dir = Table (
  'scheduler_dir', metadata,
   # Column('id', Integer, primary_key=True),
   Column('id', Integer),
   Column('id_orders', Integer, ForeignKey("orders.id"), nullable=False),
   Column('job_frequency', String),
   Column('job_frequency_type', String),
   Column('job_script', String)
)

thresholds = Table (
    'thresholds', metadata,
    # Column('id', Integer, primary_key=True),
    Column('id', Integer),
    Column('id_orders', Integer, ForeignKey("orders.id"), nullable=False),
    Column('minor_1', Integer),
    Column('minor_2', Integer),
    Column('minor_count', Integer),
    Column('minor_conditions', String),
    Column('warning_1', Integer),
    Column('warning_2', Integer),
    Column('warning_count', Integer),
    Column('warning_conditions', String),
    Column('critical_1', Integer),
    Column('critical_2', Integer),
    Column('critical_count', Integer),
    Column('critical_conditions', String),
    Column('telegram_token', String),
    Column('telegram_chatid', String),
)

scheduler_log = Table (
   'scheduler_log', metadata,
   Column('id', Integer, primary_key=True),
   Column('id_orders', Integer, ForeignKey("orders.id"), nullable=False),
   Column('job_status', String),
   Column('job_start', DateTime, default=datetime.utcnow),
   Column('job_end', DateTime, default=datetime.utcnow),
   Column('job_log', String),
)

scope_store = Table(
    'scope_store', metadata,
    Column('id', Integer, primary_key=True),
    Column('id_orders', Integer, ForeignKey("orders.id"), nullable=False),
    Column('value', String),
    Column('date', DateTime, default=datetime.utcnow)
)

metadata.create_all(engine)

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


# class scope_dir (db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(128), nullable=False)
#    describe = db.Column(db.String(255), nullable=False)

# Хранилище значений метрик на store сервере
# class scope_store (db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    id_dir = db.Column(db.Integer, db.ForeignKey('scope_dir.id'))
#    value = db.Column(db.Integer, nullable=False)
#    date = db.Column(db.DateTime, default=datetime.utcnow)


# db.create_all()
