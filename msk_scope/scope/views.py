from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

from scope import scope, logging, models

from datetime import datetime

from subprocess import Popen, PIPE, STDOUT
import shlex

def get_simple_cmd_output(cmd, stderr=STDOUT):
    """
    Execute a simple external command and get its output.
    """
    args = shlex.split(cmd)
    return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]


@scope.route('/', methods=['GET'])
def index_start():
    logging.warning("See this message in Flask Debug Toolbar!")
    # return render_template('index.html')
    return "не Fuck, а новая версия 1.13!"

@scope.route('/scope/dir', methods=['GET'])
def get_all():
    result=models.scope_dir.query.all()
    return str(models.scope_dir__schema_all.dump(result))


@scope.route('/scope_json/dir', methods=['GET'])
def get_all_json():
    #result = [x.get_json() for x in models.scope_dir.query.all()]
    result = list(map(lambda x: x.get_json(), models.scope_dir.query.all()))
    return jsonify(result)



@scope.route('/scope/dir/<int:id>', methods=['GET'])
def main_scope_dir(id):
    if request.method == "GET":
        result=models.scope_dir.query.get(id)
        return str(models.scope_dir__schema.dump(result))
      # return jsonify(json_list=[i.serialize for i in scope.all()])
    # Article.query.order_by(Article.date.desc()).all()
    # Assuming that there is a name property on your user object
    # returned by the callback
    # return "Ok!"
    # if current_user.is_authenticated:
    #     # return 'Hello %s!' % current_user.name
    #     return render_template('main.html', user=current_user)
    # else:
    #     return render_template('index.html')

@scope.route('/scope_json/dir/<int:id>', methods=['GET'])
def main_scope_dir_json(id):
    if request.method == "GET":
        result=models.scope_dir.query.get(id)
        return result.get_json()


def toDate(dateString):
    return datetime.strptime(dateString, "%Y-%m-%d").date()


@scope.route('/scope/store_by_datetime', methods=['GET'])
def main_scope_store_by_date():
    if request.method == "GET":
        # id_scope_dir,datetime_start \'2020-10-18\'
        result=models.db.session.execute('select * from scope_store s3 where s3.id_orders= :value1 and s3.date BETWEEN :value2 and :value3 order by id',{'value1': request.args.get('id_orders'),'value2': datetime.strptime(request.args.get('datetime_start'),'%Y-%m-%d %H:%M'),'value3': datetime.strptime(request.args.get('datetime_end'),'%Y-%m-%d %H:%M')})
        return jsonify({'result': [dict(row) for row in result]})


@scope.route('/scope/store/<int:id_orders>', methods=['GET'])
def main_scope_store(id_orders):
    if request.method == "GET":
        # result=models.scope_store.query.get(id_dir)
        # result=models.db.session.query(models.scope_store).filter(models.scope_store.id_dir == id_scope_dir)

        # result=models.db.session.query(models.scope_store).filter(models.scope_store.id_dir == id_dir).order_by(models.scope_store.date).first()

        # resul=models.db.engine.execute('select * from scope_store')

        # result=models.db.engine.execute('select * from scope_store where id_dir=: id_dir',id_dir=id_dir)

        result=models.db.session.execute('select * from scope_store ss where ss.id_orders= :value1 order by ss.date desc limit 1',{'value1': id_orders})

        print(result)

        # print(models.scope_store__schema.dump(result))

        # for row in result:
        #   print ("id:", row.id, "id_dir: ",row.id_dir, "value:",row.value, "date:",row.date)
        # result=models.db.session.query(models.scope_store).filter(models.scope_store.id_dir == id_dir).fetchall()
        # result=models.scope_store.select().order_by(models.scope_store.c.id.desc()).limit(5)
        return str(models.scope_store__schema_all.dump(result))

@scope.route('/scope_json/store/<int:id_scope_dir>', methods=['GET'])
def main_scope_store_json(id_scope_dir):
    if request.method == "GET":
        result=models.db.session.execute('select * from scope_store ss where ss.id_scope_dir= :value1 order by ss.date desc limit 1',{'value1': id_scope_dir})
        return jsonify({'result': [dict(row) for row in result]})


@scope.route('/scope/update', methods=['GET'])
def scope_runner():
    job_script = 'python3 scope/update_orders.py'
    # job_script = 'ls -las'
    result = str(get_simple_cmd_output(job_script))
    return result

# @scope.route('/scope/store/<int:id_scope_dir>', methods=['GET'])
# def main_scope_store1(id_scope_dir):
#     if request.method == "GET":
#         result=models.db.session.execute('select * from scope_store ss where ss.id_scope_dir= :value1 order by ss.date desc limit 1',{'value1': id_scope_dir})
#
#         print(result)
#         return jsonify(id=,
#                        email=g.user.email,
#                        id=g.user.id)

# @scope.route()


# return render_template('main.html', messages=Message.query.all())
# @app.route('/add_message', methods=['POST'])
# @login_required
# def add_message():
#     text = request.form['text']
#     tag = request.form['tag']
#
#     db.session.add(Message(text, tag))
#     db.session.commit()
#
#     return redirect(url_for('main'))
#
#
