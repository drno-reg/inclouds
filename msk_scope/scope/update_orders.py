import requests
import datetime
import json
# импорт своего
import env_change
env_change.os_pythonpath_change()
# print(dir(pythonpath_change))
print(env_change.os_pythonpath_change.__doc__)

from scope import scope, logging, models, db, app_configs

# from models import engine, metadata, scope_dir, scope_store, scheduler_log, orders, scheduler_dir

try:
    url=app_configs.get('URL_SCOPE_DIR')
    start_time=datetime.datetime.now()
    print("Начало. Время: ",start_time)
    print(url)
    r=requests.get(url)
    HTML_HEADER=r.headers
    HTML_BODY=r.text
    HTML_STATUS=r.status_code
    print(HTML_HEADER)
    print(HTML_STATUS)
    print(HTML_BODY)
    end_time=datetime.datetime.now()
    delta_time=end_time-start_time
    print("На подключение потрачено: ",delta_time.total_seconds(), " или ", delta_time.microseconds/1000000)
    print(delta_time.microseconds)
    print(r.status_code)
    value = delta_time.microseconds/1000000*100
    data = json.loads(HTML_BODY)
    keys = ["id", "name","describe","template"]
    # conn = engine.connect()
    print(data["result"])
    for entry in data["result"]:
        # print(entry["id"])
        # print(entry)
        values = [entry.get(key, None) for key in keys]
        # print(values)
        try:
            result=[{'id':entry["id"],'name':entry["name"],'describe':entry["describe"],'template':entry["template"]}]
            print(result)
            # conn.execute(scope_dir.insert(), result)
            models.db.session.execute('INSERT INTO scope_dir VALUES( :id, :name, :describe, :template)', result)
            print("Ready")
        except BaseException as error:
            print("Error update scope_dir", error)
except BaseException as error:
    print(error)


try:
    url=app_configs.get('URL_ORDERS')
    start_time=datetime.datetime.now()
    print("Начало. Время: ",start_time)
    print(url)
    r=requests.get(url)
    HTML_HEADER=r.headers
    HTML_BODY=r.text
    HTML_STATUS=r.status_code
    print(HTML_HEADER)
    print(HTML_STATUS)
    print(HTML_BODY)
    end_time=datetime.datetime.now()
    delta_time=end_time-start_time
    print("На подключение потрачено: ",delta_time.total_seconds(), " или ", delta_time.microseconds/1000000)
    print(delta_time.microseconds)
    print(r.status_code)
    value = delta_time.microseconds/1000000*100
    data = json.loads(HTML_BODY)
    keys = ["id", "id_users","id_scope_dir","parameters","executors","date"]
    # conn = engine.connect()
    print(data["result"])
    for entry in data["result"]:
        # print(entry["id"])
        # print(entry)
        values = [entry.get(key, None) for key in keys]
        # print(values)
        # dict(row) for row in result
        # cmd = """INSERT INTO orders VALUES(
        #             ?,
        #             ?,
        #             ?,
        #             ?,
        #             ?,
        #             ?
        #         );"""
        # conn.execute(cmd, values)
        # print(datetime.datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p'))
        # print(datetime.datetime.strptime('Mon, 16 Nov 2020 13:35:55 GMT', '%a, %d %b %Y %H:%M:%S %Z'))
        # приходится делать конвертацию времени т.к. через API оно приходит в таком формате
        try:
            result=[{'id':entry["id"],'id_users':entry["id_users"],'id_scope_dir':entry["id_scope_dir"],'parameters':entry["parameters"],'executors':entry["executors"],'date':datetime.datetime.strptime(entry["date"], '%a, %d %b %Y %H:%M:%S %Z')}]
            # conn.execute(orders.insert(), result)
            print(result)
            # if entry["id"]==4:
            models.db.session.execute('INSERT INTO orders VALUES( :id , :id_users, :id_scope_dir, :parameters, :executors, :date)', result)
            print("Ready")
        except BaseException as error:
            print(error)
except BaseException as error:
    print(error)

try:
    url=app_configs.get('URL_SCHEDULER_DIR')
    start_time=datetime.datetime.now()
    print("Начало. Время: ",start_time)
    print(url)
    r=requests.get(url)
    HTML_HEADER=r.headers
    HTML_BODY=r.text
    HTML_STATUS=r.status_code
    print(HTML_HEADER)
    print(HTML_STATUS)
    print(HTML_BODY)
    end_time=datetime.datetime.now()
    delta_time=end_time-start_time
    print("На подключение потрачено: ",delta_time.total_seconds(), " или ", delta_time.microseconds/1000000)
    print(delta_time.microseconds)
    print(r.status_code)
    value = delta_time.microseconds/1000000*100
    data = json.loads(HTML_BODY)
    keys = ["id", "id_orders","job_frequency","job_frequency_type","job_script"]
    # conn = engine.connect()
    print(data["result"])
    for entry in data["result"]:
        print(entry["id"])
        print(entry)
        values = [entry.get(key, None) for key in keys]
        print(values)
        try:
            result=[{'id':entry["id"],'id_orders':entry["id_orders"],'job_frequency':entry["job_frequency"],'job_frequency_type':entry["job_frequency_type"],'job_script':entry["job_script"]}]
            # conn.execute(scheduler_dir.insert(), result)
            models.db.session.execute('INSERT INTO scheduler_dir VALUES( :id , :id_orders, :job_frequency, :job_frequency_type, :job_script)', result)
            print("Ready")
        except BaseException as error:
            print(error)
except BaseException as error:
    print(error)

models.db.session.commit()
models.db.session.close()
