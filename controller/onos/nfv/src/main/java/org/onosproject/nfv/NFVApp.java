package org.onosproject.nfv;

import gurobi.GRBEnv;
import gurobi.GRBException;
import org.apache.felix.scr.annotations.*;
import org.onlab.packet.*;
import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;
import org.onosproject.groupcom.GroupManagementService;
import org.onosproject.net.*;
import org.onosproject.net.device.DeviceEvent;
import org.onosproject.net.device.DeviceService;
import org.onosproject.net.flow.*;
import org.onosproject.net.host.HostService;
import org.onosproject.net.packet.*;
import org.onosproject.net.topology.*;
import org.onosproject.nfv.placement.deploy.NfvInstantiator;
import org.onosproject.nfv.placement.solver.*;
import org.onosproject.nfv.placement.solver.ilp.TopoSyncSFCPlacementSolver;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import thesiscode.common.flow.DefaultNfvTreeFlowPusher;
import thesiscode.common.group.*;
import thesiscode.common.group.igmp.IgmpGroupIdentifier;
import thesiscode.common.nfv.traffic.*;
import thesiscode.common.topo.*;
import thesiscode.common.tree.NFVPerSourceTree;

import java.util.*;
import java.util.stream.Collectors;

@Component(immediate = true)
public class NFVApp implements PacketProcessor {
    private Logger log = LoggerFactory.getLogger(getClass());

    public static ApplicationId appId;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    protected CoreService coreService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    private PacketService pktService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    private DeviceService deviceService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    private FlowRuleService flowRuleService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    private HostService hostService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    private TopologyService topoService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    private GroupManagementService groupManagementService;

    private INfvPlacementSolver solver;
    private NfvInstantiator instantiator;

    /*
     * when we receive a stream of packets, we only want to compute the tree upon reception of the first packet.
     */
    private boolean first = true;

    private GRBEnv env;
    private Map<DeviceId, Map<NprNfvTypes.Type, Integer>> vnfDeploymentCost;
    private Map<DeviceId, Map<NprNfvTypes.Type, Double>> hwAccelFactors;
    private Map<DeviceId, Map<NprResources, Integer>> resourceCapacity;
    private List<NprNfvTypes.Type> sfc;
    private DefaultNfvTreeFlowPusher pusher;

    @Activate
    public void activate() throws GRBException {
        appId = coreService.registerApplication("org.onosproject.nfv");
        byte[] ipProtosToRedirect = {IPv4.PROTOCOL_UDP};
        pktService.addProcessor(this, PacketProcessor.director(3));

        installDefaultFlows();

        log.info("Creating GRB Environment.");
        env = new GRBEnv("/home/felix/from_app.log");
        log.info("Created GRB Environment: {}", env);

        sfc = new ArrayList<>();
        sfc.add(NprNfvTypes.Type.TRANSCODER);
        sfc.add(NprNfvTypes.Type.INTRUSION_DETECTION);

        solver = new TopoSyncSFCPlacementSolver(OptimizationGoal.MIN_MAX_DELAYSUM_THEN_DEVIATION, false, env, 1.0);
        instantiator = new NfvInstantiator();
    }

    @Deactivate
    public void deactivate() throws GRBException {
        pktService.removeProcessor(this);
        flowRuleService.removeFlowRulesById(appId);
        env.dispose();
    }

    @Override
    public void process(PacketContext packetContext) {
        InboundPacket in = packetContext.inPacket();
        Ethernet eth = in.parsed();
        if (eth.getEtherType() == Ethernet.TYPE_IPV4) {
            IPv4 ip = (IPv4) eth.getPayload();
            Ip4Address srcIP = Ip4Address.valueOf(ip.getSourceAddress());
            Ip4Address dstIp = Ip4Address.valueOf(ip.getDestinationAddress());
            if (ip.getProtocol() == IPv4.PROTOCOL_UDP && dstIp.isMulticast()) {

                log.info("received UDP && multicast");

                if (!first) {
                    return;
                } else {
                    first = false;
                }

                TopologyGraph graph = topoService.getGraph(topoService.currentTopology());

                vnfDeploymentCost = computeDeploymentCost(graph);
                hwAccelFactors = computeHwAccelerationFactors(graph);
                resourceCapacity = computeResourceCapacities(graph);

                Set<TopologyVertex> wrappedVertices = wrapVertices(graph);
                Set<TopologyEdge> wrappedEdges = wrapEdges(graph, wrappedVertices);

                AbstractMulticastGroup group = groupManagementService.getGroupById(new IgmpGroupIdentifier(dstIp));

                if (group == null || group.isEmpty()) { // nothing to do, if group is not existing or empty
                    log.info("Group was null or empty, returning now.");
                    return;
                }

                NprTraffic traffic = getTraffic(in, wrappedVertices, group);
                List<NprTraffic> trafficList = new ArrayList<>();
                trafficList.add(traffic);
                NfvPlacementRequest req = new NfvPlacementRequest(wrappedVertices, wrappedEdges, trafficList, new ConstantLinkWeigher(10, 5));
                log.info("req: {}", req);
                NfvPlacementSolution solution = solver.solve(req);
                log.info("solution: {}", solution);

                Map<NprNfvTypes.Type, Set<ConnectPoint>> vnfCps = instantiateVNF(solution);
                pushTree(srcIP, group, traffic, solution, vnfCps);
            }
        }
    }

