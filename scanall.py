import socket
import time
from api import getLocalHostIP

localHostIP = getLocalHostIP()


def sendPacket():
    sk_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk_send.bind((localHostIP, 19132))
    for a in range(256):
        print(f"Scanning range: {str(a)}.0.0.0 ~ 255.255.255.255")
        for b in range(256):
            print(
                f"Scaning range: {str(a)}.{str(b)}.0.0 ~ {str(a)}.255.255.255")
            for c in range(256):
                #print(f"Scaning range: {str(a)}.{str(b)}.{str(c)}.0 ~ {str(a)}.{str(b)}.255.255")
                for d in range(256):
                    try:
                        IP = f"{str(a)}.{str(b)}.{str(c)}.{str(d)}"
                        sk_send.sendto(
                            b'\x01\x00\x00\x00\x00$\r\x12\xd3\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx\n',
                            (IP, 19132))
                    except:
                        continue
    sk_send.close()


def recPacket():
    startTime = int(time.strftime("%S"))
    while int(time.strftime("%S")) < startTime + 2:
        #    while True:
        try:
            sk_rec = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sk_rec.settimeout(0.1)
            sk_rec.bind(("192.168.1.233", 19132))
            data, addr = sk_rec.recvfrom(10240)
            print(data)
            print(addr)
        except:
            pass


sendPacket()
#    recPacket()
