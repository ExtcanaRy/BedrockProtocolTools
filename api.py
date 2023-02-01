import socket
import time
import sys
import random

MOTD_PKT = b'\x01\x00\x00\x00\x00$\r\x12\xd3\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx\n'


def get_local_host_ip():
    local_host_ip = socket.gethostbyname(socket.gethostname())
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_host_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_host_ip


def get_time():
    return time.strftime('%H:%M:%S')


def log(*content, level: str = "INFO", info: str = "", quiet: bool = False):
    if quiet:
        return
    date = time.strftime('%H:%M:%S')
    strs = ""
    for string in content:
        strs += str(string)
    content = strs[0:]
    if info != "":
        print(f"[{date} {info}] {content}")
    else:
        print(f"[{date}] {content}")


def get_ip_list(addr: str):
    # ip = "42.186.0-255.0-255" -> len(ip_list) == 65536
    try:
        int(addr[-1])
    except:
        return [socket.gethostbyname(addr)]
    ip_list = []
    processed_ip_segs = [[], [], [], []]
    ip_seg_index = 0
    ip_segs = addr.split(".")  # 42.186.0-255.0-255 -> [42, 186, 0-255, 0-255]
    for ip_seg in ip_segs:
        if "-" in ip_seg:
            seg_list = ip_seg.split("-")  # 0-255 -> [0, 255]
            for i in range(int(seg_list[0]), int(seg_list[1])+1):   # range(0, 255+1)
                processed_ip_segs[ip_seg_index].append(str(i))
        else:
            processed_ip_segs[ip_seg_index].append(
                ip_seg)  # append("42") & append("186")
        ip_seg_index += 1

    for processed_ip_seg_a in processed_ip_segs[0]:  # 42
        for processed_ip_seg_b in processed_ip_segs[1]:  # 186
            for processed_ip_seg_c in processed_ip_segs[2]:  # range(0, 256)
                # range(0, 256)
                for processed_ip_seg_d in processed_ip_segs[3]:
                    ip_list.append(
                        f"{processed_ip_seg_a}.{processed_ip_seg_b}.{processed_ip_seg_c}.{processed_ip_seg_d}")
    return ip_list


def decode_unicode(string: str):
    is_special_unicode = False
    for index in range(0, len(string), 5):
        if string[index] != "u":
            is_special_unicode = False
            break
        else:
            is_special_unicode = True

    if is_special_unicode:
        string = string.replace("u", "\\u")

    try:
        string.encode('ascii')
    except UnicodeEncodeError:
        return string
    else:
        return string.encode("utf-8").decode("unicode-escape")


def get_udp_socket(port=random.randint(1024, 65535)):
    if not port:
        port = random.randint(1024, 65535)
    sockets = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sockets.settimeout(1)
    if sys.platform.startswith('win32'):
        sockets.bind(("", port))
    return sockets


def parse_raw_pkt(pkt):
    server_data, addr = pkt
    # motd packet must contain b"MCPE"
    if b"MCPE" not in server_data or len(server_data) <= 30:
        return None, addr
    infos = []
    prefix, motd_info = server_data.split(b"MCPE")
    infos_byte = motd_info.split(b";")
    for info in infos_byte:
        try:
            context = info.decode()
        except UnicodeDecodeError:
            context = str(info)[2:-1]
        infos.append(context)
    try:
        infos = {"motd": decode_unicode(infos[1]), "version_id": infos[2], "version": infos[3], "online": infos[4],
                 "max_player": infos[5], "unique_id": infos[6], "map": decode_unicode(infos[7]), "gamemode": infos[8],
                 "source_port_v4": infos[10], "source_port_v6": infos[11], "ip": addr[0], "addr": f"{addr[0]}:{addr[1]}"}
    except IndexError:
        return None, addr
    if infos["source_port_v4"] != str(addr[1]):
        # return None, addr
        pass
    return infos, addr
