package org.onosproject.nfv.placement.solver.ilp;

import gurobi.GRBEnv;
import gurobi.GRBException;
import org.junit.*;
import org.onosproject.net.topology.TopologyVertex;
import org.onosproject.nfv.placement.solver.*;
import thesiscode.common.nfv.traffic.NprNfvTypes;
import thesiscode.common.nfv.traffic.NprTraffic;
import thesiscode.common.topo.ConstantLinkWeigher;
import thesiscode.common.topo.ILinkWeigher;
import thesiscode.common.util.CustomDemandBuilder;
import util.mock.EvalTopoMockBuilder;
import util.mock.TestGraph;

import java.io.*;
import java.util.*;
import java.util.concurrent.ThreadLocalRandom;

public class TopoSyncSFCEval {
    private GRBEnv env;


    @Before
    public void setUp() throws GRBException {
        env = new GRBEnv("");
    }

    /**
     * used for the evaluation experiments
     *
     * @throws IOException if opening/writing to the CSV files fails
     */
    @Test
    public void eval() throws IOException {
        final int MAX_SFC_LENGTH = 2;
        final int RUNS = 1000;

        TestGraph graph = EvalTopoMockBuilder.getEvalTopo();

        ILinkWeigher lw = new ConstantLinkWeigher(10, 5);

        PrintWriter networkLoadPrintWriter = new PrintWriter(new FileWriter("network_load.csv", true));
        PrintWriter delaySumPrintWriter = new PrintWriter(new FileWriter("delay_sum.csv", true));
        PrintWriter deviationSumPrintWriter = new PrintWriter(new FileWriter("deviation_sum.csv", true));

        List<TopologyVertex> ingressList = new ArrayList<>();
        List<Set<TopologyVertex>> egressList = new ArrayList<>();

        int successfulRuns = 0;

        while (successfulRuns < RUNS) {
            System.out.println(String.format("########## run %s of %s ##########", successfulRuns, RUNS));
            for (int i = 0; i < 3; i++) {
                // choose random ingress
                Set<TopologyVertex> tbsSet = new HashSet<>(graph.getTbs());
                Set<TopologyVertex> dxtSet = new HashSet<>(graph.getDxt());
                TopologyVertex[] availableTbsArr = tbsSet.toArray(new TopologyVertex[0]);
                TopologyVertex[] availableDxtArr = dxtSet.toArray(new TopologyVertex[0]);

                if (ThreadLocalRandom.current().nextInt(100) < 25) {
                    // source = DXT
                    int index = ThreadLocalRandom.current().nextInt(availableDxtArr.length);
                    TopologyVertex ingress = availableDxtArr[index];
                    ingressList.add(ingress);
                } else {
                    // source = TBS
                    int index = ThreadLocalRandom.current().nextInt(availableTbsArr.length);
                    TopologyVertex ingress = availableTbsArr[index];
                    tbsSet.remove(ingress);
                    availableTbsArr = tbsSet.toArray(new TopologyVertex[0]);
                    ingressList.add(ingress);
                }


                // choose random egress
                Set<TopologyVertex> currentEgress = new HashSet<>();
                while (currentEgress.size() < 3) {
                    int index = ThreadLocalRandom.current().nextInt(availableTbsArr.length);
                    TopologyVertex chosenEgress = availableTbsArr[index];
                    if (chosenEgress.deviceId().toString().startsWith("tbs")) {
                        currentEgress.add(chosenEgress);
                    }
                    tbsSet.remove(chosenEgress);
                    availableTbsArr = tbsSet.toArray(new TopologyVertex[0]);
                }
                egressList.add(currentEgress);
            }

            ArrayList<Double> loadListRef = new ArrayList<>();
            ArrayList<Double> deviationListRef = new ArrayList<>();
            ArrayList<Double> delayListRef = new ArrayList<>();
            ArrayList<Double> loadListTopoSyncSFC = new ArrayList<>();
            ArrayList<Double> deviationListTopoSyncSFC = new ArrayList<>();
            ArrayList<Double> delayListTopoSyncSFC = new ArrayList<>();
            ArrayList<Double> loadListSt = new ArrayList<>();
            ArrayList<Double> deviationListSt = new ArrayList<>();
            ArrayList<Double> delayListSt = new ArrayList<>();

            for (int i = 0; i <= MAX_SFC_LENGTH; i++) {
                CustomDemandBuilder dg = new CustomDemandBuilder();
                for (int j = 0; j < 3; j++) {
                    dg.setIngress(ingressList.get(j))
                      .setEgress(egressList.get(j))
                      .setDemandValue(4)
                      .setRandomSfc(i)
                      .createDemand();
                }


                List<NprTraffic> demand = dg.generateDemand();
                System.out.println("finished building demand, here it is:");

                for (NprTraffic flow : demand) {
                    System.out.println(flow.toString());
                }

                NfvPlacementRequest req = new NfvPlacementRequest(graph.getVertexes(), graph.getEdges(), demand, lw);
                SfcPlacementSolver refSolver = new ReferencePlacementSolver(false, env, 1.0);
                NfvPlacementSolution refSol = refSolver.solve(req);
                if (refSol == null) {
                    System.out.println("refSol was not feasible, skip");
                    continue;
                }
                System.out.println("ref was feasible");


                SfcPlacementSolver topoSyncSFCPlacementSolver = new TopoSyncSFCPlacementSolver(OptimizationGoal.MIN_MAX_DELAYSUM_THEN_DEVIATION, false, env, 1.0);
                NfvPlacementSolution topoSyncSFCSolution = topoSyncSFCPlacementSolver.solve(req);
                if (topoSyncSFCSolution == null) {
                    System.out.println("TopoSync-SFC was not feasible, skip");
                    continue;
                }
                System.out.println("TopoSync-SFC was feasible");

                SfcPlacementSolver stSolver = new STSfcPlacementSolver(OptimizationGoal.MIN_MAX_DELAYSUM_THEN_DEVIATION, false, env, 1.0);
                NfvPlacementSolution stSol = stSolver.solve(req);
                if (stSol == null) {
                    System.out.println("ST was not feasible, skip");
                    continue;
                }
                System.out.println("ST was feasible");


                System.out.println("modelling times: " + topoSyncSFCPlacementSolver.getModelTime() + "," +
                                           stSolver.getModelTime());
                System.out.println(
                        "runtimes: " + topoSyncSFCPlacementSolver.getLastRuntime() + "," + stSolver.getLastRuntime());
                System.out.println(
                        "load:" + refSol.getNetworkLoad() + " vs " + topoSyncSFCSolution.getNetworkLoad() + " vs. " +
                                stSol.getNetworkLoad());
                System.out.println(
                        "delaySum:" + refSol.getDelaySum() + " vs. " + topoSyncSFCSolution.getDelaySum() + " vs. " +
                                stSol.getDelaySum());
                System.out.println(
                        "deviationSum:" + refSol.getDeviationSum() + " vs. " + topoSyncSFCSolution.getDeviationSum() +
                                " vs. " + stSol.getDeviationSum());

                loadListRef.add(refSol.getNetworkLoad());
                loadListTopoSyncSFC.add(topoSyncSFCSolution.getNetworkLoad());
                loadListSt.add(stSol.getNetworkLoad());

                deviationListRef.add(refSol.getDeviationSum());
                deviationListTopoSyncSFC.add(topoSyncSFCSolution.getDeviationSum());
                deviationListSt.add(stSol.getDeviationSum());

                delayListRef.add(refSol.getDelaySum());
                delayListTopoSyncSFC.add(topoSyncSFCSolution.getDelaySum());
                delayListSt.add(stSol.getDelaySum());

                if (i == 2) {
                    successfulRuns++;
                    System.out.println("all were feasible, writing to file");

                    for (int x = 0; x < loadListRef.size(); x++) {
                        networkLoadPrintWriter.append(String.valueOf(loadListRef.get(x)))
                                              .append(",")
                                              .append(String.valueOf(loadListTopoSyncSFC.get(x)))
                                              .append(",")
                                              .append(String.valueOf(loadListSt.get(x)))
                                              .append("\n");
                    }
                    networkLoadPrintWriter.flush();

                    for (int x = 0; x < delayListRef.size(); x++) {
                        delaySumPrintWriter.append(String.valueOf(delayListRef.get(x)))
                                           .append(",")
                                           .append(String.valueOf(delayListTopoSyncSFC.get(x)))
                                           .append(',')
                                           .append(String.valueOf(delayListSt.get(x)))
                                           .append("\n");
                    }
                    delaySumPrintWriter.flush();

                    for (int x = 0; x < deviationListRef.size(); x++) {
                        deviationSumPrintWriter.append(String.valueOf(deviationListRef.get(x)))
                                               .append(",")
                                               .append(String.valueOf(deviationListTopoSyncSFC.get(x)))
                                               .append(',')
                                               .append(String.valueOf(deviationListSt.get(x)))
                                               .append("\n");
                    }
                    deviationSumPrintWriter.flush();
                }
            }
        }
    }

