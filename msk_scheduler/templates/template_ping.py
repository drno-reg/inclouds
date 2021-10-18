# предварительно необходимо установить утилиту fping
# импорт не свеого - того, что необходимо предварительно установить
import shlex
from subprocess import Popen, PIPE, STDOUT
from sqlalchemy.orm import sessionmaker
import datetime
from sys import argv
# импорт своего
import env_change
env_change.os_pythonpath_change()
# print(dir(pythonpath_change))
print(env_change.os_pythonpath_change.__doc__)
# можно написать так но не знаю какой паттерн лучше
# from env_change import os_pythonpath_change
# os_pythonpath_change()
# print(dir(os_pythonpath_change))
from models import engine, metadata, scope_dir, scope_store, scheduler_log
import thresholds


def get_ping_time(host):
    host = host.split(':')[0]
    cmd = "fping {host} -C 3 -q".format(host=host)
    # result = str(get_simple_cmd_output(cmd)).replace('\\','').split(':')[-1].split() if x != '-']
    result = str(get_simple_cmd_output(cmd)).replace('\\', '').split(':')[-1].replace("n'", '').replace("-",'').replace("b''", '').split()
    res = [float(x) for x in result]
    if len(res) > 0:
        return sum(res) / len(res)
    else:
        return -1

def get_simple_cmd_output(cmd, stderr=STDOUT):
    """
    Execute a simple external command and get its output.
    """
    args = shlex.split(cmd)
    return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]


def main():
    # sample hard code for test
    host = 'google.com'
    print([host, get_ping_time(host)])
    host = 'inclouds.bizml.ru'
    print([host, get_ping_time(host)])

def scope_checkers_ping(host):
    result = [host, get_ping_time(host)]
    return result

if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    session = Session()
    # host = 'inclouds.bizml.ru'
    # host
    # id_orders - идентификатор заказа
    host = argv[1]
    id_orders = argv[2]
    print(len(argv))
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
            print ('Working by: ', host, ' order_id: ', id_orders, ' new_job: ', job_id)
            value=get_ping_time(host)
            print(value, ' ms or ',int(value)/1000,' s')
            job_end=datetime.datetime.now()
            result=[{'id_orders':id_orders,'value':int(value)/1000,'date':job_end}]
            session.execute(scope_store.insert(), result)
            session.execute('update scheduler_log set job_status= :value1 , job_end= :value3 , job_log= :value4 where id= :value2', {'value1': 'done','value2': job_id,'value3': job_end,'value4': str(result)})
            session.commit()
            # генерим открывающие и закрывающие уведомления
            thresholds.create_thresholds_events(id_orders, value)
        # тестируем и измерение и отправку уведомления
        elif (len(argv)>3) and (argv[3]=="test_critical"):
            print ('Working by: ', host, ' id_orders: ', id_orders, ' new_job: I think it is manual start!')
            value=get_ping_time(host)
            print(value, ' ms or ',int(value)/1000,' s')
            job_end=datetime.datetime.now()
            result=[{'id_orders':id_orders,'value':int(value)/1000,'date':job_end}]
            session.execute(scope_store.insert(), result)
            session.commit()
            # для тестирования отправки уведомлений в Telegram Chat
            # в таком решении есть большой минус, если будет латентность Telegram API то может значительно увеличиться общее время работы подпроцесса по вычислению метрики
            # но в таком случае как вариант сгенерировать дополнительный подпроцесс по отправке уведомлений
            print("Testing send critical message to Telegram Chat")
            thresholds.create_thresholds_events(id_orders, value)
        elif (len(argv)==3):
            print ('Working by: ', host, ' id_orders: ', id_orders, ' new_job: I think it is manual start!')
            value=get_ping_time(host)
            print(value, ' ms or ',int(value)/1000,' s')
            job_end=datetime.datetime.now()
            result=[{'id_orders':id_orders,'value':int(value)/1000,'date':job_end}]
            session.execute(scope_store.insert(), result)
            # return 'Thinking this is manual start'
    except IndexError:
        print("Error")
    session.commit()
    session.close
