# AS_STS_code

# HOW TO CHANGE AROUND PARAMETERS

1. Global Stuff

1.0 TestDimension: How many customers you want to use. -> main.py
Decide if you want to run with 19, 39 or 112 (all) customers. The code will then pick the correct dataset. Only these
3 options are currently supported. Gene can add more :)
    testDimension = 1 + **x**

1.1 maxIterations: For how many iteration the code can run. -> main.py
Can be set in main.py, in the **maxIterations** variable. I use 30-100 for testing & 1000 to get a serious solution.
Mostly depends on the run time tho, so if everything else is set up to run very fast, 
1.1.2 penalty_cost_dummy_iteration: Which iteration the initial solution should use to get its penalty costs. -> utils.py
penalty_cost_dummy_iteration sets the iteration that gives us the penalty cost for deciding if it is cheaper to add a 
new route or to add to the last open route.
If this is chosen too high will only create feasible routes (if possible) and tends to overload the last vehicle available.
Setting it too low only creates infeasible routes.
A good idea seems to be to set it to 75% of maxIteration
    penalty_cost_dummy_iteration = **75**  # setting this parameter correctly is very important for the initial solution.

1.2 AvailableVehicles: How many vehicles we have available. -> main.py
Can be set in main in "# 3. CREATING OUR VEHICLES".
    num_Atego = **20**
    num_VWTrans = **20**
    num_eCargoBike = **0**

1.3 Penalties
1.3.1 penalty_cost: How much cost an overload creates. -> Utils.py 
We have to decide how we want to scale the penalty_cost with growing iterations. We could do linear growth / exponential
growth etc. Additionally, the overload for the "iteration 0" can be set. It should probably not be 0, or we will put
bikes everywhere...
The cost needs to be in relation to the general cost a route creates, so it will change once we add time_cost and
fixed_costs. Also, it should probably depend on maxIterations, since it should grow slower if we run 1.000 iterations
compared to just 100 iterations. A good way to check is to see if the vehicle assignments are all feasible at the end.
If not, we need more penalty!
    penalty_cost(routeObject: RouteObject, instance: Instance, iteration: int) -> float:
        iteration_penalty = **5** + iteration * **1**  # penalty in each iteration.
1.3.2 overload_factors: How hard we punish going over a capacity limit. -> Utils.py
Check the compute_overload function in utils to see the exact function. We can for example set it so further deviations
are punished much harder by squaring the overload_factor.
    compute_overload(constraint: int, load: int) -> float:
        # Overload factor can be changed to our will. Probably should get smthing from literature
        **overload_factor** = (max(load - constraint, 0) / constraint)# ** 2  # we normalize the factor by the constraint (to not punish more because values are higher), then we square to punish bigger overloads much more



2. Adaptive Weights

2.1 Destruction: To choose how often which destruction operation should be chosen. -> Construction.py
Change the right side of the equation to pick random_removal more often (higher right side).
        if random.uniform(0, 1) >= **0.1**:  # pick a destroy operation
            # Random Removal Operation
            listOfRemoved = random_removal(instance)
            destroy_op_used = "random_removal"
        else:
            # Expensive Removal Operation
            listOfRemoved = expensive_removal(listOfRoutes, instance, iteration)
            destroy_op_used = "expensive_removal"

2.2 Insertion: To choose how often which insert operation should be chosen. -> Construction.py
Change the right side of the equation to pick cheapest_insertion more often (higher right side).
        if random.uniform(0, 1) >= **0.5**:  # pick a destroy operation
            # cheapest insertion with new  after 1 customer is assigned
            cheapest_insertion_iterative(listOfRoutes, listOfRemoved, list_of_available_vehicles, instance, iteration)
        else:
            # regret insertion
            regret_insertion(listOfRoutes, listOfRemoved, list_of_available_vehicles, instance, iteration)

2.3 Optimization: Not yet implemented



3. Inside Destruction 

3.1 numberOfRemoved lower-bound/upper-bound -> DestructionOps.py
In random_removal and expensive_removal we get a numberOfRemoved. This number is random in each iteration. We can
set the upper and lower bound inside the functions. All functions have their separate bounds. Higher bounds will
mean we remove more customers each iteration, which leads to more exploration (chaos).
In the example below the lower bound is 10% of all customers are removed, the upper bound is 50% of all customers.
Testing has shown that 50% is much too chaotic for our algorithm.
    numberOfRemoved = random.randint(round(**0.1** * (len(instance.q) - 1)), round(**0.5** * (len(instance.q) - 1)))



