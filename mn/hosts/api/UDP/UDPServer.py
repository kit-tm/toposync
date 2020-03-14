import socket
import struct
from netaddr import IPNetwork, IPAddress

class UDPServer:
    "A UDP server which applies a list of IReceiveAction instances to each received UDP packet."

    def __init__(self, listenIP, hostIP, port=6666):
        self.receiveActions = []
        self.listenIP = listenIP
        self.hostIP = hostIP
        self.port = port
        self.bindToSocket()

    def bindToSocket(self):
        "Creates a socket object and binds to it"

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
        sock = self.sock
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # prevent error when using socket a short time afterwards
        if IPAddress(self.listenIP) in IPNetwork("224.0.0.0/4"):
            group = socket.inet_aton(self.listenIP)
            intf = self.hostIP
            print("listenIP: %s" % self.listenIP)
            print("intf: %s" % intf)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, group + socket.inet_aton(intf))

        sock.bind((self.listenIP, self.port))
            

    def addReceiveActions(self, action):
        "Adds the action list to the list of IReceiveAction instances which are applied at UDP packet reception."

        self.receiveActions.extend(action)

    def startReceiveLoop(self):
        "start receiving UDP packets and apply receiveActions"

        rcv_cnt = 0
        while True:
            data, addr = self.sock.recvfrom(4096)
            for action in self.receiveActions:
                action.apply(addr, data)
            rcv_cnt += 1