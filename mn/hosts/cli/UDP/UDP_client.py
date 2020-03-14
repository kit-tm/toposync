# argument parsing
import argparse

# for packet crafting
import logging
scapyLogger = logging.getLogger("scapy.runtime")
scapyLogger.setLevel(logging.ERROR)
from scapy.all import *
scapyLogger.setLevel(logging.WARNING)

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('sip', help="source ip adress", type=str)
    parser.add_argument('dip', help="destination ip adress", type=str)
    parser.add_argument('interface', help="layer 2 interface", type=str)
    parser.add_argument('-sport', help="source port", default=6666, type=int)
    parser.add_argument('-dport', help="destination port", default=6666, type=int)
    parser.add_argument('-msg', help="message that is contained within the UDP packet", default="Brandnew Crispy Payload data of an UDP packet!")
    parser.add_argument('-c', help="amount of UDP packets to be sent", default=1)
    return parser.parse_args()

def sendPacket(destinationIP, sourceIP, destinationPort, sourcePort, message, count=1, iface=None):
    pkt = Ether()/IP(dst=destinationIP, src=sourceIP, ttl=42)/UDP(dport=destinationPort, sport=sourcePort)/Raw(load=message)
    for n in range(count):
        #send(pkt, verbose=0) 
        if(iface is not None):
            sendp(pkt, iface=iface, verbose=0)
        else:
            send(pkt)

def main():
    args = parse()
    sendPacket(args.dip, args.sip, args.dport, args.sport, args.msg, args.c)

if __name__ == "__main__":
    main()