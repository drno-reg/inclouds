# не свое
import schedule
import time
import os
from sqlalchemy.orm import sessionmaker
import datetime
import threading
from subprocess import Popen, PIPE, STDOUT
import shlex
# свое
from models import engine, metadata, scope_dir, scope_store, scheduler_dir, scheduler_log

def job():
    print("I'm working...")
    stream = os.popen('cd ~ %% ls -las')
    output = stream.read()
    print(str(output))

def get_simple_cmd_output(cmd, stderr=STDOUT):
    """
    Execute a simple external command and get its output.
    """
    args = shlex.split(cmd)
    return Popen(args, stdout=PIPE, stderr=stderr).communicate()[0]

def main_job():
    Session = sessionmaker(bind=engine)
    session = Session()
    # result_scheduler_dir = session.query(scheduler_dir).all()
    result_scheduler_dir=session.execute('select sd.*, sd2.*, o.* from scheduler_dir sd inner join orders o on o.id = sd.id_orders inner join scope_dir sd2 on sd2.id =o.id_scope_dir ').fetchall()
    print(result_scheduler_dir)

    for row in result_scheduler_dir:
        # session.execute(scheduler_log.insert(), result_row)
        # выбираем по id самую последнюю запись
        result_scheduler_log=session.execute('select * from scheduler_log s1 where s1.id in (select max(id) from scheduler_log s2 where s2.id_scheduler_dir= :value1 order by s2.job_start desc limit 1)',{'value1': row.id}).fetchall()
        # result_scheduler_log=session.execute('select * from scheduler_log s1 where s1.id in (select max(id) from scheduler_log s2 where s2.id_scheduler_dir= :value1 and s2.job_status<> :value2 and s2.job_log= :value3 order by s2.job_start desc limit 1)',{'value1': row.id, 'value2': 'wait', 'value3': None}).fetchall()
        print(result_scheduler_log)
        # print(dir(result_scheduler_log))
        # для первого запуска, если база пустая
        if (len(result_scheduler_log)==0):
            print(row.job_frequency)
            print(datetime.datetime.now().time())
            job_start=datetime.datetime.now()+datetime.timedelta(seconds=int(row.job_frequency))
            print(job_start)
            date_time_obj = datetime.datetime.strptime(str(job_start), '%Y-%m-%d %H:%M:%S.%f')
            print(date_time_obj)
            result_row=[{'id_scheduler_dir':row.id,'job_status':'wait','job_start':date_time_obj,'job_end':datetime.datetime.now()}]
            print(result_row)
            session.execute(scheduler_log.insert(), result_row)
            session.commit()
        for row1 in result_scheduler_log:
            row_as_dict = dict(row1)
            if (row_as_dict.get('job_status')=='done'):
                print(row.job_frequency)
                print(datetime.datetime.now().time())
                job_start=datetime.datetime.now()+datetime.timedelta(seconds=int(row.job_frequency))
                print(job_start)
                date_time_obj = datetime.datetime.strptime(str(job_start), '%Y-%m-%d %H:%M:%S.%f')
                print(date_time_obj)
                result_row=[{'id_scheduler_dir':row.id,'job_status':'wait','job_start':date_time_obj,'job_end':datetime.datetime.now()}]
                print(result_row)
                session.execute(scheduler_log.insert(), result_row)
                session.commit()
            if (row_as_dict.get('job_status')=='wait'):
                print('Find - id: ', row_as_dict.get('id'), ", job_start: ", row_as_dict.get('job_start'), ', job_log: ', row_as_dict.get('job_log'))
                delta_time=abs(datetime.datetime.now()-datetime.datetime.strptime(str(row_as_dict.get('job_start')), '%Y-%m-%d %H:%M:%S.%f'))
                print('Calculating delta - ', delta_time, ' between now: ', datetime.datetime.now(), ' and job_start: ',row_as_dict.get('job_start'))
                print('Delta in seconds: ', abs(delta_time.seconds))
                if (datetime.datetime.now()>datetime.datetime.strptime(str(row_as_dict.get('job_start')), '%Y-%m-%d %H:%M:%S.%f')) and (delta_time.seconds>3):
                    print('Need update')
                    job_start=datetime.datetime.now()+datetime.timedelta(seconds=int(row.job_frequency))
                    date_time_obj = datetime.datetime.strptime(str(job_start), '%Y-%m-%d %H:%M:%S.%f')
                    result_row=[{'id_scheduler_dir':row_as_dict.get('id'),'job_status':'wait','job_start':date_time_obj,'job_end':datetime.datetime.now()}]
                    print('Updating job_start: ', date_time_obj)
                    session.execute('update scheduler_log set job_start= :value1 where id= :value2', {'value1': date_time_obj, 'value2': row_as_dict.get('id')})
                    session.commit()
                if (delta_time.seconds<3):
                    # script=row.job_script+" "+str(row_as_dict.get('id'))
                    # формируемспископараметровтаким образом
                    # пример python3 templates/template_http_get.py inclouds.bizml.ru 2 5
                    # select sd.*, sd2.*, o.* from scheduler_dir sd inner join orders o on o.id = sd.id_orders inner join scope_dir sd2 on sd2.id =o.id_scope_dir
                    # итого scheduler_dir.job_script | scope_dir.template | orders.id_orders | orders.parameters | id_scheduler_dir.id
                    # пример python3 templates/template_http_get.py inclouds.bizml.ru 5 10
                    script=row.job_script+row.template+" "+str(row.parameters)+" "+str(row.id_orders)+" "+str(row.id)+" "+str(row_as_dict.get('id'))
                    print('Start run job ', row_as_dict.get('id'), ' script: ', script)
                    def start_job(job_script):
                        result = str(get_simple_cmd_output(job_script))
                        # session.execute('update scheduler_log set job_stop= :value1 and job_status= :value2 where id= :value3', {'value1': datetime.datetime.now(), 'value2': 'done','value3': row_as_dict.get('id')})
                        # session.commit()
                        print(result)
                    x = threading.Thread(target=start_job, args=(script,))
                    x.daemon=True
                    x.start()

schedule.every(10).seconds.do(main_job)
# schedule.every(1).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)
