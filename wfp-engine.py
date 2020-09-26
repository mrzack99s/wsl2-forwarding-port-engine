import socket
import threading
import json, os
from pathlib import Path
from cmds import *

engineVersion = "0.2.0"
# Create a front socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket
ctrlSockAddr = ('0.0.0.0', 40123)
sock.bind(ctrlSockAddr)

threadWorking = {}
tasks = {}
homeDir = str(Path.home())

def udp_forwarder(taskId, wsl_ip, front_port, dest_port):
    global threadWorking
    # Create a front socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Bind the socket
    frontAddr = ("0.0.0.0", int(front_port))
    sock.bind(frontAddr)

    wslSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    wslAddr = (wsl_ip, int(dest_port))

    while True:
        try:
            if not threadWorking[taskId]["status"]:
                break
        except:
            break
        
        try:
            frontData, address = sock.recvfrom(65535)
            if frontData:
                wslSock.sendto(frontData, wslAddr)
                while True:
                    wslData, _ = wslSock.recvfrom(65535)
                    sock.sendto(wslData, address)
                    break
        except:
            pass

def writeFile():
    f = open(homeDir + '\\.wfp-engine\\.wfp-routines.json', 'w')
    json.dump(tasks,f, indent=3)
    f.close()

foundFile = False
if os.path.isfile(homeDir + '\\.wfp-engine\\.wfp-routines.json'):
    try:
        f = open(homeDir + '\\.wfp-engine\\.wfp-routines.json', 'r') 
        tasks = json.load(f)
        foundFile = True
        f.close()
    except:
        pass

if foundFile:
    try:
        for taskKey in tasks:
            t = threading.Thread(target=udp_forwarder, args=(tasks[taskKey]["id"], tasks[taskKey]["ip_addr"], tasks[taskKey]["sport"], tasks[taskKey]["dport"], ))
            t.setDaemon(True)
            threadWorking.update({
                                tasks[taskKey]["id"]:{
                                    "id": tasks[taskKey]["id"],
                                    "status": True
                                }
                            })
            t.start()
    except:
        pass

while True:
    try:
        recvData, address = sock.recvfrom(2048)
        if recvData:
            recvDataSplit = recvData.decode().split("@")
            if recvDataSplit[0] == "create":
                if recvDataSplit[2] == "UDP":
                    if not recvDataSplit[1] in tasks:
                        t = threading.Thread(target=udp_forwarder, args=(recvDataSplit[1], address[0], recvDataSplit[3], recvDataSplit[4], ))
                        t.setDaemon(True)
                        tasks.update({
                            recvDataSplit[1]:{
                                "id": recvDataSplit[1],
                                "ip_addr": address[0],
                                "proto": recvDataSplit[2],
                                "sport": recvDataSplit[3],
                                "dport": recvDataSplit[4]
                            }
                        })
                        threadWorking.update({
                            recvDataSplit[1]:{
                                "id": recvDataSplit[1],
                                "status": True
                            }
                        })
                        t.start()
                        allowFirewall(recvDataSplit[2],recvDataSplit[3])
                        writeFile()
                        sock.sendto(b"SUCCESS", address)
                    else:
                        sock.sendto(b"ALREADY", address)

                elif recvDataSplit[2] == "TCP":
                    if not recvDataSplit[1] in tasks:
                        allowFirewall(recvDataSplit[2],recvDataSplit[3])
                        tcpForwarding(address[0], recvDataSplit[3],recvDataSplit[4])
                        tasks.update({
                            recvDataSplit[1]: {
                                "id": recvDataSplit[1],
                                "ip_addr": address[0],
                                "proto": recvDataSplit[2],
                                "sport": recvDataSplit[3],
                                "dport": recvDataSplit[4]
                            }
                        })
                        writeFile()
                        sock.sendto(b"SUCCESS", address)
                    else:
                        sock.sendto(b"ALREADY", address)

            elif recvDataSplit[0] == "delete":
                if tasks[recvDataSplit[1]]["proto"] == "UDP":
                    if  recvDataSplit[1] in tasks:
                        print("stopping worker")
                        threadWorking[recvDataSplit[1]]["status"] = False
                        unallowFirewall(tasks[recvDataSplit[1]]["proto"],tasks[recvDataSplit[1]]["sport"])
                        del tasks[recvDataSplit[1]]
                        del threadWorking[recvDataSplit[1]]
                        writeFile()
                        sock.sendto(b"SUCCESS", address)
                    else:
                        sock.sendto(b"ALREADY", address)

                elif tasks[recvDataSplit[1]]["proto"] == "TCP":
                    if  recvDataSplit[1] in tasks:
                        unallowFirewall(tasks[recvDataSplit[1]]["proto"], tasks[recvDataSplit[1]]["sport"])
                        unforwardingTCP(tasks[recvDataSplit[1]]["sport"])
                        del tasks[recvDataSplit[1]]
                        writeFile()
                        sock.sendto(b"SUCCESS", address)
                    else:
                        sock.sendto(b"ALREADY", address)
            elif recvDataSplit[0] == "purge":
                 if recvDataSplit[1] == "Y":
                    for taskKey in tasks:
                        print("stopping worker")
                        threadWorking[tasks[taskKey]["id"]]["status"] = False
                        unallowFirewall(tasks[taskKey]["proto"],tasks[taskKey]["sport"])
                    tasks = {}
                    threadWorking = {}
                    writeFile()
                    sock.sendto(b"SUCCESS", address)


            elif recvDataSplit[0] == "get":
                if recvDataSplit[1] == "engine_version":
                    sock.sendto(engineVersion.encode(), address)

    except Exception as e:
        print(e)
        pass
