import socket
import random
import threading
import time
import traceback
import argparse
import os
import multiprocessing as mp

from tqdm import tqdm

from api import MOTD_PKT, get_time, parse_raw_pkt, get_ip_list, get_udp_socket


def split_list(total: int, num_splits: int) -> list:
    if num_splits <= 1:
        return [[0, total]]
    split_size = total // num_splits
    split_list = [[i * split_size + 1, (i + 1) * split_size]
                  for i in range(num_splits - 1)]
    split_list.append([split_list[-1][-1] + 1, total])
    return split_list


def send_packet(udp_skt: socket.socket, ip: str, port_range: list, port_start: int, interval: float, conn):
    for port in range(port_range[0], port_range[1]):
        port += port_start
        try:
            udp_skt.sendto(MOTD_PKT, (ip, port))
            time.sleep(interval)
        except Exception as e:
            # traceback.print_exc()
            # return e
            pass
        finally:
            conn.send(1)


prog_mon = 0
def progerss_monitor(conn, port_count: int):
    global prog_mon
    prog_mon = 0
    while True:
        prog_mon_tmp = prog_mon
        time.sleep(1)
        if prog_mon == prog_mon_tmp:
            for i in range(port_count-prog_mon):
                try:
                    conn.send(1)
                except BrokenPipeError:
                    pass
            break


is_recving = False
def scanner(udp_skt: socket.socket, addr: str, interval: float, threads: int, port_start: int, port_count: int):
    global is_recving, prog_mon
    pbar = tqdm(iterable=range(port_count), desc="Scaning progress",
                leave=False, unit="Port", unit_scale=False)

    pbar.write(f"Scanning: {addr}")

    if not is_recving:
        is_recving = True
        threading.Thread(target=recv_packets, args=(
            udp_skt, pbar), daemon=True).start()

    port_ranges = split_list(port_count, threads)

    parent_conn, child_conn = mp.Pipe()

    threading.Thread(target=progerss_monitor, args=(
        child_conn, port_count), daemon=True).start()

    for port_range in port_ranges:
        mp.Process(target=send_packet, args=(udp_skt, addr,
                   port_range, port_start, interval, child_conn), daemon=True).start()

    for p in pbar:
        parent_conn.recv()
        prog_mon += 1

    time.sleep(1)

    pbar.close()


def recv_packets(udp_skt, pbar: tqdm):
    server_count = 0
    while True:
        try:
            infos, addr = parse_raw_pkt(udp_skt.recvfrom(1024))
            if not infos or not infos["motd"]:  # 过滤掉没有motd的和没有信息的
                continue
            if int(infos['online']) < display_online:
                continue

            server_count += 1

            values = [f"[Time   ] {get_time()}",
                      f"[Address] {infos['addr']}",
                      f"[MotdInf] {infos['motd']}",
                      f"[Version] {infos['version']}/{infos['version_id']}",
                      f"[GameInf] {infos['map']}/{infos['gamemode']}",
                      f"[Online ] {infos['online']}/{infos['max_player']}",
                      f"[Count  ] {server_count}",
                      ""]
            pbar.write("\n".join(values))
            os.makedirs("scan-result", exist_ok=True)
            with open(f"scan-result/{time.strftime('%Y-%d-%m-%H-%M')}.txt", "a+") as file:
                pbar.write("\n".join(values), file)
            if exec_cmd:
                threading.Thread(target=exec_cmd_async, args=(exec_cmd, infos), daemon=True).start()
        except socket.timeout:
            continue
        except ConnectionResetError:
            continue
        except OSError:
            if getattr(udp_skt, '_closed'):
                break
            traceback.print_exc()
            continue
        except:
            traceback.print_exc()
            continue


def exec_cmd_async(cmd: str, variables: dict = [None]) -> None:
    for key in variables:
        cmd = cmd.replace("{"+key+"}", variables[key])
    os.system(cmd)


if __name__ == "__main__":
    mp.freeze_support()
    parser = argparse.ArgumentParser()
    parser.add_argument("addr", help="the target server address")
    parser.add_argument("-i", "--interval", default=0.005, type=float,
                        help="send packet interval. recommand 0.01~0.0001")
    parser.add_argument("-p", "--port", default=random.randint(1024, 65535), type=int,
                        help="local port for send packet")
    parser.add_argument("-t", "--threads", default=(mp.cpu_count() - 1), type=int,
                        help="number of threads used to scan")
    parser.add_argument("-do", "--display-online", default=0, type=int,
                        help="only displayed when the number of online players is greater than or equal to this value")
    parser.add_argument("-e", "--exec-cmd", default="", type=str,
                        help="the cmd command that is executed immediately after scanning the server can use {var} as a variable, "
                        + "the command needs to be enclosed in double quotes, the available variables are: motd, version_id, "
                        + "version, online, max_player, unique_id, map, gamemode, source_port_v4, source_port_v6, addr and ip")
    parser.add_argument("-v6", "--use-ipv6", action="store_true", default=False, 
                        help="use IPv6 instead of IPv4")
    parser.add_argument("-r", "--port-range", default="1-65535", type=str,
                        help="port range to scan, format: start-end")

    args, unparsed = parser.parse_known_args()

    addr = args.addr
    interval = args.interval
    local_port = args.port
    display_online = args.display_online
    exec_cmd = args.exec_cmd
    use_ipv6 = args.use_ipv6
    threads = args.threads
    port_range = args.port_range.split("-")

    udp_skt = get_udp_socket(local_port, use_ipv6=use_ipv6)

    for addr in get_ip_list(addr):
        scanner(udp_skt, addr, interval, threads, int(port_range[0]), int(port_range[1]) - int(port_range[0]))
