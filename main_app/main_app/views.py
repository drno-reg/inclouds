from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user

from flask_caching import Cache


from main_app import main_app, logging, app_configs, models, db
from main_app.authorization.views import authorization_blueprint

import json
import plotly

import pandas as pd
import numpy as np

from datetime import datetime, timedelta
# import datetime

# config = {
#     "CACHE_TYPE": "simple"
# }
# cache = Cache(main_app)

@main_app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@main_app.route('/', methods=['GET'])
def index_start():
    logging.warning("See this message in Flask Debug Toolbar!")
    return render_template('index.html')


# попытка объединения, как же я люблю искать общее, находить общий знаменатель и упрощать)
@main_app.route('/orders/<string:dir>/<string:executors_or_command>', methods=['POST','GET'])
def orders(dir, executors_or_command):
    if request.method == "POST":
        # ожидается JSON в котором будет {id_orders: "3", critical_1: "5", critical_2: "5", critical_count: "0", critical_conditions: ">"}
        json = request.get_json()
        print("FrontEnd: ", json)
        if (dir=='scheduler_log') and (executors_or_command=='insert'):
            result=[{'id_orders': json['id_orders'],'job_status': json['job_status'],'job_start': json['job_start'],'job_end': json['job_end'],
                     'job_log': json['job_log']}]
            resultproxy=db.session.execute("""
                insert into scheduler_log (id, id_orders, job_status, job_start, job_end, job_log) 
                values ((select coalesce(max(id),0) from scheduler_log o)+1, :id_orders, :job_status, :job_start, :job_end, :job_log) RETURNING id
                    """,result);
            result=[{column: value for column, value in rowproxy.items()} for rowproxy in resultproxy]
            result=[{'scheduler_log':result[0]['id']}]
        if (dir=='thresholds'):
            result=[{'critical_1': json['critical_1'],'critical_2': json['critical_2'],'critical_count': json['critical_count'],'critical_conditions': json['critical_conditions'],
            'telegram_token': json['telegram_token'],'telegram_chatid': json['telegram_chatid'],'id_orders': json['id_orders']}]
            print("BackEnd: ",result)
            if (executors_or_command=='update'):
                db.session.execute("""
                    update thresholds set critical_1= :critical_1, critical_2= :critical_2, critical_count= :critical_count, critical_conditions= :critical_conditions, 
                                          telegram_token= :telegram_token, telegram_chatid= :telegram_chatid 
                    where id_orders= :id_orders
                    """,result);
            if (executors_or_command=='insert'):
                resultproxy=db.session.execute("""
                insert into thresholds (id, id_orders, critical_1, critical_2, critical_count, critical_conditions, telegram_token, telegram_chatid) 
                values ((select max(id) from thresholds o)+1, :id_orders, :critical_1, :critical_2, :critical_count, :critical_conditions, :telegram_token, :telegram_chatid) RETURNING id
                    """,result);
                result=[{column: value for column, value in rowproxy.items()} for rowproxy in resultproxy]
                result=[{'thresholds':result[0]['id']}]
        db.session.commit();
        return jsonify({'result': [dict(row) for row in result]})
    # для решения задачи по копированию данных от main в сторону scope через сервис /scope/update
    if request.method == "GET":
        if (dir=='thresholds') and (executors_or_command!='all'):
            result=db.session.execute("""
                select t.* from orders o
                inner join thresholds t on o.id = t.id_orders
                where o.executors= :value1
            """,{'value1': executors_or_command})
        elif (dir=='thresholds') and (executors_or_command=='all'):
            result=db.session.execute("""
                select t.* from thresholds t
                order by t.id
            """)
        elif (dir=='executors'):
            result=db.session.execute('select * from orders o where o.executors= :value1',{'value1': executors_or_command})
        return jsonify({'result': [dict(row) for row in result]})

