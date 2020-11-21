from flask import Blueprint, render_template, redirect, url_for, request, flash, send_file, send_from_directory
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
# импорт моделей
from main_app.authorization.models import Users, db


from main_app.views import main_app, logging

# объявление модели
download_blueprint = Blueprint('download_blueprint', __name__)


# @download_blueprint.route('/.well-known/pki-validation/')
# def downloadFile ():
#     #For windows you need to use drive name [ex: F:/Example.pdf]
#     path = "/"
#     return send_file(path, as_attachment=True)


# @download_blueprint.route('/.well-known/pki-validation/1A9D3A92153E375B8F438F16CA23718F.txt', methods=['GET'])
# def return_file():
#     return send_from_directory(directory='files', filename='1A9D3A92153E375B8F438F16CA23718F.txt', as_attachment=True)


@download_blueprint.route('/.well-known/pki-validation/<filename>', methods=['GET'])
def return_file(filename):
    return send_from_directory(directory='files', filename=filename, as_attachment=True)