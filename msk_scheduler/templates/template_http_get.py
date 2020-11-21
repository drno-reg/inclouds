# предварительно необходимо установить утилиту fping
# импорт несвоего, а того, что необходимо предварительно установить
from sqlalchemy.orm import sessionmaker
import datetime
from sys import argv
import requests
# импорт своего
import env_change
env_change.os_pythonpath_change()
# print(dir(pythonpath_change))
print(env_change.os_pythonpath_change.__doc__)
from models import engine, metadata, scope_dir, scope_store, scheduler_log


def get_http_get_time(url):
    try:
        start_time=datetime.datetime.now()
        print("Начало. Время: ",start_time)
        print(url)

        r=requests.get(url)
        HTML_HEADER=r.headers
        HTML_BODY=r.text
        HTML_STATUS=r.status_code
        print(HTML_HEADER)
        print(HTML_STATUS)
        end_time=datetime.datetime.now()
        delta_time=end_time-start_time
        print("На подключение потрачено: ",delta_time.total_seconds(), " или ", delta_time.microseconds/1000000)
        print(delta_time.microseconds)
        print(r.status_code)
        value = delta_time.microseconds/1000000*100
    except BaseException as error:
        value = '-1'
    return value

if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    session = Session()
    # parameters = 'https://inclouds.bizml.ru'
    url = argv[1]
    id_orders = argv[2]
    try:
        # номер задания в scheduler_log
        scheduler_id = argv[3]
        job_id = argv[4]
        session.execute('update scheduler_log set job_status= :value1 where id= :value2', {'value1': 'running','value2': job_id})
        session.commit()
        print ('Working by: ', url, ' scheduler_id: ', scheduler_id, ' new_job: ', job_id)
        result=get_http_get_time(url)
        print(result,' s')
        job_end=datetime.datetime.now()
        result=[{'id_orders':id_orders,'value':result,'date':job_end}]
        session.execute(scope_store.insert(), result)
        session.execute('update scheduler_log set job_status= :value1 , job_end= :value3 , job_log= :value4 where id= :value2', {'value1': 'done','value2': job_id,'value3': job_end,'value4': str(result)})
    except IndexError:
        print ('Working by: ', url, ' id_orders: ', id_orders, ' new_job: I think it is manual start!')
        result=get_http_get_time(url)
        print(result,' s')
        job_end=datetime.datetime.now()
        result=[{'id_orders':id_orders,'value':result,'date':job_end}]
        session.execute(scope_store.insert(), result)
    session.commit()
    session.close
