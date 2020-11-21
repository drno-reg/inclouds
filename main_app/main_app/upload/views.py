from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, send_from_directory
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
# импорт моделей
from inclouds_app.inclouds.authorization.models import Users, db

import os

from inclouds_app.inclouds.views import inclouds, logging

# объявление модели
upload_blueprint = Blueprint('download_blueprint', __name__)


# @download_blueprint.route('/.well-known/pki-validation/')
# def downloadFile ():
#     #For windows you need to use drive name [ex: F:/Example.pdf]
#     path = "/"
#     return send_file(path, as_attachment=True)


# @upload_blueprint.route('/.well-known/pki-validation/<path:filename>', methods=['GET', 'POST'])
# def download(filename):
#     uploads = os.path.join(inclouds_app.inclouds.root_path, inclouds.config['UPLOAD_FOLDER'])
#     return send_from_directory(directory=uploads, filename=filename)
