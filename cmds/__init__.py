import subprocess


def allowFirewall(proto, sport):
    subprocess.call('netsh.exe advfirewall firewall add rule name="' + proto + ' Port ' + sport +
                    '" dir=in action=allow protocol=' + proto + ' localport=' + sport, shell=True)

def tcpForwarding(wslIp, sport, dport):
    subprocess.call('netsh.exe interface portproxy add v4tov4 listenport=' + sport +
                    ' listenaddress=0.0.0.0 connectport=' + dport + ' connectaddress=' + wslIp,
                    shell=True)

def unallowFirewall(proto, sport):
    subprocess.call('netsh.exe advfirewall firewall delete rule name="'+proto+' Port ' + sport +
                    '" protocol=' + proto+ ' localport=' + sport, shell=True)


def unforwardingTCP(sport):
    subprocess.call('netsh.exe interface portproxy delete v4tov4 listenport=' + sport+ ' listenaddress=0.0.0.0', shell=True)
