import socket
import sys
import threading
import time
import os
import re
import multiprocessing as mp
from tqdm import tqdm
from random import randint
from multiprocessing.connection import _ConnectionBase

from api import getLocalHostIP, getTime, log

localHostIP = getLocalHostIP()
localHostPort = randint(1024, 65535)

socketSendRecv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketSendRecv.bind((localHostIP, localHostPort))

scanResult = {"serverCount": 0, "bdsCount": 0, "nkCount": 0, "geyserCount": 0,
              "skipped": 0, "error": 0, "serverList": [], "totalPlayerCount": 0}

motdData = b'\x01\x00\x00\x00\x00$\r\x12\xd3\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx\n'

def getIpList(ip: str):
    ipList = []
    if os.path.exists(TargetAddr):
        with open(TargetAddr, "r") as file:
            for ip in file.readlines():
                if len(ip) < 3:
                    continue
                if "|" in ip:
                    if ip.split(" | ")[2] not in ipList:
                        ipList.append(ip.split(" | ")[2])
                else:
                    if ip[:-1] not in ipList:
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
            log(f"Scaning port: {str(dstPort)} ~ {str(dstPort + int(portEnd / 5))}", info="I")
        socketSendRecv.sendto(motdData, (dstAddr, dstPort))
    # if verboseMode == "y":
    #     log(f"Port {portStart} ~ {portEnd} Done", info = "I")


def startThreads():
    global stopThread, quietMode
    if "-" in portRange:
        portStart = int(portRange.split("-")[0])
        portEnd = int(portRange.split("-")[1])
    else:
        portStart = 0
        portEnd = 65535
    ipList = getIpList(TargetAddr)
    if quietMode:
        progressBar = tqdm(desc="Scaning progress",total=len(ipList), leave=True, unit="IP", unit_scale=False)
    for dstAddr in ipList:
        stopThread = False
        log(quiet=quietMode)
        log(f"Scaning target: {dstAddr}", info="I", quiet=quietMode)
        log(quiet=quietMode)
        # sendPacket(portStart, portEnd, dstAddr)
        t1 = threading.Thread(target=sendPacket, args=(
            portStart, portEnd, dstAddr), daemon=True)
        t1.start()
        tmpServerCount = scanResult['serverCount']
        if timeout != 0:
            time.sleep(timeout)
            if tmpServerCount == scanResult['serverCount']:
                stopThread = True
        t1.join()
        if quietMode:
            progressBar.update(1)
        # while threading.enumerate().__len__() != 2:  # main and itself
        #     time.sleep(1)
    # while mp.active_children():
    #     time.sleep(1)
    mp.active_children()[0].terminate()
    # time.sleep(1)
    # print(scanResultList)
    with open(fileName, "w") as file:
        file.writelines(scanResultList)
    quietMode = False
    log(f"BE Server Count: {scanResult['serverCount']}", info="I", quiet=quietMode)
    log(f"BDS Count: {scanResult['bdsCount']}", info="I", quiet=quietMode)
    log(f"NK Count: {scanResult['nkCount']}", info="I", quiet=quietMode)
    log(f"Geyser Count: {scanResult['geyserCount']}", info="I", quiet=quietMode)
    log(f"Skipped Count: {scanResult['skipped']}", info="I", quiet=quietMode)
    log(f"Error Count: {scanResult['error']}", info="I", quiet=quietMode)
    log(f"Total Player Count: {scanResult['totalPlayerCount']}", info="I", quiet=quietMode)
    os._exit(0)


