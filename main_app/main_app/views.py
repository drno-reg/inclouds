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




@main_app.route('/main', methods=['GET', 'POST'])
# @login_required
def main():
    # Assuming that there is a name property on your user object
    # returned by the callback
    if current_user.is_authenticated:
        # return 'Hello %s!' % current_user.name
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
        result=db.session.execute('select o.id, sd.name, sd.describe, o.parameters, o.executors from orders o inner join scope_dir sd on sd.id=o.id_scope_dir inner join users us on us.id=o.id_users where us.login= :value1',{'value1': current_user.login})
        result=[dict(row) for row in result]
        # print("result: ", result)

        return render_template('main.html', user=current_user, orders=result)
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


@main_app.route('/orders/<string:executors>', methods=['POST','GET'])
def orders(executors):
    if request.method == "GET":
        result=db.session.execute('select * from orders o where o.executors= :value1',{'value1': executors})
        return jsonify({'result': [dict(row) for row in result]})


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