# пока пришлось отдельный API реализовать но в послествии объединим
@main_app.route('/orders/<string:command>', methods=['GET', 'POST'])
def main_orders(command):
    if request.method == "POST":
        # print(content)
        print(request.is_json)
        json = request.get_json()
        print("FrontEnd: ", json)
        if (command=='status'):
            result=[{'status': json["status"], 'date_change': json["date_change"], 'id': int(json["id"])}]
            print("BackEnd: ",result)
            db.session.execute('update orders set status= :status, date_change= :date_change where id= :id',result)
        if (command=='update'):
            result=[{'id_scope_dir': json["id_scope_dir"], 'parameters': json["parameters"], 'executors': json["executors"], 'date_change': json["date_change"], 'id': int(json["id"])}]
            print("BackEnd: ",result)
            db.session.execute('update orders set id_scope_dir= :id_scope_dir , parameters= :parameters , executors= :executors, date_change= :date_change where id= :id',result)
            result=[{'job_frequency': json["job_frequency"], 'job_frequency_type': json["job_frequency_type"], 'id_orders': int(json["id"])}]
            print("BackEnd: ",result)
            db.session.execute('update scheduler_dir set job_frequency= :job_frequency , job_frequency_type= :job_frequency_type where id_orders= :id_orders',result)
        if (command=='insert'):
            date_create=datetime.now()
            status = "stop"
            result=[{'id_users':json["id_users"],'id_scope_dir':json["id_scope_dir"],'parameters': json["parameters"], 'executors': json["executors"],'date_create':date_create,'status':status}]
            print("BackEnd: ",result)
            resultproxy=db.session.execute("""
            insert into orders (id, id_users, id_scope_dir, parameters, executors, date_create, status) 
            values ((select max(id) from orders o)+1, :id_users, :id_scope_dir, :parameters, :executors, :date_create, :status) RETURNING id
            """,result)
            # id=result.fetchone()
            result_order=[{column: value for column, value in rowproxy.items()} for rowproxy in resultproxy]
            print("BackEnd: ",result_order)
            job_script = "python3 templates/"
            result=[{'id_orders':result_order[0]['id'],'job_frequency':json["job_frequency"],'job_frequency_type': json["job_frequency_type"], 'job_script': job_script}]
            print("BackEnd: ",result)
            resultproxy=db.session.execute("""
            insert into scheduler_dir (id, id_orders, job_frequency, job_frequency_type, job_script) values 
            ((select max(id) from scheduler_dir o)+1, :id_orders, :job_frequency, :job_frequency_type, :job_script) RETURNING id
            """,result)
            result_scheduler_dir=[{column: value for column, value in rowproxy.items()} for rowproxy in resultproxy]
            result=[{'orders':result_order[0]['id'], 'scheduler_dir':result_scheduler_dir[0]['id']}]
        # if (command=='delete'):
        #     db.session.execute('delete from test where id= :value1',{'value1': int(json["id"])})
        db.session.commit()
        # пример [{"id":"1","context1":"xyz123"}]
        # и тогда
        # print(content[0]["id"])
        # пример {"id":"1","context1":"xyz123"}
        # и тогда
        # print(content["id"])
        return jsonify({'result': [dict(row) for row in result]})

    if request.method == "GET":
        json = request.get_json()
        if (command=='all'):
          result=db.session.execute('select o.id, sd.id as id_scope_dir, sd.name, sd.describe, o.parameters, o.executors, sd2.job_frequency, sd2.job_frequency_type, o.status from orders o inner join scope_dir sd on sd.id=o.id_scope_dir inner join scheduler_dir sd2 on o.id=sd2.id_orders order by o.id');
        elif (command=='thresholds'):
          print(request.args.get('id_orders'))
          result=db.session.execute('select * from thresholds t2 where t2.id_orders= :value1',{'value1': request.args.get('id_orders')});
          # result=models.db.session.execute('select * from thresholds t2')
        else:
          result={}
        return jsonify({'result': [dict(row) for row in result]})
        # data = json.loads(request.json)
        # text = data.get("text",None)
        # if text is None:
        #   return jsonify({"message":"text not found"})
        # else:
        #   return jsonify(data)


@main_app.route('/test/<string:command>', methods=['GET', 'POST'])
def test_post(command):
    if request.method == "POST":
      # return "Вот это пост!"
      # print(request.get_json())
      # return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
      #   content = request.json
        # print(content)
        print(request.is_json)
        json = request.get_json()
        print(json['context1'])
        if (command=='update'):
          db.session.execute('update test set context1= :value1 where id= :value2',{'value1': json["context1"], 'value2': int(json["id"])})
        if (command=='insert'):
          db.session.execute('insert into test (context1) VALUES ( :value1)',{'value1': json["context1"]})
        if (command=='delete'):
          db.session.execute('delete from test where id= :value1',{'value1': int(json["id"])})
        db.session.commit()
        # пример [{"id":"1","context1":"xyz123"}]
        # и тогда
        # print(content[0]["id"])
        # пример {"id":"1","context1":"xyz123"}
        # и тогда
        # print(content["id"])
        return jsonify(json)

    if request.method == "GET":
        content = request.get_json()
        return jsonify(content)
        # data = json.loads(request.json)
        # text = data.get("text",None)
        # if text is None:
        #   return jsonify({"message":"text not found"})
        # else:
        #   return jsonify(data)


@main_app.route('/specification', methods=['GET', 'POST'])
# @login_required
def specification():
    return render_template('specification.html', user=current_user)


@main_app.route('/react_1', methods=['GET', 'POST'])
# @login_required
def react_1():
    return render_template('react_1.html', user=current_user)


