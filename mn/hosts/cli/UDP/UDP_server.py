import sys
import os
PATH_TO_MN = os.path.abspath(__file__).split("mn")[0]
sys.path.append(PATH_TO_MN)

from mn.hosts.api.receive.ReceiveActions import LoggingReceiveAction, MulticastReceiveAction
import argparse
from mn.hosts.api.UDP.UDPServer import UDPServer

## parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('listen_ip', help="ip adress to listen to")
parser.add_argument('name', help="name of the node. is used as prefix for logfile")
parser.add_argument('host_ip', help="ip of the interface on which multicast traffic should be received")
parser.add_argument('-port', help="port to listen to", default=6666, type=int)
parser.add_argument('-log', help="adds the LoggingReceiveAction to the UDP server", action="store_true")
parser.add_argument('-multi', help="adds the MulticastReceiveAction to the UDP server", action="store_true")
args = parser.parse_args()

# create server
server = UDPServer(listenIP=args.listen_ip, port=args.port, hostIP=args.host_ip)

# create list of IReceiveAction instances
actions = []
if(args.log):
    actions.append(LoggingReceiveAction(args.name, server))
if(args.multi):
    actions.append(MulticastReceiveAction(server=server))

# add actions to server
server.addReceiveActions(actions)

# server starts receiving
server.startReceiveLoop()