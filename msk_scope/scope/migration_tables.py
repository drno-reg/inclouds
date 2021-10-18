import requests
import datetime
import json
from sys import argv
# импорт своего
import env_change
env_change.os_pythonpath_change()
# print(dir(pythonpath_change))
print(env_change.os_pythonpath_change.__doc__)

from scope import scope, logging, models, db, app_configs

# from models import engine, metadata, scope_dir, scope_store, scheduler_log, orders, scheduler_dir

def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))

#
# refresh_table(table_name, keys, sql, insert, update)
# url=app_configs.get("URL_"+table_name)
# url = "http://localhost:5000/orders/scheduler_log/insert"
table_name = argv[1]
id_num = argv[2]

url=app_configs.get("URL_"+table_name.upper())
sql="select * from scheduler_log sl where sl.id< :id"
result=models.db.session.execute(sql, {'id':id_num})
result=[dict(row) for row in result]
print(len(result))
for i in range (0, len(result)):
    print(result[i])
    # context=[{'id_orders': result[i].get('id_orders'),'job_status': result[i].get('job_status'),'job_start': result[i].get('job_start'),'job_end': result[i].get('job_end'),'job_log': result[i].get('job_log')}]
    # print(context)
    # print(result[i].get('id_orders'))
    result_request=requests.post(url, json=result[i])
    print(result_request.status_code)
    if (result_request.status_code==200):
        print(result_request.json())
        delete="DELETE FROM scheduler_log WHERE id = :id"
        print("Удаляю: ",result[i].get('id'))
        resultproxy=models.db.session.execute(delete, {'id':result[i].get('id')})
        # result=[{column: value for column, value in rowproxy.items()} for rowproxy in resultproxy]
        print(resultproxy)
        models.db.session.commit()
models.db.session.close
