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
import thresholds

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
        print("Завершено. Время: ",end_time)
        delta_time=end_time-start_time
        print("На подключение потрачено: ",delta_time.total_seconds(), " или ", delta_time.microseconds/1000000)
        print(delta_time.microseconds)
        print(r.status_code)
        # value = delta_time.microseconds/1000000*100
        value = delta_time.microseconds/1000000
    except BaseException as error:
        value = '-1'
    return value


if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    session = Session()
    # parameters = 'https://inclouds.bizml.ru'
    # в вход подаем
    # url
    # id_orders - идентификатор заказа
    url = argv[1]
    id_orders = argv[2]
    print(len(argv),": url - ",url,", id_orders: ",id_orders)
    try:
        # важный порядок:
        # - обновляем статус в scheduler_log на running чтобы главный job понял, что по этой задаче уже есть исполнитель
        # - вычисляем значение метрики и insert новое значение в scope_store
        # - обновляем статус в scheduler_log на done
        # - проверяем есть ли threshold на эту метрику и отправляем Alarm
        if (len(argv)>3) and (argv[3]!="test_critical"):
            job_id = argv[3]
            session.execute('update scheduler_log set job_status= :value1 where id= :value2', {'value1': 'running','value2': job_id})
            session.commit()
            print ('Working by: ', url, ' order_id: ', id_orders, ' new_job: ', job_id)
            value=get_http_get_time(url)
            print(value,' s')
            job_end=datetime.datetime.now()
            result=[{'id_orders':id_orders,'value':value,'date':job_end}]
            session.execute(scope_store.insert(), result)
            session.execute('update scheduler_log set job_status= :value1 , job_end= :value3 , job_log= :value4 where id= :value2', {'value1': 'done','value2': job_id,'value3': job_end,'value4': str(result)})
            session.commit()
            # генерим открывающие и закрывающие уведомления
            thresholds.create_thresholds_events(id_orders, value)
        # тестируем и измерение и отправку уведомления
        elif (len(argv)>3) and (argv[3]=="test_critical"):
            print ('Working by: ', url, ' id_orders: ', id_orders, ' new_job: I think it is manual start!')
            value=get_http_get_time(url)
            print(value,' s')
            job_end=datetime.datetime.now()
            result=[{'id_orders':id_orders,'value':value,'date':job_end}]
            session.execute(scope_store.insert(), result)
            session.commit()
            # print(len(argv))
            # для тестирования отправки уведомлений в Telegram Chat
            # в таком решении есть большой минус, если будет латентность Telegram API то может значительно увеличиться общее время работы подпроцесса по вычислению метрики
            # но в таком случае как вариант сгенерировать дополнительный подпроцесс по отправке уведомлений
            print("Testing send critical message to Telegram Chat")
            thresholds.create_thresholds_events(id_orders, value)
        elif (len(argv)==3):
            # тестируем просто измерение и загрузку в store
            print ('Working by: ', url, ' id_orders: ', id_orders, ' new_job: I think it is manual start!')
            value=get_http_get_time(url)
            print(value,' s')
            job_end=datetime.datetime.now()
            result=[{'id_orders':id_orders,'value':value,'date':job_end}]
            session.execute(scope_store.insert(), result)
    except IndexError:
        print("Error")
    session.commit()
    session.close
