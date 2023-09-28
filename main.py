from gurobipy import *

model = Model("optimization")
# Assign initial degradation levels for each asset i and every Wth scenario (There are WxW scenarios in total,
# in this step assign W of them only.).
for j in range(1, Omega + 1, W):
    for i in range(1, M + 1):
        model.addConstr(l_temp[j, i, 0] == degradation[i], name='Initialization (1)_%d,%d' % (j, i))
# Assign initial degradation levels for each asset i and scenarios same as the 1st scenario in their subset (All
# scenarios in a subset will be the same with each other, but different from other subsets, there are W many subsets.)
for j in range(1, Omega + 1, W):
    for i in range(1, M + 1):
        for u in range(W):
            model.addConstr(l[u + j, i, 0] == l_temp[j, i, 0], name='Initialization (2)_%d,%d' % (u + j, i))
# Assign initial degradation levels with observation errors for each asset i and scenario w (There are WxW scenarios
# in total.).
for w in range(1, Omega + 1):
    for i in range(1, M + 1):
        model.addConstr(l_95[w, i, 0] == l[w, i, 0] + gamma[i, 0], name='Initialization (3)_%d,%d' % (w, i))
        for t in range(0, T):
            # Update degradation level for each scenario w, asset i, and time t. Include underlying degradation
            # changes if an inspection was made before. Initialize it if there is a failure or maintenance.
            model.addConstr(l[w, i, t + 1] >= l[w, i, t] + d[w, i, t + 1] + z[i, t]
                            * quicksum(delta[w, i, s] for s in range(1, t + 1))
                            + delta[w, i, t + 1] * quicksum(z[i, s] for s in range(1, t + 1))
                            - bigM_1 * (m[w, i, t + 1] + f[w, i, t + 1]),
                            name='Constraint (2)_%d,%d,%d' % (w, i, t))
            model.addConstr(l[w, i, t + 1] <= l[w, i, t] + d[w, i, t + 1] + z[i, t]
                            * quicksum(delta[w, i, s] for s in range(1, t + 1))
                            + delta[w, i, t + 1] * quicksum(z[i, s] for s in range(1, t + 1))
                            + bigM_1 * (m[w, i, t + 1] + f[w, i, t + 1]),
                            name='Constraint (3)_%d,%d,%d' % (w, i, t))
            # A failure can start if and only if the degradation level of an asset exceeds the threshold.
            model.addConstr(
                0 <= (l[w, i, t] + d[w, i, t + 1] + z[i, t] * quicksum(delta[w, i, s] for s in range(1, t + 1))
                      + delta[w, i, t + 1] * quicksum(z[i, s] for s in range(1, t + 1))) - Lamda
                + bigM_1 * (1 - q[w, i, t + 1]), name='Constraint (NEW)_%d,%d,%d' % (w, i, t))
            # Update degradation level with observation errors for each scenario w, asset i, and time t. Initialize
            # it if there is a failure, maintenance, or inspection.
            model.addConstr(l_95[w, i, t + 1] >= l_95[w, i, t] + gamma[i, t + 1] - bigM_1
                            * (m[w, i, t + 1] + f[w, i, t + 1] + z[i, t + 1]),
                            name='Constraint (6.1)_%d,%d,%d' % (w, i, t))
        for t in range(0, T + 1):
            # Degradation level of an asset i drops to zero if a maintenance or a failure occurs.
            model.addConstr(l[w, i, t] <= bigM_1 * (1 - m[w, i, t] - f[w, i, t]),
                            name='Constraint (4)_%d,%d,%d' % (w, i, t))
            model.addConstr(l[w, i, t] >= -bigM_1 * (1 - m[w, i, t] - f[w, i, t]),
                            name='Constraint (5)_%d,%d,%d' % (w, i, t))
            # Degradation level with observation errors of an asset i drops to zero if a maintenance or a failure occurs.
            model.addConstr(l_95[w, i, t] <= bigM_1 * (1 - m[w, i, t] - f[w, i, t]),
                            name='Constraint (6.2)_%d,%d,%d' % (w, i, t))
            # The lower bound of degradation level with observation errors is the actual degradation level (
            # degradation level without observation errors)
            model.addConstr(l_95[w, i, t] >= l[w, i, t], name='Constraint (7)_%d,%d,%d' % (w, i, t))
            # Find out if the degradation level with observation errors of asset i in scenario w exceeded the failure
            # threshold, so that it can trigger the chance constraint.
            model.addConstr(f_95[w, i] >= (l_95[w, i, t] - Lamda) / bigM_1,
                            name='Constraint (8)_%d,%d,%d' % (w, i, t))
