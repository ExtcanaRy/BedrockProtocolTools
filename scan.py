from os import _exit
from random import randint
import socket, threading, sys, time
from scapy.all import *

localHostIP = socket.gethostbyname(socket.gethostname())
BDSIP = str(sys.argv[1])
motdData = b'\x01\x00\x00\x00\x00$\r\x12\xd3\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx\n'
serverCount = 0

def sendPacket(startNum, count):
    port = startNum
    while True:
        Time = time.strftime('%H:%M:%S')
        if port % 1000 == 0:
            print(f"[{Time} I] Scaning port: {str(port)} ~ {str(port + 1000)}")
        send(IP(src=localHostIP, dst=BDSIP) / UDP(sport=49132, dport=port) /
             motdData,
             verbose=False)
        if port == 65535:
            print(f"[{Time} I] Port {startNum} ~ 65535 Done")
            while True:
                time.sleep(1)
        elif port == startNum + count - 1:
            print(f"[{Time} I] Port {startNum} ~ {startNum + count} Done")
            time.sleep(10)
            print("BE Server Count: " + str(serverCount))
            print("BDS Count: " + str(bdsCount))
            print("NK Count: " + str(nkCount))
            print("Geyser Count: " + str(geyserCount))
            _exit(0)
        port += 1


t1 = threading.Thread(target=sendPacket, args=(0, 10000))
t2 = threading.Thread(target=sendPacket, args=(10000, 10000))
t3 = threading.Thread(target=sendPacket, args=(20000, 10000))
t4 = threading.Thread(target=sendPacket, args=(30000, 10000))
t5 = threading.Thread(target=sendPacket, args=(40000, 10000))
t6 = threading.Thread(target=sendPacket, args=(50000, 10000))
t7 = threading.Thread(target=sendPacket, args=(60000, 5535))
t1.setDaemon(True)
t2.setDaemon(True)
t3.setDaemon(True)
t4.setDaemon(True)
t5.setDaemon(True)
t6.setDaemon(True)
t7.setDaemon(True)
t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
t6.start()
t7.start()

bdsCount = 0
nkCount = 0
geyserCount = 0


while True:
    sk_rec = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk_rec.bind((localHostIP, randint(1024, 65535)))
    try:
        data, addr = sk_rec.recvfrom(10240)
        Time = time.strftime('%H:%M:%S')
        print(f"[{Time} D] {str(data)}")
        print(f"[{Time} A] {str(addr)}")
        serverCount += 1
        print(f"[{Time} C] {str(serverCount)}")
        if re.search(b"edicated", data):
            bdsCount += 1
        if re.search(b"nukkit", data):
            nkCount += 1
        if re.search(b"eyser", data):
            geyserCount += 1
    except:
        pass

