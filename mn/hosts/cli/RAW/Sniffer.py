# adapted from https://github.com/soarpenguin/python-scripts/blob/master/sniffer.py
import binascii
import socket, sys
import ipaddress
import argparse
import time
import csv
from struct import *
from scapy.all import *
import os
PATH_TO_MN = os.path.abspath(__file__).split("mn")[0]
sys.path.append(PATH_TO_MN)
#from mn.hosts.api.group.groupmanagement import GroupManager
from mn.hosts.cli.UDP.UDP_client import sendPacket
import threading

#manager = GroupManager()

#Convert a string of 6 characters of ethernet address into a dash separated hex string
def eth_addr (a) :
    b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]) , ord(a[1]) , ord(a[2]), ord(a[3]), ord(a[4]) , ord(a[5]))
    return b

parser = argparse.ArgumentParser()
parser.add_argument("iface", help="layer 2 interface to redirect multicast packets to", type=str)
parser.add_argument("delay", help="delay which should be added by this VNF", type=int)
parser.add_argument("name", help="VNF name to concatenate to UDP payload", type=str)
parser.add_argument('--time', dest='time', action='store_true')
parser.add_argument('--v', help="verbose", action="store_true")
args = parser.parse_args()


s = socket.socket( socket.AF_PACKET , socket.SOCK_RAW , socket.ntohs(0x0003))

def sleep(time_in_ms):
    time.sleep(time_in_ms / 1000.0)


scapy_sock = conf.L2socket(iface=args.iface)

def debug_send(pkt):
    print ("sending now")
    pkt.show()
    scapy_sock.send(bytes(pkt))
    print("sent")

