package org.onosproject.nfv.placement.deploy;

import org.onosproject.net.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import thesiscode.common.nfv.traffic.NprNfvTypes;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.stream.Collectors;

/**
 * Instantiates VNFs at switches.
 */
public class NfvInstantiator {
    private Logger log = LoggerFactory.getLogger(getClass());


    /**
     * Instantiates a VNF at a switch. Uses the REST interface started in the containernet instance to do so.
     *
     * @param vnfType        the type of the VNF to instantiate
     * @param switchToAttach the switch at which the VNF shall be instantiated
     * @param hwAccelerated  whether or not the node offers hardware acceleration for vnfType
     * @return the connectpoint (switch and port) at which the VNF was instantiated
     */
    public ConnectPoint instantiate(NprNfvTypes.Type vnfType, Device switchToAttach, boolean hwAccelerated) {
        URL url = null;
        HttpURLConnection con = null;
        String instantiatedAtPort = null;
        try {
            String urlString = "http://localhost:9000/" + switchToAttach.id().uri().getSchemeSpecificPart() + "/" +
                    vnfType.toString();

            if (hwAccelerated) {
                urlString += "_accelerated";
            }
            url = new URL(urlString);
            log.info("sending request to {}", url);
            con = (HttpURLConnection) url.openConnection();
            con.setRequestMethod("PUT");
            instantiatedAtPort = new BufferedReader(new InputStreamReader(con.getInputStream())).lines()
                                                                                                .collect(Collectors.joining());
            log.info("response code: {}", con.getResponseCode());
            log.info("instated at port: {}", instantiatedAtPort);
        } catch (IOException e) {
            e.printStackTrace();
        }
                /*
                stub
                 */
        ConnectPoint cp = new ConnectPoint(switchToAttach.id(), PortNumber.portNumber(Integer.parseInt(instantiatedAtPort)));
        log.info("VNF {} instantiated at cp: {}", vnfType, cp);
        return cp;
    }
}
