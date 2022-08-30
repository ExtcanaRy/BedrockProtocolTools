import socket
import sys
import threading
import time
from os import _exit
from random import randint

from scapy.all import *
from scapy.layers.inet import IP, UDP

from api import getLocalHostIP

localHostIP = getLocalHostIP()
localHostPort = randint(1024, 65535)

try:
    TargetAddr = sys.argv[1]
    portRange = sys.argv[2]
    verboseMode = sys.argv[3]
except:
    TargetAddr = input("Target IP: ")
    portRange = input("Port range(like 1145-1919 and all): ")
    verboseMode = input("Show verbose info(y/n): ")

try:
    timeout = int(sys.argv[4])
except:
    timeout = None

try:
    fileName = str(sys.argv[5])
except:
    fileName = ""

motdData = b'\x01\x00\x00\x00\x00$\r\x12\xd3\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx\n'
serverCount = 0


def getIpList(ip: str):
    ipList = []
    if os.path.exists(TargetAddr):
        with open(TargetAddr, "r") as file:
            for ip in file.readlines():
                ipList.append(ip[:-1])
            return ipList
    try:
        int(ip[-1])
        # ip = "8.8.1-5.8-11"
        processedIpSegs = [[], [], [], []]
        ipSegIndex = 0
        ipSegs = ip.split(".")  # 8.8.0-255.0-5 -> [8, 8, 0-255, 0-5]
        for ipSeg in ipSegs:
            if "-" in ipSeg:
                segList = ipSeg.split("-")  # 0-5 -> [0, 5]
                # range(0, 5)  -> [0, 1, 2, 3, 4]
                for i in range(int(segList[0]), int(segList[1])+1):
                    processedIpSegs[ipSegIndex].append(str(i))
            else:
                processedIpSegs[ipSegIndex].append(ipSeg)
            ipSegIndex += 1

        # [['8'], ['8'], ['1', '2', '3', '4'], ['8', '9', '10']]
        for processedIpSegA in processedIpSegs[0]:
            for processedIpSegB in processedIpSegs[1]:
                for processedIpSegC in processedIpSegs[2]:
                    for processedIpSegD in processedIpSegs[3]:
                        ipList.append(
                            f"{processedIpSegA}.{processedIpSegB}.{processedIpSegC}.{processedIpSegD}")
        return ipList
    except:
        return [ip]


def sendPacket(startPort, count, ip):
    port = startPort
    while True:
        if stopThread:
            break
        Time = time.strftime('%H:%M:%S')
        if port % int(count / 5) == 0 and verboseMode == "y":
            print(f"[{Time} I] Scaning port: {str(port)} ~ {str(port + int(count / 5))}")
        send(IP(src=localHostIP, dst=ip) / UDP(sport=localHostPort, dport=port) /
             motdData,
             verbose=False)
        if port == startPort + count - 1:
            if verboseMode == "y":
                print(f"[{Time} I] Port {startPort} ~ {startPort + count} Done")
            break
        port += 1


def startThreads():
    global stopThread
    if "-" in portRange:
        portRangeStart = int(portRange.split("-")[0])
        portRangeEnd = int(portRange.split("-")[1])
    else:
        portRangeStart = 0
        portRangeEnd = 65535
    portCount = portRangeEnd - portRangeStart
    if portCount < 7:
        portCount += 7
    singleThreadProcPort = (portCount - (portCount % 7)) / 7
    portStartList = []
    for i in range(7):
        portStartList.append(int(portRangeStart))
        portRangeStart += singleThreadProcPort
    ipList = getIpList(TargetAddr)
    for ip in ipList:
        stopThread = False
        print()
        print(
            f"[{time.strftime('%H:%M:%S')} I] Scaning target: {ip}")
        print()
        for portStart in portStartList:
            if portStart == portStartList[-1]:
                t1 = threading.Thread(target=sendPacket, args=(portStart, int(singleThreadProcPort + (portCount % 7)), ip))
            else:
                t1 = threading.Thread(target=sendPacket, args=(portStart, int(singleThreadProcPort), ip))
            t1.setDaemon(True)
            t1.start()
        tmpServerCount = serverCount
        if timeout:
            time.sleep(timeout)
            if tmpServerCount == serverCount:
                stopThread = True
        while threading.enumerate().__len__() != 2:  # main and itself
            time.sleep(1)

    print("BE Server Count: " + str(serverCount))
    print("BDS Count: " + str(bdsCount))
    print("NK Count: " + str(nkCount))
    print("Geyser Count: " + str(geyserCount))
    print("Skipped Count: " + str(skipped))
    print("Error Count: " + str(error))
    print("Total Player Count: " + str(totalPlayerCount))
    _exit(0)


t = threading.Thread(target=startThreads)
t.setDaemon(True)
t.start()

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
        if fileName:
            with open(fileName, "a+") as file:
                file.write(
                    f"{date} | {serverCount} | {addr[0]} | {addr[1]} | {infos[1]} | {infos[3]} | {infos[4]}\n")
        if len(infos) == 10 or len(infos) == 6:
            nkCount += 1
        elif re.search(b"edicated", data):
            bdsCount += 1
        elif re.search(b"nukkit", data):
            nkCount += 1
        elif re.search(b"eyser", data):
            geyserCount += 1
        sk_rec.close()
    except OSError as info:
        if verboseMode == "y":
            print(f"[{time.strftime('%H:%M:%S')} R] {info}, skipped.")
        error += 1
    except Exception as info:
        print(f"[{time.strftime('%H:%M:%S')} R] {info}, skipped.")
        error += 1
        pass
