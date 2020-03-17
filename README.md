# TopoSync-SFC Code Repository
This repository contains the evaluation and prototype code related to the paper 
"TopoSync-SFC: SFC-aware Network-driven Synchronization of Multicast Traffic in Software-defined Environments" which was published at the NetSoft 2020 conference and authored by Felix Bachmann, Robert Bauer, Hauke Heseding, and Martina Zitterbart.
Our results were obtained with 
* ONOS SDN Controller (Version 1.13.6) 
* Gurobi ILP Solver (Version 8.1.0)
* Containernet v2.0 (using mininet Version 2.3.0d1) 
* Java 11
* Python 2.7.15+

Make sure to have all of the above installed and a valid Gurobi license set up (free for academic use).

## Reproduce the evaluation
 1. In the `nfv/` directory, navigate to the class `TopoSyncSFCEval`.
 2. Executing the JUnit tests in this class produces several .csv files in the `nfv/` directory, containing the evaluation data. (`eval()` and `runtimes()` produce the data shown in Fig. 8, `tradeoff()`produces the data shown in Fig. 9).  Note that the requests are generated randomly, so the exact data may vary but the trends should be the same.
 3. Create plots from the data using the python scripts in `eval/`. In `eval/data` you can find our evaluation data, i.e. the data we got from executing step 2 and which is shown in the evaluation section of the paper.
## Use the prototype
 1. Start an ONOS instance on localhost.
 2. Deploy the `NFVApp` on ONOS  using the script `nfv/buildAndDeploy.sh`. This may require installing the modules `common`and `groupcom`first. 
 3. Emulate the TETRA topology using `sudo python mn/startup/tetra_topo_test.py`. The script will start the topology and send ARP requests so that ONOS recognizes the hosts.
 4. Using the ONOS web GUI (http://localhost:8181/onos/ui/index.html) you should see that the ONOS connected to the network and recognized some hosts, ![similar to this screenshot](https://raw.githubusercontent.com/kit-tm/toposync/master/onos_screen.png)
 4. Enter `quit` in the containernet shell to send IGMP requests from some hosts to join a group. You should see the `IgmpGroupManager`updating its state in the ONOS shell.
 5. Enter `quit`again to start sending data from one source to the group. This triggers the app to install flow rules and instantiate the VNF according to the TopoSync-SFC ILP. You can trace the VNF instantiation using the containernet and ONOS shell. The installed flow rules can be checked, for example, using the ONOS web GUI. 
 6. Now you can send data from the source to the group using `tbs17host java -classpath <PATH-TO-REPO>/mn/hosts/cli/UDP PeriodicUDP 10.0.0.21 224.2.3.4 17 66 33`. You can check that the data arrived and was processed by the VNFs by investigating the logs in `mn/logs`: Each destination host logs the received data in its own file. Each line in a log file is the payload of one UDP packet, which includes a timestamp and the source-to-destination delay. Also, each VNF concatenates its own name/type as a String to the payload.