def recvPackets(socketSendRecv: socket.socket, verboseMode: str, fileName: list, scanResult: dict, pipe: _ConnectionBase):
    if verboseMode == "nn":
        quietMode = True
    else:
        quietMode = False
    with open(fileName[1], "r") as file:
        scanResultList = file.readlines()
    while True:
        try:
            data, addr = socketSendRecv.recvfrom(10240)
            date = getTime()
            if len(data) <= 30:
                scanResult['skipped'] += 1
                log(
                    f"data length <= 30, may not motd packet, skipped. Source: {addr[0]}:{addr[1]}", info="R", quiet=quietMode)
                continue
            if b"MCPE" not in data:
                scanResult['skipped'] += 1
                log(
                    f"metadata \"MCPE\" not in packet, may not motd packet, skipped. Source: {addr[0]}:{addr[1]}", info="R", quiet=quietMode)
                continue
            if addr not in scanResult['serverList']:
                scanResult['serverList'].append(addr)
            else:
                scanResult['skipped'] += 1
                log(
                    f"Duplicate server found, skipped. Source: {addr[0]}:{addr[1]}", info="R", quiet=quietMode)
                continue
            infos = []
            data1 = data.split(b"MCPE")
            # log("----------------------------------------------------")
            # log(data1)
            # log(quiet=quietMode)
            infos_byte = data1[1].split(b";")
            for info in infos_byte:
                try:
                    context = info.decode()
                except:
                    context = str(info)[2:-1]
                infos.append(context)
            # log(len(infos))
            log(f"Motd: {infos[1]}", info="R", quiet=quietMode)
            log(f"Versin: {infos[3]}/{infos[2]}", info="R", quiet=quietMode)
            log(f"Online: {infos[4]}/{infos[5]}", info="R", quiet=quietMode)
            try:
                log(f"Map: {infos[7]}/{infos[8]}", info="R", quiet=quietMode)
            except:
                log(f"Map info is unavailable.", info="R", quiet=quietMode)
            try:
                log(f"Port(v4/v6): {infos[10]}/{infos[11]}", info="R", quiet=quietMode)
            except:
                log(f"Port info is unavailable.", info="R", quiet=quietMode)
            log(f"Source: {addr[0]}:{addr[1]}", info="R", quiet=quietMode)
            scanResult['serverCount'] += 1
            scanResult['totalPlayerCount'] += int(infos[4])
            log(f"{scanResult['serverCount']}", info="C", quiet=quietMode)
            log(f"{scanResult['totalPlayerCount']}", info="P", quiet=quietMode)
            log(quiet=quietMode)
            if fileName[0]:
                scanResultList = saveResults(fileName, scanResult, addr, date, infos, scanResultList)
            if len(infos) == 10 or len(infos) == 6:
                scanResult['nkCount']  += 1
            elif re.search(b"edicated", data):
                scanResult['bdsCount'] += 1
            elif re.search(b"nukkit", data):
                scanResult['nkCount'] += 1
            elif re.search(b"eyser", data):
                scanResult['geyserCount'] += 1
            # socketSendRecv.close()
        except OSError as errorInfo:
            if verboseMode == "y":
                log(f"{errorInfo}, skipped.", info="R", quiet=quietMode)
            scanResult['error'] += 1
        except Exception as errorInfo:
            log(f"{errorInfo}, skipped.", info="R", quiet=quietMode)
            scanResult['error'] += 1
        finally:
            pipe.send((scanResult, scanResultList))

def saveResults(fileName, scanResult, addr, date, infos, scanResultList):
    formatedScanResult = f"{date} | {scanResult['serverCount']} | {addr[0]} | {addr[1]} | {infos[1]} | {infos[3]} | {infos[4]} | {infos[5]}"
    # scanResultListBackup = scanResultList
    with open(fileName[0], "r+") as file:
        # scanResultList = file.readlines()
        for index in range(len(scanResultList)):
            # print(scanResultList[index])
            # print(infos[1], scanResultList[index])
            if scanResultList[index] == "\n\n":
                del scanResultList[index]
                # log("del line: ", scanResultList[index])
                return scanResultList
            if infos[1] in scanResultList[index]:
                try:
                    int(infos[1])
                    infos[1][3]
                except:
                    return scanResultList
                if addr[0] not in scanResultList[index]:
                    if fileName[0] == fileName[1]:
                        with open("updated.txt", "a") as file:
                            pervInfo = scanResultList[index].split(" | ")
                            file.write(f"{formatedScanResult}  Pervious: {pervInfo[2]}:{pervInfo[3]}\n")
                    scanResultList[index] = formatedScanResult + "\n"
                    # if len(scanResultList) < len(scanResultListBackup):
                    #     scanResultList = scanResultListBackup
                    #     log(f"{len(scanResult)} < {len(scanResultListBackup)}!")
                    #     with open("less.txt", "w") as file:
                    #         file.writelines(scanResultList)
                    #     with open("more.txt", "w") as file:
                    #         file.writelines(scanResultListBackup)
                    #     os._exit(0)
                    # if randint(1, 5) == 0:
                    #     with open(fileName, "w") as file:
                    #         file.writelines(scanResultList)
                return scanResultList
        scanResultList.append("\n" + formatedScanResult)
        if len(scanResultList) == 0:
            scanResultList.append(formatedScanResult + "\n")
        return scanResultList


if __name__ == "__main__":
    try:
        TargetAddr = sys.argv[1]
        portRange = sys.argv[2]
        verboseMode = sys.argv[3]
    except:
        TargetAddr = input("Target IP: ")
        portRange = input("Port range(like 1145-1919 and all): ")
        verboseMode = input("Show verbose info(y/n/nn): ")
    if verboseMode == "nn":
        quietMode = True
    else:
        quietMode = False
    try:
        timeout = int(sys.argv[4])
    except:
        timeout = 0

    try:
        fileName = str(sys.argv[5])
    except:
        fileName = ""

    pipe1, pipe2 = mp.Pipe()
    p = mp.Process(target=recvPackets, args=(
        socketSendRecv, verboseMode, [fileName, TargetAddr], scanResult, pipe2), daemon=True)
    p.start()
    t = threading.Thread(target=startThreads, daemon=True)
    t.start()
    while mp.active_children():
        scanResult, scanResultList = pipe1.recv()
