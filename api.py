import socket
import time

def getLocalHostIP():
    localHostIP = socket.gethostbyname(socket.gethostname())
    try: 
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
        s.connect(('8.8.8.8', 80)) 
        localHostIP = s.getsockname()[0] 
    finally:
        s.close()
    return localHostIP

def getTime():
    return time.strftime('%H:%M:%S')