    private NprTraffic getTraffic(InboundPacket in, Set<TopologyVertex> wrappedVertices, AbstractMulticastGroup group) {
        DeviceId ingressDevId = in.receivedFrom().deviceId();
        TopologyVertex ingress = findByDevId(ingressDevId, wrappedVertices);
        Objects.requireNonNull(ingress,
                               "ingress was null, not contained in wrapped vertex set, " + "ingressDeviceId was" +
                                       ingressDevId);
        Set<DeviceId> egressDeviceIds = group.toDeviceIds()
                                             .stream()
                                             .filter(v -> !v.equals(ingressDevId))
                                             .collect(Collectors.toSet());
        Set<TopologyVertex> egress = new HashSet<>();
        for (DeviceId deviceId : egressDeviceIds) {
            TopologyVertex egressForDevId = findByDevId(deviceId, wrappedVertices);
            Objects.requireNonNull(ingress,
                                   "egress was null, not contained in wrapped vertex set, " + "egress DeviceId was" +
                                           deviceId);
            egress.add(egressForDevId);
        }

        return new NprTraffic(sfc, ingress, egress, 4);
    }

    private Set<TopologyEdge> wrapEdges(TopologyGraph graph, Set<TopologyVertex> wrappedVertices) {
        Set<TopologyEdge> wrappedEdges = new HashSet<>();
        for (TopologyEdge edge : graph.getEdges()) {
            wrappedEdges.add(new DefaultTopologyEdge(findByDevId(edge.src()
                                                                     .deviceId(), wrappedVertices), findByDevId(edge.dst()
                                                                                                                    .deviceId(), wrappedVertices), edge
                                                             .link()));
        }
        return wrappedEdges;
    }

    private Set<TopologyVertex> wrapVertices(TopologyGraph graph) {
        Set<TopologyVertex> wrappedVertices = new HashSet<>();
        for (TopologyVertex vert : graph.getVertexes()) {
            DeviceId deviceId = vert.deviceId();
            if (deviceId.toString().startsWith("of:0") || deviceId.toString().startsWith("of:1")) {
                wrappedVertices.add(new WrappedPoPVertex(vert, vnfDeploymentCost.get(deviceId), hwAccelFactors.get(deviceId), resourceCapacity
                        .get(deviceId)));
            } else {
                wrappedVertices.add(new WrappedVertex(vert));
            }
        }
        return wrappedVertices;
    }

    private Map<DeviceId, Map<NprResources, Integer>> computeResourceCapacities(TopologyGraph graph) {
        Map<DeviceId, Map<NprResources, Integer>> resourceCapacity = new HashMap<>();
        for (TopologyVertex vert : graph.getVertexes()) {
            if (vert.deviceId().toString().startsWith("of:0") || vert.deviceId().toString().startsWith("of:1")) {
                Map<NprResources, Integer> resourceToCapacity = new HashMap<>();
                resourceToCapacity.put(NprResources.CPU_CORES, 6);
                resourceToCapacity.put(NprResources.RAM_IN_GB, 2);
                resourceCapacity.put(vert.deviceId(), resourceToCapacity);
            }
        }
        return resourceCapacity;
    }

    private Map<DeviceId, Map<NprNfvTypes.Type, Double>> computeHwAccelerationFactors(TopologyGraph graph) {
        Map<DeviceId, Map<NprNfvTypes.Type, Double>> hwAccelFactors = new HashMap<>();

        for (TopologyVertex vert : graph.getVertexes()) {
            DeviceId deviceId = vert.deviceId();
            log.info("device id: {}", deviceId);

            if (!(vert.deviceId().toString().startsWith("of:0") || vert.deviceId().toString().startsWith("of:1"))) {
                continue;
            }

            Map<NprNfvTypes.Type, Double> typeToFactor = new HashMap<>();
            for (NprNfvTypes.Type type : NprNfvTypes.Type.values()) {
                if (type == NprNfvTypes.Type.TRANSCODER) {
                    // DXTT2 and DXT9 offer hw acceleration for transcoder
                    if (deviceId.toString().contains("0000000000000002") ||
                            deviceId.toString().contains("1000000000000009")) {
                        log.info("setting HW acc for {}", deviceId);
                        typeToFactor.put(type, 0.25);
                    } else {
                        typeToFactor.put(type, 1.0);
                    }
                } else {
                    typeToFactor.put(type, 1.0);
                }
            }
            hwAccelFactors.put(deviceId, typeToFactor);
        }
        return hwAccelFactors;
    }

