from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
import logging

#свои
from main_app import app_configs

main_app = Flask(__name__, static_url_path='')

main_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
main_app.config['TEMPLATES_AUTO_RELOAD'] = True
# inclouds.config["CACHE_TYPE"] = "simple"
# inclouds.config["CACHE_DEFAULT_TIMEOUT"] = "300"
main_app.config["DEBUG"] = True
main_app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
main_app.config['PROPAGATE_EXCEPTIONS'] = True
# Ensure that debug mode is *on*
# app.debug = True
# Set the secret key to some random bytes. Keep this really secret!
main_app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# Enable flask session cookies
main_app.config['SECRET_KEY'] = 'key'

app_configs=app_configs.load_configs()

main_app.config['SQLALCHEMY_DATABASE_URI'] = app_configs.get('SQLALCHEMY_DATABASE_URI')
main_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(main_app)

login_manager = LoginManager(main_app)

# toolbar = DebugToolbarExtension(main_app)

from main_app import models, views
# регистрируем представление для аутентификации
from main_app.authorization.views import authorization_blueprint
main_app.register_blueprint(authorization_blueprint)
# регистрируем представление для скачивания файлов
from main_app.download.views import download_blueprint
main_app.register_blueprint(download_blueprint)

db.create_all()
