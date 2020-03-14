from mininet.topo import Topo
from mininet.log import info
from mininet.node import Docker

class LinearDockerTopo( Topo ):
    "Creates a LinearTopo and adds a docker container."

    def __init__(self, amountOfSwitches=3, hostsPerSwitch=3, docker=True):
        Topo.__init__(self)

        hostNumber = 0
        lastSwitch = None
        for n in range(amountOfSwitches):
            # create switch
            switch = self.addSwitch('s%s' % n)

            # link switch to last switch, if any
            if lastSwitch is not None:
                self.addLink(switch, lastSwitch)
            lastSwitch = switch

            # create hosts and add them to switch
            for m in range(hostsPerSwitch):
                host = self.addHost('h%s' % hostNumber )
                self.addLink(host, switch)
                hostNumber += 1
            
        if(docker == False):
            return
            
        # create docker host
        ip = '10.0.0.253'
        dimage = 'own_test_container:ubuntu1804'
        volumes = ["/home:/home", # code sync
               "/etc/localtime:/etc/localtime"] # timezone to host timezone
        d0 = self.addHost('d0', cls=Docker, ip=ip, dimage=dimage, volumes=volumes) 

        # add docker host to switch 'in the middle'
        switches = self.switches()
        midSwitch = switches[len(switches)/2]
        self.addLink(midSwitch, d0)

class TopoRef20( Topo ):

    def __init__(self, addDocker=False):
        Topo.__init__(self)

        s = [0]
        for n in range(1,9):
            s.append(self.addSwitch('s%s' % n))

        h = [0]
        for n in range(1, 8):
            h.append(self.addHost('h%s' % n))

        linkopts = {'delay': '10ms'}

        self.addLink(h[1], s[1])
        self.addLink(h[2], s[3])
        self.addLink(h[3], s[4])
        self.addLink(h[4], s[6])
        self.addLink(h[5], s[6])
        self.addLink(h[6], s[7])
        self.addLink(h[7], s[8])

        self.addLink(s[1], s[2], **linkopts)
        self.addLink(s[1], s[3], **linkopts)
        self.addLink(s[2], s[4], **linkopts)
        self.addLink(s[3], s[4], **linkopts)
        self.addLink(s[3], s[7], **linkopts)
        self.addLink(s[4], s[6], **linkopts)
        self.addLink(s[5], s[4], **linkopts)
        self.addLink(s[5], s[3], **linkopts)
        self.addLink(s[5], s[7], **linkopts)
        self.addLink(s[5], s[6], **linkopts)
        self.addLink(s[7], s[8], **linkopts)
        self.addLink(s[5], s[8], **linkopts)

        if(addDocker):
            # create docker host
            ip = '10.0.0.10'
            dimage = 'own_test_container:ubuntu1804'
            volumes = ["/home:/home", # code sync
                "/etc/localtime:/etc/localtime"] # timezone to host timezone
            d0 = self.addHost('d0', cls=Docker, ip=ip, dimage=dimage, volumes=volumes, mac="00:00:00:00:00:10") 
            self.addLink(s[5], d0)

            
def create_dpid_from_id(msb, id):
    "create DPID with given MSB and ID (LSBs). Zero Pad in between to fill 16 character"
    id = str(id)

    dpid = msb + id.zfill(15)

    return dpid

def addLinkAndDebugPrint(topo, node1, node2):
    if node1.endswith("host") or node2.endswith("host"):
        topo.addLink(node1, node2)
        print('added link %s <-> %s' % (node1, node2))
    else:
        topo.addLink(node1, node2, **{'delay': '50ms'})
        print('added link %s <-> %s (artificial delay)' % (node1, node2))
    

