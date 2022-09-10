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

def log(*content, level: str = "INFO", info: str = "", quiet: bool = False):
    if quiet:
        return
    date = time.strftime('%H:%M:%S')
    strs = ""
    for string in content:
        strs += str(string)
    content = strs[0:]
    if info != "":
        print(f"[{date} {info}] {content}")
    else:
        print(f"[{date}] {content}")