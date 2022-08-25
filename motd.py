from random import randint
import socket
import sys
from api import getLocalHostIP, getTime
localHostIP = getLocalHostIP()


def sendPacket(ip, port):
    sk_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk_send.settimeout(3)
    sk_send.bind((localHostIP, randint(1024, 65535)))
    sk_send.sendto(
        b'\x01\x00\x00\x00\x00$\r\x12\xd3\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx\n',
        (str(ip), int(port)))
    recvPacket(sk_send)


def recvPacket(sk_send):
    data, addr = sk_send.recvfrom(10240)
    infos = []
    data1 = data.split(b"MCPE")
    infos_byte = data1[1].split(b";")
    # print(data)
    # print(data1)
    # print(infos_byte)
    for info in infos_byte:
        try:
            context = info.decode()
        except:
            context = str(info)[2:-1]
        infos.append(context)
    print(f"[{getTime()}] Motd: {infos[1]}")
    print(f"[{getTime()}] Versin: {infos[3]}/{infos[2]}")
    print(f"[{getTime()}] Online: {infos[4]}/{infos[5]}")
    try:
        print(f"[{getTime()}] Map: {infos[7]}/{infos[8]}")
    except:
        print(f"[{getTime()}] Map info is unavailable.")
    try:
        print(f"[{getTime()}] Port(v4/v6): {infos[10]}/{infos[11]}")
    except:
        print(f"[{getTime()}] Port info is unavailable.")
    print(f"[{getTime()}] Source: {addr[0]}:{addr[1]}")

    sk_send.close()


if __name__ == "__main__":
    try:
        ip = sys.argv[1]
        port = sys.argv[2]
    except:
        ip = input("Target: ")
        port = input("Port: ")
    try:
        sendPacket(ip, port)
    except:
        print(
            f"[{getTime()}] Timeout! Server may be offline or blocked motd request.")
