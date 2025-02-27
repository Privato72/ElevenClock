import io
from types import FunctionType


from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


def loadTimeFormat():
    raise NotImplementedError("loadTimeFormat function has not been defined!")

def updateIfPossible():
    raise NotImplementedError("updateIfPossible function has not been defined!")
    
def restartClocks():
    raise NotImplementedError("restartClocks function has not been defined!")
    
def closeClocks():
    raise NotImplementedError("closeClocks function has not been defined!")

def _(a):
    try:
        raise NotImplementedError("_ function has not been defined!")
    except Exception as e:
        print("🟠", e)
    return a
    

app: QApplication = None
buffer: io.StringIO = None
old_stdout: io.StringIO = None
trayIcon: QSystemTrayIcon = None
sw: QScrollArea = None
tempDir: str = None

