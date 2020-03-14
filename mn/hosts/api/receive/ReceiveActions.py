import sys
import datetime, os
PATH_TO_MN = os.path.abspath(__file__).split("mn")[0]
sys.path.append(PATH_TO_MN)


import struct
import time

class IReceiveAction:
    "Represents a receive action, that is an action which is applied when a packet is received."

    def apply(self, addr, data):
        raise NotImplementedError

class LoggingReceiveAction( IReceiveAction ):
    "A logging receive action. When this receive action is applied to a packet, then the packet is logged to a file containing a timestamp."

    ## WARNING!!--> THIS DIRECTORY GETS WIPED ON STARTUP <--!!WARNING
    LOG_DIR = "%smn/logs" % PATH_TO_MN

    def __init__(self, logFilePrefix, server, logDirectory=LOG_DIR):
        self.logDirectory = logDirectory
        self.logFilePrefix = logFilePrefix
        self.LOGPATH = "%s/%s_server.log" % (logDirectory, logFilePrefix)
        self.log("This is the logfile of %s listening to (%s, %d)." %(logFilePrefix, server.listenIP, server.port), "w+")

    def apply(self, addr, data):
        "Logs the packet into the log file."
        timestamp = struct.unpack('!Q', bytearray(data[0:8]))[0]
        vnfs = data[8:]
        now_timestamp = int(round(time.time() * 1000))
        diff_timestamp = now_timestamp - timestamp
        self.log("From: %s: %s -> %s" %(addr, str(timestamp)+str(vnfs), "sending timestamp="+str(timestamp)+",VNF which processed this packets="+str(vnfs)+",delay="+str(diff_timestamp)+"ms"), "a")

    def log(self, logMsg, mode):
        "Logs a logMsg in the log file using the supplied mode for log file access."

        f = open(self.LOGPATH, mode)
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write("%s: %s\n" %(ts, logMsg))
        f.flush()
        f.close()


## dont use this anymore! (sendPacket was changed)
class MulticastReceiveAction( IReceiveAction ):
    "A multicast receive action. When this receive action is applied to a packet, the packet will be used for group communication/multicast."

    JOIN_MESSAGE = "join"
    LEAVE_MESSAGE = "leave"

    def __init__(self, server, joinMessage=JOIN_MESSAGE, leaveMessage=LEAVE_MESSAGE):
        self.joinMessage = joinMessage
        self.leaveMessage = leaveMessage
        self.server = server
        self.group = []
    
    def apply(self, addr, data):
        "Uses the packet for group management (if it contains JOIN_MESSAGE or LEAVE_MESSAGE) or as payload for a multicast to all group members."

        group = self.group

        # group management
        if data == self.joinMessage:
            if addr not in group:
                group.append(addr) 
            return
        elif data == self.leaveMessage:
            if addr in group:
                group.remove(addr)
            return

        # non-group members are not allowed to send multicast to group
        if addr not in group:
            return


        # sending a multicast to everyone in the group 
        for receiver in group:
            # do not echo packets
            if addr == receiver:
                continue

            # address of current group member == destination address of duplicated packet
            dip = receiver[0]
            dport = receiver[1]

            # source address of the packet currently being received == source address of duplicated packet
            sip = addr[0]
            sport = addr[1]

            manipulatedData = data + " I was manipulated by a MulticastReceiveAction!"

            #sendPacket(destinationIP=dip, sourceIP=sip, destinationPort=dport, sourcePort=sport, message=manipulatedData)
