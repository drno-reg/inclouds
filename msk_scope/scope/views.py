from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

from scope import scope, logging, models, db

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


@scope.route('/scope/<string:table_name>/<string:command>/<string:number>', methods=['GET'])
def scope_runner(table_name, command, number):
    if (command == "migration"):
        job_script = 'python3 scope/migration_tables.py '+table_name+' '+number
        result = str(get_simple_cmd_output(job_script))
        return result
    if (table_name=='all') and (command == "refresh"):
        job_script = 'python3 scope/refresh_tables.py'
        # job_script = 'ls -las'
        result = str(get_simple_cmd_output(job_script))
        return result
    if (table_name=='all') and (command == "drop_refresh"):
        models.db.session.execute("""
        DROP TABLE IF EXISTS threshols;
        """);
        models.db.session.execute("""
        DROP TABLE IF EXISTS scope_dir; 
        """);
        models.db.session.execute("""
        DROP TABLE IF EXISTS scheduler_dir;
        """);
        models.db.session.execute("""
        DROP TABLE IF EXISTS orders;
        """);
        models.db.create_all()
        job_script = 'python3 scope/refresh_tables.py'
        # job_script = 'ls -las'
        result = str(get_simple_cmd_output(job_script))
        return result



# попытка объединения, как же я люблю искать общее, находить общий знаменатель и упрощать)
@scope.route('/orders/<string:dir>/<string:value_or_command>', methods=['POST','GET'])
def orders(dir, value_or_command):
    if request.method == "POST":
        # ожидается JSON в котором будет {id_orders: "3", critical_1: "5", critical_2: "5", critical_count: "0", critical_conditions: ">"}
        json = request.get_json()
        print("FrontEnd: ", json)
        if (dir=='thresholds'):
            if (value_or_command=='update'):
                result=[{'critical_1': json['critical_1'],'critical_2': json['critical_2'],'critical_count': json['critical_count'],'critical_conditions': json['critical_conditions'],
                         'telegram_token': json['telegram_token'],'telegram_chatid': json['telegram_chatid'],'id_orders': json['id_orders']}]
                print("BackEnd: ",result)
                models.db.session.execute("""
                    update thresholds set critical_1= :critical_1, critical_2= :critical_2, critical_count= :critical_count, critical_conditions= :critical_conditions, 
                                          telegram_token= :telegram_token, telegram_chatid= :telegram_chatid 
                    where id_orders= :id_orders
                    """,result);
            if (value_or_command=='insert'):
                result=[{'id':json['thresholds'],'critical_1': json['critical_1'],'critical_2': json['critical_2'],'critical_count': json['critical_count'],'critical_conditions': json['critical_conditions'],
                         'telegram_token': json['telegram_token'],'telegram_chatid': json['telegram_chatid'],'id_orders': json['id_orders']}]
                print("BackEnd: ",result)
                models.db.session.execute("""
                insert into thresholds (id, id_orders, critical_1, critical_2, critical_count, critical_conditions, telegram_token, telegram_chatid) 
                values (:id, :id_orders, :critical_1, :critical_2, :critical_count, :critical_conditions, :telegram_token, :telegram_chatid)
                    """,result);
        models.db.session.commit();
        return jsonify({'result': [dict(row) for row in result]})
    # для решения задачи по копированию данных от main в сторону scope через сервис /scope/update
    if request.method == "GET":
        if (dir=='thresholds') and (value_or_command!='all'):
            result=models.db.session.execute("""
                select t.* from orders o
                inner join thresholds t on o.id = t.id_orders
                where o.executors= :value1
            """,{'value1': value_or_command})
        elif (dir=='thresholds') and (value_or_command=='all'):
            result=models.db.session.execute("""
                select t.* from thresholds t
                order by t.id
            """)
        elif (dir=='scheduler_log'):
            result=models.db.session.execute("""
                 select * from (  
                 select * from scheduler_log sl where sl.id_orders = :id_order 
                   ORDER BY
                    rowid desc
                LIMIT 10)
                ORDER by id
                """, {'id_order':value_or_command})
        elif (dir=='executors'):
            result=models.db.session.execute('select * from orders o where o.executors= :executors',{'executors': value_or_command})
        return jsonify({'result': [dict(row) for row in result]})

# пока пришлось отдельный API реализовать но в послествии объединим
@scope.route('/orders/<string:command>', methods=['GET', 'POST'])
def scope_orders(command):
    if request.method == "POST":
        # return "Вот это пост!"
        # print(request.get_json())
        # return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
        #   content = request.json
        # print(content)
        print(request.is_json)
        json = request.get_json()
        print("FrontEnd: ", json)
        if (command=='status'):
            result=[{'status': json["status"], 'date_change': json["date_change"], 'id': int(json["id"])}]
            print("BackEnd: ",result)
            models.db.session.execute('update orders set status= :status, date_change= :date_change where id= :id',result)
        if (command=='update'):
            result=[{'id_scope_dir': json["id_scope_dir"], 'parameters': json["parameters"], 'executors': json["executors"], 'date_change': json["date_change"], 'id': int(json["id"])}]
            print("BackEnd: ",result)
            models.db.session.execute('update orders set id_scope_dir= :id_scope_dir , parameters= :parameters , executors= :executors, date_change= :date_change where id= :id',result)
            result=[{'job_frequency': json["job_frequency"], 'job_frequency_type': json["job_frequency_type"], 'id_orders': int(json["id"])}]
            print("BackEnd: ",result)
            models.db.session.execute('update scheduler_dir set job_frequency= :job_frequency , job_frequency_type= :job_frequency_type where id_orders= :id_orders',result)
        if (command=='insert'):
            print(json)
            date_create=datetime.now()
            status = "stop"
            result=[{'id':json["orders"],'id_users':json["id_users"],'id_scope_dir':json["id_scope_dir"],'parameters': json["parameters"], 'executors': json["executors"],'date_create':date_create,'status':status}]
            resultproxy=models.db.session.execute('insert into orders (id, id_users, id_scope_dir, parameters, executors, date_create, status) values (:id, :id_users, :id_scope_dir, :parameters, :executors, :date_create, :status)',result)
            # если нужно вычислить id
            # print(resultproxy.lastrowid)
            job_script = "python3 templates/"
            result=[{'id':json["scheduler_dir"],'id_orders':resultproxy.lastrowid,'job_frequency':json["job_frequency"],'job_frequency_type': json["job_frequency_type"], 'job_script': job_script}]
            print("BackEnd: ",result)
            models.db.session.execute('insert into scheduler_dir (id_orders, job_frequency, job_frequency_type, job_script) values (:id_orders, :job_frequency, :job_frequency_type, :job_script)',result)
        # if (command=='delete'):
        #     db.session.execute('delete from test where id= :value1',{'value1': int(json["id"])})
        models.db.session.commit()
        # пример [{"id":"1","context1":"xyz123"}]
        # и тогда
        # print(content[0]["id"])
        # пример {"id":"1","context1":"xyz123"}
        # и тогда
        # print(content["id"])
        return jsonify({'result': [dict(row) for row in result]})

    if request.method == "GET":
        result=models.db.session.execute('select o.id, sd.id as id_scope_dir, sd.name, sd.describe, o.parameters, o.executors, sd2.job_frequency, sd2.job_frequency_type, o.status from orders o inner join scope_dir sd on sd.id=o.id_scope_dir inner join scheduler_dir sd2 on o.id=sd2.id_orders order by o.id');
        return jsonify({'result': [dict(row) for row in result]})



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
