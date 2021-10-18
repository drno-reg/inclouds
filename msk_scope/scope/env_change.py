import os,sys

def os_pythonpath_change():
    """
    меняем каталог с текущего на уровень выше для того, чтобы подтянуть models.py
    """
    pythonpath = os.path.dirname(os.path.abspath(__file__))
    pythonpath = pythonpath.rpartition('/')[0]
    print(pythonpath)
    sys.path.append(pythonpath)
