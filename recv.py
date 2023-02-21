import argparse
from threading import Thread
from api import get_udp_socket, log


def recv_pkt(loc_addr, loc_port, disable_errors=False):
    udp_skt = get_udp_socket(loc_port=loc_port, timeout=0, use_ipv6=use_ipv6, loc_addr=loc_addr)
    err_count = 0
    while True:
        try:
            data, addr = udp_skt.recvfrom(10240)
            log(data, info=addr)
        except Exception as exc:
            err_count += 1
            log(exc, level="ERROR", info=err_count, quiet=disable_errors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--address", type=str,
                        default="", help="local address to bind")
    parser.add_argument("-p", "--port", type=int,
                        default=19132, help="local port to bind")
    parser.add_argument("-v6", "--use-ipv6", action="store_true",
                        default=False, help="use IPv6 instead of IPv4")
    parser.add_argument("-de", "--disable-errors", action="store_true",
                        default=False, help="disable error message output")
    args = parser.parse_args()

    loc_addr = args.address
    loc_port = args.port
    use_ipv6 = args.use_ipv6
    disable_errors = args.disable_errors

    log(f"Starting listening {loc_addr}:{loc_port}, type q to exit.")
    Thread(target=recv_pkt, args=(loc_addr, loc_port, disable_errors), daemon=True).start()
    while True:
        if input() == "q":
            log("Exit...")
            exit()
