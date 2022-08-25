from os import _exit
from random import randint
import socket
import threading
import sys
import time
from scapy.all import *
from api import getLocalHostIP

localHostIP = getLocalHostIP()
localHostPort = randint(1024, 65535)

try:
    TargetAddr = str(sys.argv[1])
except:
    TargetAddr = input("Target IP: ")
motdData = b'\x01\x00\x00\x00\x00$\r\x12\xd3\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx\n'
serverCount = 0


def sendPacket(startNum, count):
    port = startNum
    while True:
        Time = time.strftime('%H:%M:%S')
        if port % 1000 == 0:
            print(f"[{Time} I] Scaning port: {str(port)} ~ {str(port + 1000)}")
        send(IP(src=localHostIP, dst=TargetAddr) / UDP(sport=localHostPort, dport=port) /
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
            print("Skipped Count: " + str(skipped))
            print("Error Count: " + str(error))
            print("Total Player Count: " + str(totalPlayerCount))
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
skipped = 0
error = 0
payloads = []
totalPlayerCount = 0
while True:
    try:
        sk_rec = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sk_rec.bind((localHostIP, localHostPort))
        data, addr = sk_rec.recvfrom(10240)
        date = time.strftime('%H:%M:%S')
        if len(data) <= 30:
            skipped += 1
            print(
                f"[{date} R] data length <= 30, may not motd packet, skipped. Source: {addr[0]}:{addr[1]}")
            continue
        if b"MCPE" not in data:
            skipped += 1
            print(
                f"[{date} R] metadata \"MCPE\" not in packet, may not motd packet, skipped. Source: {addr[0]}:{addr[1]}")
            continue
        if addr[1] not in payloads:
            payloads.append(addr[1])
        else:
            skipped += 1
            print(
                f"[{date} R] Duplicate server found, skipped. Source: {addr[0]}:{addr[1]}")
            continue
        infos = []
        data1 = data.split(b"MCPE")
        # print("----------------------------------------------------")
        # print(data1)
        # print()
        infos_byte = data1[1].split(b";")
        for info in infos_byte:
            try:
                context = info.decode()
            except:
                context = str(info)[2:-1]
            infos.append(context)
        print("")
        # print(len(infos))
        print(f"[{date} R] Motd: {infos[1]}")
        print(f"[{date} R] Versin: {infos[3]}/{infos[2]}")
        print(f"[{date} R] Online: {infos[4]}/{infos[5]}")
        try:
            print(f"[{date} R] Map: {infos[7]}/{infos[8]}")
        except:
            print(f"[{date} R] Map info is unavailable.")
        try:
            print(f"[{date} R] Port(v4/v6): {infos[10]}/{infos[11]}")
        except:
            print(f"[{date} R] Port info is unavailable.")
        print(f"[{date} R] Source: {addr[0]}:{addr[1]}")
        serverCount += 1
        totalPlayerCount += int(infos[4])
        print(f"[{date} C] {str(serverCount)}")
        print(f"[{date} P] {totalPlayerCount}")
        if len(infos) == 10 or len(infos) == 6:
            nkCount += 1
        elif re.search(b"edicated", data):
            bdsCount += 1
        elif re.search(b"nukkit", data):
            nkCount += 1
        elif re.search(b"eyser", data):
            geyserCount += 1
        sk_rec.close()
    except:
        print(f"[{time.strftime('%H:%M:%S')} R] An error occurred, skipped.")
        error += 1
        pass
