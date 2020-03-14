import sys 
import time
import threading
import os

from mininet.net import Containernet
from mininet.link import TCLink
from mininet.node import RemoteController, Docker
from mininet.cli import CLI
from mininet.log import setLogLevel, info

PATH_TO_MN = os.path.abspath(__file__).split("mn")[0]
sys.path.append(PATH_TO_MN)

from mn.hosts.api.receive.ReceiveActions import LoggingReceiveAction
from mn.topo.Topos import EvalTetraTopo
from mn.cn_rest import start_rest


# originates from https://www.etsi.org/deliver/etsi_en/300300_300399/30039502/01.03.01_60/en_30039502v010301p.pdf
# TETRA speech codec
UDP_MESSAGE_SIZE_BYTES = 17
PACKETS_PER_SECOND = 33
PACKET_COUNT = PACKETS_PER_SECOND * 2

GROUP_IP = "224.2.3.4"

def printAndExecute(host, cmdString):
    print("%s: %s" % (host.name, cmdString))
    host.cmd(cmdString)

def startUDPClient(host, groupIP, msgsize, count, rate, sport=6666, dport=6666):
    cmdString = 'java -classpath %smn/hosts/cli/UDP PeriodicUDP %s %s %s %s %s' % (PATH_TO_MN, host.IP(), groupIP, msgsize, count, rate) 
    printAndExecute(host, cmdString)

def startUDPServer(host, listenIP, hostIP):
    cmdString = 'python %smn/hosts/cli/UDP/UDP_server.py \"%s\" \"%s\" \"%s\" -log &' % (PATH_TO_MN, listenIP, host.name, hostIP)
    printAndExecute(host, cmdString)

def startARP(host, srcIP, srcMAC, dstIP, iface):
    cmdString = 'python %smn/hosts/cli/ARP/ARP_client.py \"%s\" %s %s %s' % (PATH_TO_MN, srcIP, dstIP, srcMAC, iface)
    printAndExecute(host, cmdString)

def startIP(host, srcIP, dstIP, ipProto, iface, srcMAC):
    cmdString = 'python %smn/hosts/cli/RAW/IPClient.py %s %s %s %s %s' % (PATH_TO_MN, srcIP, dstIP, ipProto, iface, srcMAC)
    printAndExecute(host, cmdString)

def main():
    setLogLevel('info')

    topo = EvalTetraTopo()

    net = Containernet(controller=RemoteController, topo=topo, build=False, autoSetMacs=True, link=TCLink)
    net.start()

    print()

    print("**Wiping log dir.")
    for root, dirs, files in os.walk(LoggingReceiveAction.LOG_DIR):
        for file in files:
            os.remove(os.path.join(root, file))

    print("**Starting containernet REST Server.")
    thr = threading.Thread(target=start_rest, args=(net,)) # comma behind net is on purpose
    thr.daemon = True
    thr.start()

    # wait for connection with controller
    time.sleep(3)

    hosts = net.hosts

    # send arp from reqHost to every other host -> required by ONOS HostService to resolve hosts (i.e. map MAC<->IP)
    reqHost = hosts[0]
    for host in hosts:
        if(host is not reqHost):
            startARP(reqHost, reqHost.IP(), reqHost.MAC(), host.IP(), reqHost.intf())

    CLI(net)

    ## set up UDP servers to join group
    for host in hosts:
        if host.name in ['tbs10host', 'tbs11host', 'tbs4host', 'tbs21host']:
            startUDPServer(host, GROUP_IP, host.IP())

    CLI(net)

    ## send data
    startUDPClient(net.getNodeByName('tbs17host'), GROUP_IP, UDP_MESSAGE_SIZE_BYTES, count=PACKET_COUNT, rate=PACKETS_PER_SECOND)

    CLI(net)

    net.stop()

if __name__ == '__main__':
    main()

