import sys
import time
import requests
import datetime

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        token=sys.argv[1]
        bot_chatID=sys.argv[2]
        bot_message=sys.argv[3]
        print("Exist values on enter: token=",token,"; bot_chatID=",bot_chatID)
    # Если нет данных то штем тестовое сообщение с тестовый Telegram Chat
    else:
        token='1437446131:AAGDZsBcE1F_ZYfO8d2_axmeS45-xFXJprM'
        bot_chatID='375749506'
        # bot_chatID='-237542414'
        # bot_chatID="153389366"
        print("Start test, because absent values on enter: token=",token,"; bot_chatID=",bot_chatID)
        # Выполняем пробное подключение к API Telegram
        url='https://api.telegram.org/bot'+token+'/getUpdates'
        start_time=datetime.datetime.now()
        print("Начало. Время: ",start_time)
        print(url)
        r=requests.get(url)
        print(r)
        HTML_HEADER=r.headers
        HTML_BODY=r.text
        print(HTML_BODY)
        bot_message="""
        <b>bold</b>, <strong>bold</strong> <i>italic</i>, <em>italic</em>
        <a href="http://www.example.com/">inline URL</a>
        <a href="tg://user?id=123456789">inline mention of a user</a>
        <code>inline fixed-width code</code>
        <pre>pre-formatted fixed-width code block</pre>
        """

        bot_message="""
        <b>Alarm: </b> Событие по точке inclouds.bizml.ru
        <code>inline fixed-width code</code>
        <pre>pre-formatted fixed-width code block</pre>
        """

        datetime_start=datetime.datetime.now()-datetime.timedelta(minutes=15)
        # datetime_start=datetime.strptime(request.args.get('datetime_start'),'%Y-%m-%d %H:%M')
        print(datetime_start)
        datetime_end=datetime.datetime.now()+datetime.timedelta(minutes=15)
        bot_message="""
        <b>Alarm! Open: 08.11.2020 21:56</b> 
        <pre>Событие по точке tech.rtb.mts.ru</pre>
         <a href="https://inclouds.bizml.ru/chart_datetime?id_orders=6&id_scope_describe=http_get%20-%20https://tech.rtb.mts.ru&datetime_start={}&datetime_end={}">Посмотреть график</a>
        
        <code>Латентность более 10 секунд</code>
    
        """.format(f"{datetime_start:%Y-%m-%d %H:%M}", f"{datetime_end:%Y-%m-%d %H:%M}")

        bot_message="""\"
        <b>Critical_Open: """+f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"+"""</b> 
        <pre>Значение метрики: = 10 вышло за критический порог  с  повторениями </pre>
        <a href="https://inclouds.bizml.ru/chart_datetime?id_orders={}&id_scope_describe={}&datetime_start={}&datetime_end={}">Посмотреть график</a>
        \"""".format(6,'0.01',f"{datetime_start:%Y-%m-%d %H:%M}",f"{datetime_end:%Y-%m-%d %H:%M}")


    # url='https://api.telegram.org/bot'+token+'/sendMessage?chat_id=' + bot_chatID + '&text=' + bot_message+'&parse_mode=html'
    # r=requests.get(url)

    # переделываем на другой формат
    params ={
        "chat_id":bot_chatID,
        "text": bot_message,
        "parse_mode": "HTML",
    }
    r=requests.get(
        "https://api.telegram.org/bot{}/sendMessage".format(token),
        params=params
    )
    print(r)
    HTML_HEADER=r.headers
    HTML_BODY=r.text
    print(HTML_BODY)