    private Map<DeviceId, Map<NprNfvTypes.Type, Integer>> computeDeploymentCost(TopologyGraph graph) {
        Map<DeviceId, Map<NprNfvTypes.Type, Integer>> vnfDeploymentCost = new HashMap<>();

        Map<NprNfvTypes.Type, Integer> typeToCost = new HashMap<>();
        for (NprNfvTypes.Type type : NprNfvTypes.Type.values()) {
            typeToCost.put(type, 40);
        }

        for (TopologyVertex vert : graph.getVertexes()) {
            if (vert.deviceId().toString().startsWith("of:0") || vert.deviceId().toString().startsWith("of:1")) {
                vnfDeploymentCost.put(vert.deviceId(), typeToCost);
            }
        }
        return vnfDeploymentCost;
    }

    private void pushTree(Ip4Address srcIP, AbstractMulticastGroup group, NprTraffic traffic, NfvPlacementSolution solution, Map<NprNfvTypes.Type, Set<ConnectPoint>> vnfCps) {
        IGroupMember src = new WrappedHost(hostService.getHostsByIp(srcIP).iterator().next());
        Set<IGroupMember> dsts = new HashSet<>(group.getGroupMembers());
        dsts.removeIf(dst -> dst.getIpAddress().equals(src.getIpAddress()));

        pusher = new DefaultNfvTreeFlowPusher(appId, flowRuleService);

        List<Set<TopologyEdge>> solutionEdges = solution.getLogicalEdgesPerTraffic().get(traffic);

        if (!(solutionEdges.size() == traffic.getSfc().size() + 1)) {
            throw new IllegalStateException("wrong solution edges size: " + solutionEdges.size() + ", " + "expected " +
                                                    (traffic.getSfc().size() + 1));
        }

        List<Set<Link>> solutionLinks = solutionEdges.stream()
                                                     .map(x -> x.stream()
                                                                .map(TopologyEdge::link)
                                                                .collect(Collectors.toSet()))
                                                     .collect(Collectors.toList());

        List<Set<ConnectPoint>> solutionVnfCps = new ArrayList<>();
        for (NprNfvTypes.Type type : traffic.getSfc()) {
            solutionVnfCps.add(vnfCps.get(type));
        }

        NFVPerSourceTree nfvTree = new NFVPerSourceTree(src, solutionLinks, dsts, solutionVnfCps, group);
        pusher.pushTree(nfvTree);
    }

    private Map<NprNfvTypes.Type, Set<ConnectPoint>> instantiateVNF(NfvPlacementSolution solution) {
        Map<NprNfvTypes.Type, Set<TopologyVertex>> toInstantiate = solution.getSharedPlacements();
        Map<NprNfvTypes.Type, Set<ConnectPoint>> vnfCps = new HashMap<>();

        for (NprNfvTypes.Type type : toInstantiate.keySet()) {
            Set<ConnectPoint> cpsForType = new HashSet<>();
            vnfCps.put(type, cpsForType);
            for (TopologyVertex vert : toInstantiate.get(type)) {
                if (vert instanceof WrappedPoPVertex) {
                    WrappedPoPVertex wrapped = (WrappedPoPVertex) vert;
                    if (wrapped.hwAccelerationOffered(type)) {
                        cpsForType.add(instantiator.instantiate(type, deviceService.getDevice(vert.deviceId()), true));
                    } else {
                        cpsForType.add(instantiator.instantiate(type, deviceService.getDevice(vert.deviceId()), false));
                    }
                } else {
                    throw new IllegalStateException(
                            "Trying to instantiate VNF at vert which is not a PoP (" + type.name() + "@" +
                                    vert.deviceId().toString() + ")");
                }
            }
        }
        return vnfCps;
    }

    private TopologyVertex findByDevId(DeviceId deviceId, Set<TopologyVertex> setToSearch) {
        for (TopologyVertex vertex : setToSearch) {
            if (vertex.deviceId().equals(deviceId)) {
                return vertex;
            }
        }
        return null;
    }

    private void installDefaultFlows() {
        // existing devices
        Set<FlowRule> flowRules = new HashSet<>();
        deviceService.getDevices().forEach(d -> flowRules.add(buildDefaultFlowRule(d.id())));
        flowRuleService.applyFlowRules(flowRules.toArray(new FlowRule[0]));

        // new devices
        deviceService.addListener(deviceEvent -> {
            if (deviceEvent.type() != DeviceEvent.Type.DEVICE_ADDED) {
                return;
            }
            flowRuleService.applyFlowRules(buildDefaultFlowRule(deviceEvent.subject().id()));
        });
    }

    private FlowRule buildDefaultFlowRule(DeviceId deviceId) {
        return DefaultFlowRule.builder()
                              .forDevice(deviceId)
                              .fromApp(appId)
                              .forTable(0)
                              .makePermanent()
                              .withPriority(FlowRule.MAX_PRIORITY - 2)
                              .withSelector(DefaultTrafficSelector.builder()
                                                                  .matchEthType(Ethernet.TYPE_IPV4)
                                                                  .matchIPProtocol(IPv4.PROTOCOL_UDP)
                                                                  .build())
                              .withTreatment(DefaultTrafficTreatment.builder().setOutput(PortNumber.CONTROLLER).build())
                              .build();
    }
}
