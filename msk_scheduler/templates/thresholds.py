# импорт несвоего, а того, что необходимо предварительно установить
from sqlalchemy.orm import sessionmaker
import datetime
from sys import argv
import requests
from subprocess import Popen, PIPE, STDOUT
import shlex
# импорт своего
import env_change
env_change.os_pythonpath_change()
# print(dir(pythonpath_change))
print(env_change.os_pythonpath_change.__doc__)
from models import engine, metadata, scope_dir, scope_store, scheduler_log


def get_simple_cmd_output(cmd, stderr=STDOUT):
    """
    Execute a simple external command and get its output.
    """
    args = shlex.split(cmd)
    return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]


def create_thresholds_events(id_orders, value):
    Session = sessionmaker(bind=engine)
    session = Session()
    thresholds_result=session.execute("""
                    select sd.*, sd2.*, o.*,t2.* from scheduler_dir sd 
                    inner join orders o on o.id = sd.id_orders 
                    inner join scope_dir sd2 on sd2.id =o.id_scope_dir 
                    inner join thresholds t2 on t2.id_orders =o.id 
                    where t2.id_orders= :id
                    """,{'id':id_orders});
    thresholds_result=[dict(row) for row in thresholds_result]
    print(thresholds_result)
    datetime_start=datetime.datetime.now()-datetime.timedelta(minutes=15)
    datetime_end=datetime.datetime.now()+datetime.timedelta(minutes=15)


    if (len(thresholds_result)>0):
        # если пороги одинаковые
        if (thresholds_result[0]['critical_1']==thresholds_result[0]['critical_2']):
            print("Корридора критических значений нет, т.к. пороги одинаковые и = ",thresholds_result[0]['critical_1'])
            print("Определяем выражение для проверки: количество повторений - ", thresholds_result[0]['critical_count'], " как проверяем - ",thresholds_result[0]['critical_conditions'])
            if (thresholds_result[0]['critical_conditions']=='>'):
                scheduler_log_text="""
                                select * from scheduler_log s1 where s1.id in (select max(id) from scheduler_log s2 
                                where s2.id_orders= :value1 and s2.job_status='critical' and s2.job_end is null 
                                order by s2.job_start desc limit 1)  
                                """
                store_values=session.execute("""
                     select * from scope_store ss where ss.id_orders= :id order by ss.id DESC limit :critical_count 
                    """,{'id':id_orders, 'critical_count':thresholds_result[0]['critical_count']});
                store_values=[dict(row) for row in store_values]
                print(store_values)
                critical_count=0
                for entry_values in store_values:
                    if (entry_values['value']>thresholds_result[0]['critical_1']):
                        critical_count=critical_count+1
                job_log = "To Telegram: Send Critical_Open message"
                format_dictionary = {
                    'datetime_now': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),'id_orders': id_orders,
                    'describe':thresholds_result[0]["describe"],'parameters':thresholds_result[0]['parameters'],
                    'critical_1':thresholds_result[0]['critical_1'],'critical_count':thresholds_result[0]['critical_count'],'value':value,
                    'datetime_start': datetime_start.strftime("%Y-%m-%d %H:%M"),'datetime_end': datetime_end.strftime("%Y-%m-%d %H:%M")
                }
                if (critical_count == thresholds_result[0]['critical_count']):
                    print(value," > ",thresholds_result[0]['critical_1'])
                    # print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
                    # telegram html format <code></code>
                    telegram_message="""\"
                                    <b>Critical_Open: {datetime_now}</b> 
                                    <pre>Значение метрики: {describe} {parameters} = {value} вышло за критический порог {critical_1} с {critical_count} повторениями</pre>
                                    <a href='https://inclouds.bizml.ru/chart_datetime?id_orders={id_orders}&id_scope_describe={describe}&datetime_start={datetime_start}&datetime_end={datetime_end}'>Посмотреть график: </a>
                                    \"""".format(**format_dictionary)
                    scheduler_log_sql=session.execute(scheduler_log_text,{'value1':id_orders});
                    scheduler_log_sql=[dict(row) for row in scheduler_log_sql]
                    if (len(scheduler_log_sql)==0):
                        print(get_simple_cmd_output("python3 templates/send_message_to_telegram.py "+str(thresholds_result[0]['telegram_token'])+" "+str(thresholds_result[0]['telegram_chatid'])+" "+telegram_message))
                        print("Нет ни одной записи")
                        print(scheduler_log)
                        result_row=[{'id_orders':id_orders,'job_status':'critical','job_start':datetime.datetime.now(),'job_end':None,'job_log':job_log}]
                        session.execute(scheduler_log.insert(), result_row)
                        session.commit()
                # if (value < thresholds[0]['critical_1']):
                else:
                    print("Больше нет условий для Critical ",value," < ",thresholds_result[0]['critical_1'])
                    scheduler_log_sql=session.execute(scheduler_log_text,{'value1':id_orders});
                    scheduler_log_sql=[dict(row) for row in scheduler_log_sql]
                    print(scheduler_log_sql)
                    if (len(scheduler_log_sql)!=0):
                        telegram_message="""\"
                                        <b>Critical_Close: {datetime_now}</b> 
                                        <pre>Значение метрики: {describe} {parameters} = {value}, критический порог: {critical_1}, количество повторений: {critical_count}</pre>
                                        <a href='https://inclouds.bizml.ru/chart_datetime?id_orders={id_orders}&id_scope_describe={describe}&datetime_start={datetime_start}&datetime_end={datetime_end}'>Посмотреть график</a>
                                        \"""".format(**format_dictionary)
                        print(get_simple_cmd_output("python3 templates/send_message_to_telegram.py "+str(thresholds_result[0]['telegram_token'])+" "+str(thresholds_result[0]['telegram_chatid'])+" "+telegram_message))
                        job_log = job_log + " and send Critical_Close message"
                        session.execute('update scheduler_log set job_end= :value1, job_log= :value2 where id= :value3', {'value1': datetime.datetime.now(),'value2': job_log, 'value3': scheduler_log_sql[0]['id']})
                        session.commit()
    elif (len(thresholds_result)==0):
        print("Пороговых значений для заказа: ",id_orders," не найдено.")
    session.commit()
    session.close