# DXTTs, DXTs and TBSs are switches, each TBS is connected to exactly one host
# DXTTs DPID: 0x0 + id
# DXTs DPID:  0x1 + id
# TBS DPID:   0x2 + id
class EvalTetraTopo( Topo ):

    def __init__(self):
        Topo.__init__(self)
        self.dxtt = []
        self.dxt = []
        self.tbs = []
        self.tbsHosts = []
        self.dwsHosts = []
        self.addNodes()
        self.addLinks()
        

    def addNodes(self):
        self.addDxtt()
        self.addDxt()
        self.addTbs()
        self.addHosts()

    def addDxtt(self):
        # add 4 DXTTs
        for i in range(4):
            self.dxtt.append(self.addSwitch('dxtt%s' % (i + 1), dpid=str(i+1)))

    def addDxt(self):
        # add 10 DXTs
        for i in range(10):
            id = i + 1 # ID (LSBs of DPID)

            dpid = create_dpid_from_id("1", id) # DPID
             
            # finally add DXT switch with DPID
            self.dxt.append(self.addSwitch('dxt%s' % id, dpid=dpid))

    def addTbs(self):
        # add TBSs
        for i in range(24):
            id = i + 1 # ID

            dpid = create_dpid_from_id("2", id) # DPID

            self.tbs.append(self.addSwitch('tbs%s' % id, dpid=dpid))

    def addHosts(self):
        self.addTbsHosts()
        self.addDwsHosts()

    def addTbsHosts(self):
        for base_station in self.tbs:
            host = self.addHost(base_station + "host")
            addLinkAndDebugPrint(self, host, base_station)
            self.tbsHosts.append(host)

    def addDwsHosts(self):
        for dxt_switch in [self.dxt[3], self.dxt[4], self.dxt[8], self.dxt[9]]:
            host = self.addHost(dxt_switch + "host")
            addLinkAndDebugPrint(self, host, dxt_switch)
            self.dwsHosts.append(host)
        

    def addLinks(self):
        self.addDxttInterconnectLinks()
        self.addDxtToDxttLinks()
        self.addTbsToDxtLinks()

    def addDxttInterconnectLinks(self):
        # interconnect DXTTs (full mesh)
        for i in range(4):
            for j in range(i+1, 4):
                addLinkAndDebugPrint(self, self.dxtt[i], self.dxtt[j])

    def addDxtToDxttLinks(self):
        # connect DXTs with DXTTs (each DXT connected to 2 DXTTs)
        addLinkAndDebugPrint(self, self.dxt[0], self.dxtt[0])
        addLinkAndDebugPrint(self, self.dxt[0], self.dxtt[1])
        addLinkAndDebugPrint(self, self.dxt[1], self.dxtt[0])
        addLinkAndDebugPrint(self, self.dxt[1], self.dxtt[1])
        addLinkAndDebugPrint(self, self.dxt[2], self.dxtt[1])
        addLinkAndDebugPrint(self, self.dxt[2], self.dxtt[3])
        addLinkAndDebugPrint(self, self.dxt[3], self.dxtt[1])
        addLinkAndDebugPrint(self, self.dxt[3], self.dxtt[3])
        addLinkAndDebugPrint(self, self.dxt[4], self.dxtt[1])
        addLinkAndDebugPrint(self, self.dxt[4], self.dxtt[3])
        addLinkAndDebugPrint(self, self.dxt[5], self.dxtt[2])
        addLinkAndDebugPrint(self, self.dxt[5], self.dxtt[3])
        addLinkAndDebugPrint(self, self.dxt[6], self.dxtt[2])
        addLinkAndDebugPrint(self, self.dxt[6], self.dxtt[3])
        addLinkAndDebugPrint(self, self.dxt[7], self.dxtt[0])
        addLinkAndDebugPrint(self, self.dxt[7], self.dxtt[2])
        addLinkAndDebugPrint(self, self.dxt[8], self.dxtt[2])
        addLinkAndDebugPrint(self, self.dxt[8], self.dxtt[0])
        addLinkAndDebugPrint(self, self.dxt[9], self.dxtt[0])
        addLinkAndDebugPrint(self, self.dxt[9], self.dxtt[2])

    
    def addTbsToDxtLinks(self):
        # connect TBSs with DXTs (ring or star)
        addLinkAndDebugPrint(self, self.tbs[0], self.dxt[0])
        addLinkAndDebugPrint(self, self.tbs[1], self.dxt[0])

        addLinkAndDebugPrint(self, self.tbs[2], self.dxt[1])
        addLinkAndDebugPrint(self, self.tbs[3], self.dxt[1])
        addLinkAndDebugPrint(self, self.tbs[4], self.dxt[1])

        addLinkAndDebugPrint(self, self.tbs[5], self.dxt[2])
        addLinkAndDebugPrint(self, self.tbs[6], self.dxt[2])
        addLinkAndDebugPrint(self, self.tbs[6], self.tbs[5])

        addLinkAndDebugPrint(self, self.tbs[7], self.dxt[3])
        addLinkAndDebugPrint(self, self.tbs[8], self.dxt[3])

        addLinkAndDebugPrint(self, self.tbs[9], self.dxt[4])
        addLinkAndDebugPrint(self, self.tbs[10], self.dxt[4])

        addLinkAndDebugPrint(self, self.tbs[12], self.dxt[5])
        addLinkAndDebugPrint(self, self.tbs[11], self.dxt[5])
        addLinkAndDebugPrint(self, self.tbs[12], self.tbs[11])

        addLinkAndDebugPrint(self, self.tbs[13], self.dxt[6])
        addLinkAndDebugPrint(self, self.tbs[15], self.dxt[6])
        addLinkAndDebugPrint(self, self.tbs[15], self.tbs[14])
        addLinkAndDebugPrint(self, self.tbs[14], self.tbs[13])

        addLinkAndDebugPrint(self, self.tbs[16], self.dxt[7])
        addLinkAndDebugPrint(self, self.tbs[17], self.dxt[7])
        addLinkAndDebugPrint(self, self.tbs[17], self.tbs[16])

        addLinkAndDebugPrint(self, self.tbs[18], self.dxt[8])
        addLinkAndDebugPrint(self, self.tbs[19], self.dxt[8])
        addLinkAndDebugPrint(self, self.tbs[20], self.dxt[8])

        addLinkAndDebugPrint(self, self.tbs[21], self.dxt[9])
        addLinkAndDebugPrint(self, self.tbs[23], self.dxt[9])
        addLinkAndDebugPrint(self, self.tbs[21], self.tbs[22])
        addLinkAndDebugPrint(self, self.tbs[22], self.tbs[23])