    /**
     * Used to measure the runtime
     *
     * @throws IOException
     */
    @Test
    public void runtime() throws IOException {
        final int RUNS = 1000;
        final int DEMANDS = 3;
        final int DESTINATIONS_PER_DEMAND = 3;
        final int MAX_SFC_LEN = 2;

        TestGraph graph = EvalTopoMockBuilder.getEvalTopo();

        ILinkWeigher lw = new ConstantLinkWeigher(10, 5);

        PrintWriter runTimePrintWriter = new PrintWriter(new FileWriter("runtime.csv", true));

        List<TopologyVertex> ingressList = new ArrayList<>();
        List<Set<TopologyVertex>> egressList = new ArrayList<>();

        int successfulRuns = 0;


        while (successfulRuns < RUNS) {
            for (int i = 0; i < DEMANDS; i++) {
                // choose random ingress
                Set<TopologyVertex> tbsSet = new HashSet<>(graph.getTbs());
                Set<TopologyVertex> dxtSet = new HashSet<>(graph.getDxt());
                TopologyVertex[] availableTbsArr = tbsSet.toArray(new TopologyVertex[0]);
                TopologyVertex[] availableDxtArr = dxtSet.toArray(new TopologyVertex[0]);

                if (ThreadLocalRandom.current().nextInt(100) < 25) {
                    // source = DXT
                    int index = ThreadLocalRandom.current().nextInt(availableDxtArr.length);
                    TopologyVertex ingress = availableDxtArr[index];
                    ingressList.add(ingress);
                } else {
                    // source = TBS
                    int index = ThreadLocalRandom.current().nextInt(availableTbsArr.length);
                    TopologyVertex ingress = availableTbsArr[index];
                    tbsSet.remove(ingress);
                    availableTbsArr = tbsSet.toArray(new TopologyVertex[0]);
                    ingressList.add(ingress);
                }


                // choose random egress
                Set<TopologyVertex> currentEgress = new HashSet<>();
                while (currentEgress.size() < DESTINATIONS_PER_DEMAND) {
                    int index = ThreadLocalRandom.current().nextInt(availableTbsArr.length);
                    TopologyVertex chosenEgress = availableTbsArr[index];
                    if (chosenEgress.deviceId().toString().startsWith("tbs")) {
                        currentEgress.add(chosenEgress);
                    }
                    tbsSet.remove(chosenEgress);
                    availableTbsArr = tbsSet.toArray(new TopologyVertex[0]);
                }
                egressList.add(currentEgress);
            }

            ArrayList<Double> runTimesTopoSyncSFC = new ArrayList<>();
            ArrayList<Double> runTimesSt = new ArrayList<>();

            for (int i = 0; i <= MAX_SFC_LEN; i++) {
                CustomDemandBuilder dg = new CustomDemandBuilder();
                for (int j = 0; j < DEMANDS; j++) {
                    dg.setIngress(ingressList.get(j))
                      .setEgress(egressList.get(j))
                      .setDemandValue(4)
                      .setRandomSfc(i)
                      .createDemand();
                }

                List<NprTraffic> demand = dg.generateDemand();

                System.out.println("demand: " + demand.toString());

                NfvPlacementRequest req = new NfvPlacementRequest(graph.getVertexes(), graph.getEdges(), demand, lw);


                SfcPlacementSolver topoSyncSFCSolver = new TopoSyncSFCPlacementSolver(OptimizationGoal.MIN_MAX_DELAYSUM_THEN_DEVIATION, false, env, 1.0);
                NfvPlacementSolution topoSyncSFCSolution = topoSyncSFCSolver.solve(req);
                if (topoSyncSFCSolution == null) {
                    System.out.println("TopoSync-SFC was not feasible, skip");
                    continue;
                }
                System.out.println("TopoSync-SFC was feasible");

                SfcPlacementSolver stSolver = new STSfcPlacementSolver(OptimizationGoal.MIN_MAX_DELAYSUM_THEN_DEVIATION, false, env, 1.0);
                NfvPlacementSolution stSol = stSolver.solve(req);
                if (stSol == null) {
                    System.out.println("ST was not feasible, skip");
                    continue;
                }
                System.out.println("ST was feasible");


                System.out.println(
                        "runtimes: " + (topoSyncSFCSolver.getLastRuntime() + topoSyncSFCSolver.getModelTime()) + "," +
                                (stSolver.getLastRuntime() + stSolver.getModelTime()));

                runTimesTopoSyncSFC.add(topoSyncSFCSolver.getLastRuntime() + topoSyncSFCSolver.getModelTime());
                runTimesSt.add(stSolver.getLastRuntime() + stSolver.getModelTime());

                if (i == 2) {
                    successfulRuns++;
                    System.out.println("all were feasible, writing to file");

                    for (int x = 0; x < runTimesTopoSyncSFC.size(); x++) {
                        runTimePrintWriter.append(String.valueOf(runTimesTopoSyncSFC.get(x)))
                                          .append(",")
                                          .append(String.valueOf(runTimesSt.get(x)))
                                          .append("\n");
                    }
                    runTimePrintWriter.flush();
                }
            }
        }
    }

