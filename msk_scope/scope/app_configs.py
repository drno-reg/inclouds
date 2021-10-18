import os

def load_file_by_lines(PATH):
    """
    читаем построчно файл где каждая строка параметр=значение и преобразовываем его в словарь
    :param PATH:
    :return:
    """
    result = []
    result_map = {}
    # print(dir(result_map))
    with open(PATH) as fp:
        line = fp.readline()
        cnt = 1
        while line:
            # print("Line {}: {}".format(cnt, line.strip()))
            line="{}".format(line.strip())
            result.append(line)
            # print(line.find('='))
            key=line[:line.find('=')]
            value=line[line.find('=')+1:]
            # print(key)
            result_map[key]=value
            line = fp.readline()
            cnt += 1
    # print(result_map)
    return result_map

def load_configs():
    """
    пробуем получить данные конфигурации сначала по локальным путям, если там нет то ищем по путям тестовой зоны в облаке
    :return:
    """
    result = []
    try:
        PATH = 'scope/configs/db.conf'
        if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
            print("Работаем на хосте тестовой зоны")
            result=load_file_by_lines(PATH)
        else:
            PATH = '/Users/nabaran2/docker/msk_scope/configs/db.conf'
            print("Работаем на хосте разработки")
            result=load_file_by_lines(PATH)
    except:
        print("печалька! ни по одному из путей файл db.conf не найден...")
    # print(result)
    # print(result.get('MSK_SCOPE'))
    return result


