import argparse

parser = argparse.ArgumentParser()
parser.add_argument("sourceIP", help="source IP of the created packet, as string", type=str)
parser.add_argument("destinationIP", help="destination IP of the created packet, as string", type=str)
parser.add_argument("ip_proto", help="the ip protocol", type=int)
parser.add_argument("interface", help="layer 2 interface", type=str)
parser.add_argument("sourceMAC", help="source MAC of the created packet, as string", type=str)
parser.add_argument("-ip_tos", default=0)
parser.add_argument("-ip_id", default=1337)
parser.add_argument("-ip_ttl", default=0)
args = parser.parse_args()

from scapy.all import *
eth = Ether(src=args.sourceMAC)
ip = IP(src=args.sourceIP, dst=args.destinationIP, proto=args.ip_proto)
pkt = eth/ip
pkt.show2()
sendp(pkt, iface=args.interface)