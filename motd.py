import argparse
from api import get_udp_socket, log, parse_raw_pkt, MOTD_PKT


def send_pkt(addr, port, timeout: float=3.0):
    udp_skt = get_udp_socket()
    udp_skt.settimeout(timeout)
    udp_skt.sendto(
        MOTD_PKT,
        (addr, port))
    recv_pkt(udp_skt)


def recv_pkt(sk_send):
    infos, addr = parse_raw_pkt(sk_send.recvfrom(10240))
    log(f"Motd: {infos['motd']}")
    log(f"Versin: {infos['version']}/{infos['version_id']}")
    log(f"Online: {infos['online']}/{infos['max_player']}")
    try:
        log(f"Map: {infos['map']}/{infos['gamemode']}")
    except:
        log(f"Map info is unavailable.")
    try:
        log(f"Port(v4/v6): {infos['source_port_v4']}/{infos['source_port_v6']}")
    except:
        log(f"Port info is unavailable.")
    log(f"Source: {infos['addr']}")

    sk_send.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", help="target server address, can be domain or ip")
    parser.add_argument("port", type=int, default=19132,
                        help="target server port")
    parser.add_argument("-t", "--timeout", default=3.0, type=float,
                        help="timeout")

    args = parser.parse_args()

    addr = args.addr
    port = args.port
    timeout = args.timeout

    try:
        send_pkt(addr, port, timeout)
    except TimeoutError:
        log(f"Timeout! Server may be offline or blocked motd request.")