    /**
     * used for the tradeoff eval experiments
     *
     * @throws IOException
     */
    @Test
    public void tradeoff() throws IOException {
        final int X_START = 16; // initial load constraint
        final int X_END = 3 * 16; // last load constraint
        final int X_STEP = 4;

        TestGraph graph = EvalTopoMockBuilder.getEvalTopo();

        ILinkWeigher lw = new ConstantLinkWeigher(10, 5);

        PrintWriter deviationWriterTopoSyncSFC = new PrintWriter(new FileWriter("tradeoff_deviation_tpl.csv", true));
        PrintWriter loadWriterTopoSyncSFC = new PrintWriter(new FileWriter("tradeoff_load_tpl.csv", true));
        PrintWriter deviationWriterSt = new PrintWriter(new FileWriter("tradeoff_deviation_st.csv", true));
        PrintWriter loadWriterSt = new PrintWriter(new FileWriter("tradeoff_load_st.csv", true));

        for (int x = 0; x < 1000; x++) {
            // choose random ingress
            TopologyVertex ingress = null;
            Set<TopologyVertex> tbsSet = new HashSet<>(graph.getTbs());
            Set<TopologyVertex> dxtSet = new HashSet<>(graph.getDxt());
            TopologyVertex[] availableTbsArr = tbsSet.toArray(new TopologyVertex[0]);
            TopologyVertex[] availableDxtArr = dxtSet.toArray(new TopologyVertex[0]);

            if (ThreadLocalRandom.current().nextInt(100) < 25) {
                // source = DXT
                int index = ThreadLocalRandom.current().nextInt(availableDxtArr.length);
                ingress = availableDxtArr[index];
            } else {
                // source = TBS
                int index = ThreadLocalRandom.current().nextInt(availableTbsArr.length);
                ingress = availableTbsArr[index];
                tbsSet.remove(ingress);
                availableTbsArr = tbsSet.toArray(new TopologyVertex[0]);
            }

            int egressAmount = 3;
            Set<TopologyVertex> egress = new HashSet<>();
            while (egress.size() < egressAmount) {
                int index = ThreadLocalRandom.current().nextInt(availableTbsArr.length);
                TopologyVertex chosenEgress = availableTbsArr[index];
                if (chosenEgress.deviceId().toString().startsWith("tbs")) {
                    egress.add(chosenEgress);
                }
                tbsSet.remove(chosenEgress);
                availableTbsArr = tbsSet.toArray(new TopologyVertex[0]);
            }

            for (int sfcLength = 0; sfcLength <= 2; sfcLength++) {
                // choose random SFC(s)
                NprNfvTypes.Type[] allTypes = NprNfvTypes.Type.values();
                Set<NprNfvTypes.Type> typeSet = new HashSet<>(Arrays.asList(allTypes));
                List<NprNfvTypes.Type> currentSfc = new ArrayList<>();
                for (int i = 0; i < sfcLength; i++) {
                    int index = ThreadLocalRandom.current().nextInt(allTypes.length);
                    NprNfvTypes.Type chosenType = allTypes[index];
                    currentSfc.add(chosenType);
                    typeSet.remove(chosenType);
                    allTypes = typeSet.toArray(new NprNfvTypes.Type[0]);
                }
                List<NprTraffic> traffic = new ArrayList<>();
                traffic.add(new NprTraffic(currentSfc, ingress, egress, 4));
                System.out.println("finished building demand, here it is:");
                System.out.println(traffic.get(0));
                NfvPlacementRequest req = new NfvPlacementRequest(graph.getVertexes(), graph.getEdges(), traffic, lw);

                for (int loadConstraint = X_START; loadConstraint <= X_END; loadConstraint += X_STEP) {
                    boolean topoSyncFeasible = true;
                    boolean stFeasible = true;


                    SfcPlacementSolver topoSyncSFCPlacementSolver = new TopoSyncSFCPlacementSolver(OptimizationGoal.MIN_MAX_DELAYSUM_THEN_DEVIATION, false, env, 1.0, loadConstraint);
                    NfvPlacementSolution topoSyncSFCSolution = topoSyncSFCPlacementSolver.solve(req);
                    if (topoSyncSFCSolution == null) {
                        System.out.println("TopoSync-SFC was not feasible");
                        topoSyncFeasible = false;
                    }

                    SfcPlacementSolver stSolver = new STSfcPlacementSolver(OptimizationGoal.MIN_MAX_DELAYSUM_THEN_DEVIATION, false, env, 1.0, loadConstraint);
                    NfvPlacementSolution stSol = stSolver.solve(req);
                    if (stSol == null) {
                        System.out.println("ST was not feasible");
                        stFeasible = false;
                    }

                    if (topoSyncFeasible) {
                        deviationWriterTopoSyncSFC.append(String.valueOf(topoSyncSFCSolution.getDeviationSum()));
                        loadWriterTopoSyncSFC.append(String.valueOf(topoSyncSFCSolution.getNetworkLoad()));

                        System.out.println(
                                "TopoSync-SFC (load, devi) = (" + topoSyncSFCSolution.getNetworkLoad() + ", " +
                                        topoSyncSFCSolution.getDeviationSum() + ")");
                        System.out.println("TopoSync-SFC runtime: " + topoSyncSFCPlacementSolver.getLastRuntime());
                    } else {
                        deviationWriterTopoSyncSFC.append('i');
                        loadWriterTopoSyncSFC.append('i');
                    }

                    if (loadConstraint != X_END) {
                        deviationWriterTopoSyncSFC.append(',');
                        loadWriterTopoSyncSFC.append(',');
                    }

                    if (stFeasible) {
                        deviationWriterSt.append(String.valueOf(stSol.getDeviationSum()));
                        loadWriterSt.append(String.valueOf(stSol.getNetworkLoad()));

                        System.out.println(
                                "ST  (load, devi) = (" + stSol.getNetworkLoad() + ", " + stSol.getDeviationSum() + ")");
                    } else {
                        deviationWriterSt.append('i');
                        loadWriterSt.append('i');
                    }

                    if (loadConstraint != X_END) {
                        deviationWriterSt.append(',');
                        loadWriterSt.append(',');
                    }
                }

                deviationWriterTopoSyncSFC.append('\n');
                deviationWriterTopoSyncSFC.flush();
                deviationWriterSt.append('\n');
                deviationWriterSt.flush();
                loadWriterTopoSyncSFC.append('\n');
                loadWriterTopoSyncSFC.flush();
                loadWriterSt.append('\n');
                loadWriterSt.flush();
            }
        }
    }

    @After
    public void tearDown() throws GRBException {
        env.dispose();
    }
}
