from itertools import product
import pandas as pd
from mip import Model, xsum, BINARY


############################################################
##### Scenario 1 or 2?
scen = 2
resource_sheet = "surgery_resources{0}".format(scen)
scenario_sheet = "surgery_scen1"

############################################################
resource_constraints = pd.read_excel(
    "rcs_data.xlsx", sheet_name=resource_sheet, engine="openpyxl"
)

scenario = pd.read_excel("rcs_data.xlsx", sheet_name=scenario_sheet, engine="openpyxl")
scenario = scenario.set_index("job_id")

# Number of non-dummy jobs
n = scenario.shape[0] - 2
print("Number of non-dummy jobs:", n, "\n")

# Job duration
p = scenario["estimated_duration"].astype(int).tolist()
p = [int(i) for i in p]
print("Job Duration:", p)
print(len(p), "\n")


# Resource Requirements
u = scenario.iloc[:, 6:].fillna(0).values.astype(int).tolist()
print("Resource Requirements:", u)
print(len(u[0]), len(u), "\n\n")

# Resource Constraints
c = resource_constraints["total_available"].tolist()
print("Resource Constraints", c)
print(len(c), "\n")


# Precedence Constraints
S = []
for i in scenario.index:
    if i != 0:
        preds = str(scenario.loc[i, "precedence"]).split(",")
        for j in preds:
            S.append([int(j), i])
print(S)
print(len(S))


def solve(n, p, u, c, S):
    (R, J, T) = (range(len(c)), range(len(p)), range(sum(p)))
    print(R, J, T)

    model = Model()

    x = [
        [model.add_var(name="x({},{})".format(j, t), var_type=BINARY) for t in T]
        for j in J
    ]

    for j in J:
        model += xsum(x[j][t] for t in T) == 1

    for (r, t) in product(R, T):
        model += (
            xsum(
                u[j][r] * x[j][t2]
                for j in J
                for t2 in range(max(0, t - p[j] + 1), t + 1)
            )
            <= c[r]
        )

    for (j, s) in S:
        model += xsum(t * x[s][t] - t * x[j][t] for t in T) >= p[j]

    ##### Model Objective can be adjusted.
    ##### Total time to complete all jobs are minimized
    # # Minimize wait time of preceding/successive events, and makespan, and start job sooner rather than later
    model.objective = xsum(
        t * (x[s][t] - x[j][t]) + t * x[n + 1][t] / 5 + t / 5 * x[s][t]
        for t in T
        for (j, s) in S
        if j != 0 and s != (n + 1)
    )
    status = model.optimize()
    print(status)
    results = {}
    for (j, t) in product(J, T):
        if x[j][t].x >= 0.99 and j != 0 and j != n + 1:
            results[j] = [t, t + p[j]]
            print("Job {}: begins at t={} and finishes at t={}".format(j, t, t + p[j]))

    return results


results = solve(n, p, u, c, S)
print(results)
print("\n\n")


##### ASSIGN INDIVIDUAL RESOURCE to JOB#####
pool = pd.read_excel("rcs_data.xlsx", sheet_name="resource_pool", engine="openpyxl")

assigned = {}
jobs = scenario.copy()
for r in jobs.index:
    if r != 0 and r != n + 1:
        temp_pool = pool.copy()
        if assigned:
            time_overlapped = []
            for j in assigned.keys():
                timeframe_j = range(results[j][0], results[j][1])
                timeframe_r = range(results[r][0], results[r][1])
                # Overlap, need to disable those resources that have been assigned
                if list(set(timeframe_j) & set(timeframe_r)):
                    for key, val in assigned[j].items():
                        temp_pool.loc[
                            (temp_pool["resource"] == val)
                            & (temp_pool["unique_identification"] == key),
                            "resource",
                        ] = "used"

        a = {}
        for c in jobs.iloc[:, 6:].columns:
            if jobs.loc[r, c] != 0:
                while jobs.loc[r, c] > 0:
                    p = temp_pool.loc[
                        temp_pool["resource"] == c, "unique_identification"
                    ].tolist()[0]
                    temp_pool.loc[
                        (temp_pool["resource"] == c)
                        & (temp_pool["unique_identification"] == p),
                        "resource",
                    ] = "used"
                    jobs.loc[r, c] -= 1
                    a[p] = c
        assigned[r] = a
for k, v in assigned.items():
    print(k, v, "\n")