# Chance constraint: limit the number of scenarios in which asset i is allowed fail (degradation level with
# observation errors is allowed to exceed the failure threshold) to a predefined number.
for i in range(1, M + 1):
    model.addConstr(quicksum(f_95[w, i] for w in range(1, Omega + 1)) <= alpha * Omega,
                    name='Constraint (9)_%d' % i)
# The maintenance status of asset i must be the same at time t with any maintenance status in scenario w,
# if the asset has not failed or an inspection was not made until time t.
for w in range(1, Omega + 1):
    for i in range(1, M + 1):
        for t in range(0, T + 1):
            model.addConstr(
                m[w, i, t] >= mu[i, t] - bigM_2 * quicksum(f[w, i, s] + z[i, s] for s in range(1, t + 1)),
                name='Constraint (10)_%d,%d,%d' % (w, i, t))
            model.addConstr(
                m[w, i, t] <= mu[i, t] + bigM_2 * quicksum(f[w, i, s] + z[i, s] for s in range(1, t + 1)),
                name='Constraint (11)_%d,%d,%d' % (w, i, t))
# The maintenance status of asset i must be the same at time t with any maintenance status in scenario w,
# if the asset has not failed or an inspection was not made until time t.
for j in range(1, Omega + 1, W):
    for i in range(1, M + 1):
        for t in range(0, T + 1):
            for u in range(W):
                model.addConstr(m[u + j, i, t] >= m[j, i, t] - bigM_2
                                * (quicksum(f[u + j, i, s] for s in range(1, t + 1))
                                   + (1 - quicksum(z[i, s] for s in range(1, t + 1)))),
                                name='Constraint (12)_%d,%d,%d' % (u + j, i, t))
                model.addConstr(m[u + j, i, t] <= m[j, i, t] + bigM_2
                                * (quicksum(f[u + j, i, s] for s in range(1, t + 1))
                                   + (1 - quicksum(z[i, s] for s in range(1, t + 1)))),
                                name='Constraint (13)_%d,%d,%d' % (u + j, i, t))
# Couple the maintenance status with preventive and corrective maintenance decisions.
for w in range(1, Omega + 1):
    for i in range(1, M + 1):
        for t in range(0, T + 1):
            model.addConstr(m[w, i, t] == quicksum(v[w, i, s] for s in range(max(0, t - Y_p + 1), t + 1))
                            + quicksum(r[w, i, s] for s in range(max(0, t - Y_c + 1), t + 1)),
                            name='Constraint (14)_%d,%d,%d' % (w, i, t))
            # An asset cannot be in failure mode if a failure was not started until time t.
            model.addConstr(f[w, i, t] <= quicksum(q[w, i, s] for s in range(0, t + 1)),
                            name='Constraint (Q)_%d,%d,%d' % (w, i, t))
            # A degradation level must be less than or equal to the failure threshold
            model.addConstr(l[w, i, t] <= Lamda, name='Constraint (15)_%d,%d,%d' % (w, i, t))
            # A crew visit must be scheduled to location k in scenario w, if a maintenance or an inspection is
            # scheduled for asset i in that location.
            model.addConstr(m[w, i, t] <= visit[w, t], name='Constraint (20)_%d,%d,%d' % (w, i, t))
            model.addConstr(z[i, t] <= visit[w, t], name='Constraint (21)_%d,%d,%d' % (w, i, t))
            # If a failure occurs at time t, then a preventive maintenance cannot be started for the asset in that
            # scenario.
            model.addConstr(1 - f[w, i, t] >= v[w, i, t], name='Constraint (16)_%d,%d,%d' % (w, i, t))
            # Each period that the asset is not in failure mode or under maintenance, the asset is available.
            model.addConstr(a[w, i, t] == 1 - f[w, i, t] - m[w, i, t], name='Availability_%d,%d,%d' % (w, i, t))
        # If an asset was in failure status until time t − 1, but not in time t, then a corrective maintenance must
        # be started for the asset in that scenario.
        for t in range(1, T + 1):
            model.addConstr(f[w, i, t - 1] - f[w, i, t] <= r[w, i, t], name='Constraint (17)_%d,%d,%d' % (w, i, t))
# If a visit to location k is not possible during maintenance period t in scenario w, then the maintenance crew
# cannot conduct maintenance, or inspection at that location.
for w in range(1, Omega + 1):
    for t in range(0, T + 1):
        model.addConstr(visit[w, t] <= avail[w, t], name='Constraint (22)_%d,%d' % (w, t))

model.update()

model.modelSense = GRB.MINIMIZE
model.optimize()
model.write('output.lp')
