package org.onosproject.groupcom;

import thesiscode.common.group.AbstractMulticastGroup;
import thesiscode.common.group.IGroupIdentifier;

import java.util.Set;

/**
 * A service that can be queried for currently known multicast groups.
 */
public interface GroupManagementService {
    Set<AbstractMulticastGroup> getActiveGroups();

    AbstractMulticastGroup getGroupById(IGroupIdentifier id);
}
