from flask import Flask
from flask_cors import CORS

from flask_debugtoolbar import DebugToolbarExtension
import logging

#свои
from scope import app_configs

scope = Flask(__name__, static_url_path='')
# пришлось добавить эту штуку чтобы решить проблему с blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
CORS(scope)

scope.config["DEBUG"] = True
scope.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
scope.config['PROPAGATE_EXCEPTIONS'] = True
# Ensure that debug mode is *on*
# app.debug = True
# Set the secret key to some random bytes. Keep this really secret!
scope.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# Enable flask session cookies
scope.config['SECRET_KEY'] = 'key'

app_configs=app_configs.load_configs()

scope.config['SQLALCHEMY_DATABASE_URI'] = app_configs.get('SQLALCHEMY_DATABASE_URI')

# scope.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////opt/docker/sqlite_inclouds/msk_scope.db'
# scope.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/msk_scope.db'
scope.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

toolbar = DebugToolbarExtension(scope)

from scope import views, models

# регистрируем представление для аутентификации
# from inclouds.authorization.views import authorization_blueprint
# inclouds.register_blueprint(authorization_blueprint)
# # регистрируем представление для скачивания файлов
# from inclouds.download.views import download_blueprint
# inclouds.register_blueprint(download_blueprint)
#
# регистрируем представление для скачивания файлов
from scope.download.views import download_blueprint
scope.register_blueprint(download_blueprint)
