package org.onosproject.nfv.placement.solver;

public enum OptimizationGoal {
    /**
     * load reduction goal. minimize absolute link utilization
     */
    LOAD_REDUCTION,
    /**
     * minimize delay by minimizing sum_{t in T} sum_{d in D} delay(d)
     */
    DELAY_REDUCTION_PER_DST_SUM,
    /**
     * with sum of maxDelay-minDelay as lower-prioritized objective
     */
    DELAY_REDUCTION_PER_DST_SUM_MULTI,
    /**
     * multi-objective:
     * 1.minimize sum of max deviations per flow
     * 2.minimize sum of delay deviations
     */
    MIN_MAX_DELAYSUM_THEN_DEVIATION,
    /**
     * shortest path tree (shortest delay tree)
     */
    SPT
}
