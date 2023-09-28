# PROMISE

**PROMISE** is an optimization package for the inspection and maintenance scheduling of marine energy systems, a fundamental optimization problem in marine energy systems used. The package provides a five-year significant wave height data together with low and medium accessibility cases for the problem and Python implementations of state-of-the-art stochastic mixed-integer programming formulation using Gurobi.


## Sample Usage

```python
# Import Gurobi optimization package
from gurobipy import *

# Construct model
model = Model("optimization")

# Initialize variables
for j in range(1, Omega + 1, W):
    for i in range(1, M + 1):
        model.addConstr(l_temp[j, i, 0] == degradation[i], name='Initialization (1)_%d,%d' % (j, i))
...

# Update the model - Couple the maintenance status with preventive and corrective maintenance decisions.
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

...

model.update()

model.modelSense = GRB.MINIMIZE
model.optimize()
model.write('output.lp')
```

## Authors
* **Muhammet Ceyhan Sahin** (Wayne State University)
* **Deniz Altinpulluk** (Wayne State University)
* **Shijia Zhao** (Argonne National Laboratory)
* **Murat Yildirim** (Wayne State University)
* **Feng Qiu** (Argonne National Laboratory)

## Acknowledgments

* This material is based upon work supported by the U.S. Department of Energy, Office of Energy Efficiency and Renewable Energy (EERE), specifically the **Water Power Technology Office (WPTO)**, under seedling project "Prognostics Driven Operations, Maintenance and Inspection for a Sustainable Energy Infrastructure (PROMISE): Developing Maintenance Decision Models for Marine Energy". 

## Citing

If you use PROMISE in your research (instances, models or algorithms), we kindly request that you cite the package as follows:

* Muhammet Ceyhan Sahin, Deniz Altinpulluk, Shijia Zhao, Feng Qiu, and Murat Yildirim. author, “A degradation embedded stochastic optimization framework for inspection and maintenance in marine energy systems”, submitted to IEEE Transactions on Power Systems, 2023


## License

```text
PROMISE: A Python optimization package for the inspection and maintenance scheduling of marine energy systems.
Copyright © 2023-2023, UChicago Argonne, LLC. All Rights Reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of
   conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of
   conditions and the following disclaimer in the documentation and/or other materials provided
   with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to
   endorse or promote products derived from this software without specific prior written
   permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```
