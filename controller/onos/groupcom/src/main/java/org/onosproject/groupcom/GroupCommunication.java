/*
 * Copyright 2018-present Open Networking Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.onosproject.groupcom;

import org.apache.felix.scr.annotations.*;
import org.onosproject.core.ApplicationId;
import org.onosproject.core.CoreService;
import org.onosproject.net.*;
import org.onosproject.net.device.DeviceEvent;
import org.onosproject.net.device.DeviceService;
import org.onosproject.net.flow.*;
import org.onosproject.net.host.HostService;
import org.onosproject.net.packet.PacketProcessor;
import org.onosproject.net.packet.PacketService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import thesiscode.common.group.*;
import thesiscode.common.group.igmp.IgmpGroupManager;

import java.util.Set;

/**
 * ONOS component which handles the group management (installs rule to forward relevant group management packets to
 * controller, e.g. IGMP) and forwards them to a {@link AbstractGroupManager}.
 */
@Component(immediate = true)
@Service
public class GroupCommunication implements GroupManagementService {
    private final Logger log = LoggerFactory.getLogger(getClass());

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    protected PacketService pktService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    protected CoreService coreService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    protected DeviceService deviceService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    protected FlowRuleService flowRuleService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY_UNARY)
    private HostService hostService;

    public static ApplicationId appId;
    private AbstractGroupManager groupManager;

    @Activate
    protected void activate() {
        appId = coreService.registerApplication("org.onosproject.groupcom");

        groupManager = new IgmpGroupManager(hostService);

        installDefaultFlowRules();

        log.info("groupManager: {}", groupManager);

        // let group manager receive packets
        pktService.addProcessor(groupManager, PacketProcessor.director(2));
        log.info("Activated.");
    }

    @Deactivate
    protected void deactivate() {
        flowRuleService.removeFlowRulesById(appId);
        pktService.removeProcessor(groupManager);
        log.info("Deactivated.");
    }

    /**
     * installs the default flow rules
     */
    private void installDefaultFlowRules() {
        // for all existing devices
        for (Device device : deviceService.getDevices()) {
            flowRuleService.applyFlowRules(buildDefaultFlowRule(device.id()));
        }

        // for all devices, which may be added to the topology later on
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
                              .forTable(0)
                              .makePermanent()
                              .withSelector(groupManager.getSelector())
                              .withTreatment(DefaultTrafficTreatment.builder().setOutput(PortNumber.CONTROLLER).build())
                              .fromApp(appId)
                              .withPriority(FlowRule.MAX_PRIORITY)
                              .build();
    }

    @Override
    public Set<AbstractMulticastGroup> getActiveGroups() {
        return groupManager.getGroups();
    }

    @Override
    public AbstractMulticastGroup getGroupById(IGroupIdentifier id) {
        return groupManager.getGroupById(id);
    }
}