print("starting to receive")
while True:
    packet = s.recvfrom(10000)

    # time of reception
    reception_time = int(round(time.time() * 1000))

    packet = packet[0]

    eth_length = 14

    eth_header = packet[:eth_length]
    eth = unpack('!6s6sH' , eth_header)
    eth_type = eth[2]
    eth_dst = eth_addr(packet[0:6])
    eth_src = eth_addr(packet[6:12])
    if(args.v):
        print('Ethernet[Dst: %s, Src: %s, EtherType: %s]' % (eth_dst, eth_src, hex(eth_type)))

    if eth_type == 0x0800:
        #Parse IP header
        #take first 20 characters for the ip header
        ip_header = packet[eth_length:20+eth_length]

        #now unpack them :)
        iph = unpack('!BBHHHBBH4s4s' , ip_header)

        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF

        iph_length = ihl * 4

        ttl = iph[5]
        protocol = iph[6]
        s_addr = socket.inet_ntoa(iph[8])
        d_addr = socket.inet_ntoa(iph[9])

        if args.v:
            print('IP[Proto: %s, Src: %s, Dst: %s, ttl: %s]' % (hex(protocol), s_addr, d_addr, ttl))

        ## IGMP
        if protocol == 0x2:
            if args.v:
                print('IGMP[')

            igmp_start = iph_length + eth_length

            igmp_type = packet[igmp_start:igmp_start+1]

            # look at type
            igmp_t = unpack('!B' , igmp_type)

            igmp_type = igmp_t[0]
            if igmp_type == 0x16: #IGMPv2 Join
                if args.v:
                    print("v2 join")
            elif igmp_type == 0x17: #IGMPv2 Leave
                if args.v:
                    print("v2 leave")
            elif igmp_type == 0x22: #IGMPv3 Join/Leave
                if args.v:
                    print('v3 join/leave')

                # get amount of group records
                igmpv3_num_group_records = packet[igmp_start+6:igmp_start+8]
                igmpv3_n = unpack('!H', igmpv3_num_group_records)[0]
                if args.v:
                    print('num of group records: %s' % igmpv3_n)

                next_group_record = igmp_start + 8
                # unpack each group record 
                for n in range(0, igmpv3_n):
                    if args.v:
                        print("group record %s:" % n)
                    group_record = packet[next_group_record:next_group_record+8]
                    group_r = unpack('!BBH4s', group_record)
                    
                    record_type = group_r[0]
                    aux_data_len = group_r[1]
                    num_sources = group_r[2]
                    group_addr = socket.inet_ntoa(group_r[3])

                    if args.v:
                        print("record type %s, aux_data_len %s, num_sources %s, group_addr %s" % (record_type, aux_data_len, num_sources, group_addr))

                    if record_type == 3: # CHANGE_TO_INCLUDE_MODE
                        if num_sources == 0: # include zero sources -> leave group
                            if args.v:
                                print('it is a leave!')
                            #manager.handleLeave(group_addr, s_addr, eth_src)
                    if record_type == 4: # CHANGE_TO_EXCLUDE_MODE
                        if num_sources == 0: # exlude zero sources -> join group
                            if args.v:
                                print('it is a join!')
                            #manager.handleJoin(group_addr, s_addr, eth_src)

                    # NOTE: ignore aux data and source addresses and go to next group record
                    next_group_record = next_group_record + aux_data_len * 4 + num_sources * 4 + 8

            if args.v:
                print(']')

        ## UDP
        elif protocol == 17:
            u = iph_length + eth_length
            udph_length = 8
            udp_header = packet[u:u+8]

            #now unpack them :)
            udph = unpack('!HHHH' , udp_header)

            source_port = udph[0]
            dest_port = udph[1]
            length = udph[2]
            checksum = udph[3]

            h_size = eth_length + iph_length + udph_length
            data_size = len(packet) - h_size

            #get data from the packet
            data = packet[h_size:]
            if args.v:
                print("UDP[SrcPort: %s, DstPort: %s, Len: %s, Checksum: %s, Data: %s" % (source_port, dest_port, length, hex(checksum), binascii.hexlify(data)))
            #manager.redirectUDPTraffic(d_addr, s_addr, source_port, dest_port, data)

            if ipaddress.IPv4Address(iph[9]).is_multicast: 
                # ttl 42 are packets sent Transcoder, ttl 43 sent by intrusion detection -> ignore packets sent by "us" -> avoid processing packets several times if looped back to the VNF
                if( ((args.name == "TRANSCODER" or args.name == "TRANSCODER_accelerated") and ttl != 42) or  args.name == "INTRUSION_DETECTION" and ttl != 43): 
                    
                    print("from receive to before send: %s" % (int(round(time.time() * 1000)) - reception_time))
                    data += args.name
                    ether_dst = ""
                    ttl = 0
                    if args.name == "TRANSCODER" or args.name == "TRANSCODER_accelerated":
                        ether_dst = "22:22:22:22:22:22"
                        ttl = 42
                    elif args.name == "INTRUSION_DETECTION":
                        ether_dst = "33:33:33:33:33:33"
                        ttl = 43
                        
                    print("args.name: %s" % args.name)
                    print("ether dst: %s" % ether_dst)

                    pkt = Ether(dst=ether_dst)/IP(dst=d_addr, src=s_addr, ttl=ttl)/UDP(dport=dest_port, sport=source_port)/Raw(load=data)
                    before_send = int(round(time.time() * 1000))
                    if before_send - reception_time >= args.delay: # if delay by unpacking the packet already exceeds the delay, instantly send the packet back
                        print("sending packet right away")
                        scapy_sock.send(pkt)
                    else:
                        #print("sleeping for %s ms" % (args.delay - (before_send - reception_time)))
                        print("scheduling sending for in %s seconds." % str((args.delay - (before_send - reception_time)) / 1000.0))
                        t = threading.Timer((args.delay - (before_send - reception_time)) / 1000.0, debug_send, args=[pkt])
                        t.start()
                        #time.sleep()
                        #print("sending packet now")
                        #scapy_sock.send(pkt)   

        else :
            print('unhandled IP protocol: ' + str(protocol))