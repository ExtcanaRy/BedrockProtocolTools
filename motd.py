from random import randint
import socket
import sys
from api import getLocalHostIP, getTime, log
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
    prefix, motd_info = data.split(b"MCPE")
    infos_byte = motd_info.split(b";")
    for info in infos_byte:
        try:
            context = info.decode()
        except:
            context = str(info)[2:-1]
        infos.append(context)
    log(f"Motd: {infos[1]}")
    log(f"Versin: {infos[3]}/{infos[2]}")
    log(f"Online: {infos[4]}/{infos[5]}")
    try:
        log(f"Map: {infos[7]}/{infos[8]}")
    except:
        log(f"Map info is unavailable.")
    try:
        log(f"Port(v4/v6): {infos[10]}/{infos[11]}")
    except:
        log(f"Port info is unavailable.")
    log(f"Source: {addr[0]}:{addr[1]}")
    #infos = {"motd": infos[1], "version_id": infos[2], "version": infos[3], "online": infos[4], "max_player": infos[5],
    #         "unique_id": infos[6], "map": infos[7], "gamemode": infos[8], "source_port_v4": infos[10], "source_port_v6": infos[11]}

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
        log(f"Timeout! Server may be offline or blocked motd request.")
