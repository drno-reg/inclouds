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

def Diff(li1, li2):
    return (list(list(set(li1)-set(li2)) + list(set(li2)-set(li1))))


def refresh_table(table_name, keys, sql, insert, update):
    try:
        url=app_configs.get("URL_"+table_name)
        start_time=datetime.datetime.now()
        print("Compare ",table_name," use url=",url,". Start. Start_time: ",start_time)
        r=requests.get(url)
        HTML_HEADER=r.headers
        HTML_BODY=r.text
        HTML_STATUS=r.status_code
        print(HTML_HEADER)
        print(HTML_STATUS)
        print(HTML_BODY)
        end_time=datetime.datetime.now()
        delta_time=end_time-start_time
        print("Time request: ",delta_time.total_seconds(), " or ", delta_time.microseconds/1000000)
        print(delta_time.microseconds)
        print(r.status_code)
        value = delta_time.microseconds/1000000*100
        data = json.loads(HTML_BODY)
        print("Main: ",data["result"])
        print("Context: ",sql)
        scope=models.db.session.execute(sql)
        scope=[dict(row) for row in scope]
        print("Scope: ",scope)
        for entry_main in data["result"]:
            print("Main id: ",entry_main['id'])
            # keys_context=[]
            keys_context={}
            for i in keys:
                # делаем [{'id':entry_main["id"]}]
                keys_context[i]=entry_main[i]
                # keys_context.append([{i:entry_main[i]}])
            print(keys_context)
            if (len(scope)==0):
                # print("Scope=0 Insert: ", result)
                # print("Context: ",insert)
                # conn.execute(scope_dir.insert(), result)
                models.db.session.execute(insert, keys_context)
            else:
                id=""
                for entry_scope in scope:
                    # print("scope id: ",entry_scope["id"])
                    if (entry_scope['id']==entry_main['id']):
                        id=entry_main["id"]
                if (id==""):
                    # print("Context: ",insert)
                    # print("Scope<>0 Insert: ", entry_main['id'])
                    models.db.session.execute(insert, keys_context)
                elif (id!=""):
                    # print("Context: ",update)
                    # print("Scope<>0 Update: ", entry_main['id'])
                    models.db.session.execute(update, keys_context)
        result="Update done"
    except BaseException as error:
        result="table_name: ",error
        print(result)
    models.db.session.commit()
    models.db.session.close()
    return result


table_name="SCOPE_DIR"
keys = ["id", "name","describe","template"]
# keys=[{'id':entry_main["id"],'name':entry_main["name"],'describe':entry_main["describe"],'template':entry_main["template"]}]
sql="select * from SCOPE_DIR sd order by id"
insert="INSERT INTO SCOPE_DIR VALUES( :id, :name, :describe, :template)"
update="UPDATE SCOPE_DIR set name= :name, describe= :describe, template= :template where id= :id"

refresh_table(table_name, keys, sql, insert, update)

table_name="ORDERS"
keys = ["id", "id_users","id_scope_dir","parameters","executors","date_create","date_change","status"]
sql="select * from ORDERS sd order by id"
insert="INSERT INTO ORDERS VALUES( :id, :id_users, :id_scope_dir, :parameters, :executors, :date_create, :date_change, :status)"
update="""
       UPDATE ORDERS set id_users= :id_users, id_scope_dir= :id_scope_dir, parameters= :parameters, executors= :executors, 
                         date_create= :date_create, date_change= :date_change, status= :status where id= :id
       """

refresh_table(table_name, keys, sql, insert, update)

table_name="SCHEDULER_DIR"
keys = ["id", "id_orders","job_frequency","job_frequency_type","job_script"]
sql="select * from SCHEDULER_DIR sd order by id"
insert="INSERT INTO SCHEDULER_DIR VALUES( :id, :id_orders, :job_frequency, :job_frequency_type, :job_script)"
update="""
       UPDATE SCHEDULER_DIR set id_orders= :id_orders, job_frequency= :job_frequency, job_frequency_type= :job_frequency_type, job_script= :job_script
                            where id= :id
       """

refresh_table(table_name, keys, sql, insert, update)

table_name="THRESHOLDS"
keys = ["id", "id_orders","minor_1","minor_2","minor_count","minor_conditions","warning_1","warning_2","warning_count","warning_conditions","critical_1","critical_2","critical_count","critical_conditions","telegram_token","telegram_chatid"]
sql="select * from THRESHOLDS sd order by id"
insert="""INSERT INTO THRESHOLDS 
          VALUES( :id, :id_orders, 
                  :minor_1, :minor_2, :minor_count, :minor_conditions, 
                  :warning_1, :warning_2, :warning_count, :warning_conditions, 
                  :critical_1, :critical_2, :critical_count, :critical_conditions, 
                  :telegram_token, :telegram_chatid)
        """
update="""
       UPDATE THRESHOLDS set id_orders= :id_orders, 
                             minor_1= :minor_1, minor_2= :minor_2, minor_count= :minor_count, minor_conditions= :minor_conditions,
                             warning_1= :warning_1, warning_2= :warning_2, warning_count= :warning_count, warning_conditions= :warning_conditions, 
                             critical_1= :critical_1, critical_2= :critical_2, critical_count= :critical_count, critical_conditions= :critical_conditions,
                             telegram_token= :telegram_token,telegram_chatid= :telegram_chatid
                            where id= :id
       """

refresh_table(table_name, keys, sql, insert, update)


