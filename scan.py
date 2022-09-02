import socket
import sys
import threading
import time
import os
import re
from random import randint

from api import getLocalHostIP, log

localHostIP = getLocalHostIP()
localHostPort = randint(1024, 65535)

socketSendRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketSendRecv.bind((localHostIP, localHostPort))

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
    timeout = 0

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
                # ipList.append(ip.split(" | ")[2])
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


def sendPacket(portStart, portEnd, dstAddr):
    for dstPort in range(portStart, portEnd + 1):
        if stopThread:
            break
        if dstPort % int(portEnd / 5) == 0 and verboseMode == "y":
            log(f"Scaning port: {str(dstPort)} ~ {str(dstPort + int(portEnd / 5))}", info = "I")
        socketSendRecv.sendto(motdData, (dstAddr, dstPort))
    # if verboseMode == "y":
    #     log(f"Port {portStart} ~ {portEnd} Done", info = "I")

def startThreads():
    global stopThread
    if "-" in portRange:
        portStart = int(portRange.split("-")[0])
        portEnd = int(portRange.split("-")[1])
    else:
        portStart = 0
        portEnd = 65535
    ipList = getIpList(TargetAddr)
    for dstAddr in ipList:
        stopThread = False
        print()
        log(f"Scaning target: {dstAddr}", info = "I")
        print()
        # sendPacket(portStart, portEnd, dstAddr)
        t1 = threading.Thread(target=sendPacket, args=(portStart, portEnd, dstAddr), daemon = True)
        t1.start()
        tmpServerCount = serverCount
        if timeout != 0:
            time.sleep(timeout)
            if tmpServerCount == serverCount:
                stopThread = True
        t1.join()
        # while threading.enumerate().__len__() != 2:  # main and itself
        #     time.sleep(1)

    log("BE Server Count: " + str(serverCount), info = "I")
    log("BDS Count: " + str(bdsCount), info = "I")
    log("NK Count: " + str(nkCount), info = "I")
    log("Geyser Count: " + str(geyserCount), info = "I")
    log("Skipped Count: " + str(skipped), info = "I")
    log("Error Count: " + str(error), info = "I")
    log("Total Player Count: " + str(totalPlayerCount), info = "I")
    os._exit(0)

if __name__ == "__main__":
    t = threading.Thread(target=startThreads, daemon = True)
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
            data, addr = socketSendRecv.recvfrom(10240)
            date = time.strftime('%H:%M:%S')
            if len(data) <= 30:
                skipped += 1
                log(f"data length <= 30, may not motd packet, skipped. Source: {addr[0]}:{addr[1]}", info = "R")
                continue
            if b"MCPE" not in data:
                skipped += 1
                log(f"metadata \"MCPE\" not in packet, may not motd packet, skipped. Source: {addr[0]}:{addr[1]}", info = "R")
                continue
            if addr not in payloads:
                payloads.append(addr)
            else:
                skipped += 1
                log(f"Duplicate server found, skipped. Source: {addr[0]}:{addr[1]}", info = "R")
                continue
            infos = []
            data1 = data.split(b"MCPE")
            # log("----------------------------------------------------")
            # log(data1)
            # log()
            infos_byte = data1[1].split(b";")
            for info in infos_byte:
                try:
                    context = info.decode()
                except:
                    context = str(info)[2:-1]
                infos.append(context)
            # log(len(infos))
            log(f"Motd: {infos[1]}", info = "R")
            log(f"Versin: {infos[3]}/{infos[2]}", info = "R")
            log(f"Online: {infos[4]}/{infos[5]}", info = "R")
            try:
                log(f"Map: {infos[7]}/{infos[8]}", info = "R")
            except:
                log(f"Map info is unavailable.", info = "R")
            try:
                log(f"Port(v4/v6): {infos[10]}/{infos[11]}", info = "R")
            except:
                log(f"Port info is unavailable.", info = "R")
            log(f"Source: {addr[0]}:{addr[1]}", info = "R")
            serverCount += 1
            totalPlayerCount += int(infos[4])
            log(f"{str(serverCount)}", info = "C")
            log(f"{totalPlayerCount}", info = "P")
            print("")
            if fileName:
                with open(fileName, "a+") as file:
                    file.write(
                        f"{date} | {serverCount} | {addr[0]} | {addr[1]} | {infos[1]} | {infos[3]} | {infos[4]} | {infos[5]}\n")
            if len(infos) == 10 or len(infos) == 6:
                nkCount += 1
            elif re.search(b"edicated", data):
                bdsCount += 1
            elif re.search(b"nukkit", data):
                nkCount += 1
            elif re.search(b"eyser", data):
                geyserCount += 1
            #socketSendRecv.close()
        except OSError as errorInfo:
            if verboseMode == "y":
                log(f"{errorInfo}, skipped.", info = "R")
            error += 1
        except Exception as errorInfo:
            log(f"{errorInfo}, skipped.", info = "R")
            error += 1
            pass
