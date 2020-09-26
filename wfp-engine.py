import socket
import threading
import json, os
from pathlib import Path
from cmds import *
from global_functions import *
from hashlib import sha256

engineVersion = "0.3.0"
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
            if tasks[taskKey]["ip_addr"] == getWSLIPAddr():
                t = threading.Thread(target=udp_forwarder, args=(tasks[taskKey]["id"], tasks[taskKey]["ip_addr"], tasks[taskKey]["sport"], tasks[taskKey]["dport"], ))
                t.setDaemon(True)
                threadWorking.update({
                                    tasks[taskKey]["id"]:{
                                        "id": tasks[taskKey]["id"],
                                        "status": True
                                    }
                                })
                t.start()
            else:
                if tasks[taskKey]["proto"] == "UDP":
                    unallowFirewall(tasks[taskKey]["proto"],tasks[taskKey]["sport"])
                    del tasks[taskKey]
                    del threadWorking[tasks[taskKey]["id"]]
                    writeFile(homeDir, tasks)

                elif tasks[taskKey]["proto"] == "TCP":
                    unallowFirewall(tasks[taskKey]["proto"], tasks[taskKey]["sport"])
                    unforwardingTCP(tasks[taskKey]["sport"])
                    del tasks[taskKey]
                    writeFile(homeDir, tasks)

    except:
        pass

while True:
    try:
        recvData, address = sock.recvfrom(65535)
        if recvData:
            recvDataSplit = recvData.decode().split("@")
            if recvDataSplit[0] == "create":
                newTask = {
                            "ip_addr": address[0],
                            "proto": recvDataSplit[1],
                            "sport": recvDataSplit[2],
                            "dport": recvDataSplit[3]
                        }
                hashId = sha256(json.dumps(newTask).encode()).hexdigest().encode().decode()
                newTask.update({
                    "id": hashId[:8],
                })

                if newTask["proto"] == "UDP":

                    if not newTask["id"] in tasks:

                        t = threading.Thread(target=udp_forwarder, args=(newTask["id"], newTask["ip_addr"], newTask["sport"], newTask["dport"], ))
                        t.setDaemon(True)

                        threadWorking.update({
                            newTask["id"]:{
                                "id": newTask["id"],
                                "status": True
                            }
                        })

                        tasks.update({
                            newTask["id"]: newTask
                        })

                        t.start()
                        allowFirewall(newTask["proto"],newTask["sport"])
                        writeFile(homeDir, tasks)
                        sock.sendto(b"SUCCESS", address)
                    else:
                        sock.sendto(b"ALREADY", address)

                elif newTask["proto"] == "TCP":
                    if not newTask["id"] in tasks:
                        allowFirewall(newTask["proto"],newTask["sport"])
                        tcpForwarding(newTask["ip_addr"], newTask["sport"], newTask["dport"])
                        tasks.update({
                            newTask["id"]: newTask
                        })
                        writeFile(homeDir, tasks)
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
                        writeFile(homeDir, tasks)
                        sock.sendto(b"SUCCESS", address)
                    else:
                        sock.sendto(b"ALREADY", address)

                elif tasks[recvDataSplit[1]]["proto"] == "TCP":
                    if  recvDataSplit[1] in tasks:
                        unallowFirewall(tasks[recvDataSplit[1]]["proto"], tasks[recvDataSplit[1]]["sport"])
                        unforwardingTCP(tasks[recvDataSplit[1]]["sport"])
                        del tasks[recvDataSplit[1]]
                        writeFile(homeDir, tasks)
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
                    writeFile(homeDir, tasks)
                    sock.sendto(b"SUCCESS", address)


            elif recvDataSplit[0] == "get":
                if recvDataSplit[1] == "ls":
                    strTasks = ""
                    for i, taskKey in enumerate(tasks):
                        if i == len(tasks) - 1:
                            strTasks += tasks[taskKey]["id"] + "@" + tasks[taskKey]["ip_addr"] + "@" + tasks[taskKey]["proto"] + "@" + tasks[taskKey]["sport"] + "@" + tasks[taskKey]["dport"]
                        else:
                            strTasks += tasks[taskKey]["id"] + "@" + tasks[taskKey]["ip_addr"] + "@" + tasks[taskKey]["proto"] + "@" + tasks[taskKey]["sport"] + "@" + tasks[taskKey]["dport"] + "@@"
                    if len(tasks) > 0:
                        sock.sendto(strTasks.encode(), address)
                    else:
                        sock.sendto(b"FAILLED", address)

                elif recvDataSplit[1] == "engine_version":
                    sock.sendto(engineVersion.encode(), address)

    except Exception as e:
        print(e)
        pass