@main_app.route('/main', methods=['GET', 'POST'])
# @login_required
def main():
    # Assuming that there is a name property on your user object
    # returned by the callback
    if current_user.is_authenticated:
        if request.method == "GET":
            # orders = [{
            #     "name": "ping",
            #     "parameter": "inclouds.bizml.ru"
            # },
            #     {
            #         "name": "http_get",
            #         "parameter": "https://inclouds.bizml.ru"
            #     }
            # ]
            # metrics = ['ping - inclouds.bizml.ru','http_get - https://inclouds.bizml.ru']
            #
            #
            #
            # return render_template('main.html', user=current_user, metrics=metrics, orders=orders)
            # для тестирования попробуем закачать
            users=db.session.execute('select * from users sd order by id')
            users=[dict(row) for row in users]
            scope_dir=db.session.execute('select * from scope_dir sd order by id')
            scope_dir=[dict(row) for row in scope_dir]
            result1=db.session.execute('select * from test order by id')
            result1=[dict(row) for row in result1]
            result=db.session.execute("""
            select o.id, sd.id as id_scope_dir, sd.name, sd.describe, o.parameters, o.executors, o.status, sd2.job_frequency, sd2.job_frequency_type  from orders o 
                    inner join scope_dir sd on sd.id=o.id_scope_dir 
                    inner join users us on us.id=o.id_users 
                    inner join scheduler_dir sd2 on o.id=sd2.id_orders 
                    where us.login= :login order by o.id
                    """,{'login': current_user.login})
            result=[dict(row) for row in result]
            print("result: ", result)

            return render_template('main.html', user=current_user, orders=result, test=result1, scope_dir=scope_dir, users=users, msk_scope=app_configs.get('MSK_SCOPE'))
    else:
        return render_template('index.html')

@main_app.route('/chart_datetime', methods=['POST','GET'])
def chart_datetime_picker():
    if request.method == "GET":
        if current_user.is_authenticated:
            id_orders=request.args.get('id_orders')
            datetime_start=request.args.get('datetime_start')
            datetime_end=request.args.get('datetime_end')
            print(id_orders," - from: ",datetime_start, ' to: ',datetime_end)
            print(app_configs)
            if datetime_start!=None:
                datetime_start=datetime.strptime(request.args.get('datetime_start'),'%Y-%m-%d %H:%M')
            else:
                datetime_start=datetime.now()-timedelta(minutes=15)
                print(datetime_start)
            if datetime_end!=None:
                datetime_end=datetime.strptime(request.args.get('datetime_end'),'%Y-%m-%d %H:%M')
                print(datetime_end)
            else:
                datetime_end=datetime.now()
            return render_template('chart_plotly.html', user=current_user, id_orders=id_orders, datetime_start=datetime_start, datetime_end=datetime_end, msk_scope=app_configs.get('MSK_SCOPE'))
        else:
            return render_template('index.html')


@main_app.route('/scheduler_dir/<string:executors>', methods=['POST','GET'])
def scheduler_dir(executors):
    if request.method == "GET":
        result=db.session.execute('select sd.* from scheduler_dir sd, orders o2 where sd.id_orders = o2.id and o2.executors=  :value1',{'value1': executors})
        return jsonify({'result': [dict(row) for row in result]})


@main_app.route('/scope_dir', methods=['POST','GET'])
def scope_dir():
    if request.method == "GET":
        result=db.session.execute('select * from scope_dir sd order by id')
        return jsonify({'result': [dict(row) for row in result]})


# @cache.clear()
# @inclouds.after_request
@main_app.route('/chart_plotly', methods=['GET', 'POST'])
def chart_plotly():
    # cache.init_app(main_app, config=config)
    # Assuming that there is a name property on your user object
    # returned by the callback
    if current_user.is_authenticated:

        rng = pd.date_range('1/1/2011', periods=7500, freq='H')
        ts = pd.Series(np.random.randn(len(rng)), index=rng)

        graphs = [
            dict(
                data=[
                    dict(
                        x=[1, 2, 3, 4, 5, 6, 7],
                        y=[11, 22, 30, 5, 15, 25, 77],
                        type='scatter'
                    ),
                ],
                layout=dict(
                    title='первый график'
                )
            ),

            dict(
                data=[
                    dict(
                        x=[1, 3, 5, 2],
                        y=[10, 50, 30, 15],
                        type='bar'
                    ),
                ],
                layout=dict(
                    title='второй график'
                )
            ),

            dict(
                data=[
                    dict(
                        x=ts.index,  # Can use the pandas data structures directly
                        y=ts
                    )
                ],
                layout=dict(
                    title='третий график'
                )
            )
        ]

        # Add "ids" to each of the graphs to pass up to the client
        # for templating
        ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

        # Convert the figures to JSON
        # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
        # objects to their JSON equivalents
        graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

        # return 'Hello %s!' % current_user.name
        return render_template('chart_plotly.html', user=current_user, ids=ids, graphJSON=graphJSON)
    else:
        return render_template('index.html')
