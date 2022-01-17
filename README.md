# AS_STS_code

# HOW TO CHANGE AROUND PARAMETERS

1. Global Stuff

1.0 TestDimension: How many customers you want to use. -> main.py
Decide if you want to run with 19, 39 or 112 (all) customers. The code will then pick the correct dataset. Only these
3 options are currently supported. Gene can add more :)
    testDimension = 1 + **x**

1.1 maxIterations: For how many iteration the code can run. -> instance
Can be set in instance, in the **max_iterations** variable. I use 30-100 for testing & 1000 to get a serious solution.
Mostly depends on the run time tho, so if everything else is set up to run very fast, use way more iterations.  
1.1.2 penalty_cost_iteration_for_initialization: Which iteration the initial solution should use to get its penalty costs. -> instance
penalty_cost_iteration_for_initialization sets the iteration that gives us the penalty cost for deciding if it is cheaper to add a 
new route or to add to the last open route.
If this is chosen too high will only create feasible routes (if possible) and tends to overload the last vehicle available.
Setting it too low only creates infeasible routes and tends to overload the first routes.
A good idea seems to be to set it to 75% of maxIteration
    self.penalty_cost_iteration_for_initialization = 0.75 * self.max_iterations  # setting this parameter correctly is very important for the initial solution.

1.2 max_time: for how long the code should run max. -> instance
Since we want to optimize for speed, and we need to compare with the speed of the ExcelSolver, we can now set a maxTime.
This is useful to compare the speed of different parameter settings. The loop will stop after either maxTime or maxIterations
are reached, so if you want only 1, set the other very high.
    max_time = **120.0**  # sets how much time the loop should maximally use

1.3 AvailableVehicles: How many vehicles we have available. -> main.py
Can be set in main in "# 3. CREATING OUR VEHICLES".
    num_Atego = **20**
    num_VWTrans = **20**
    num_eCargoBike = **0**

1.4 Penalties
1.4.1 penalty_cost: How much cost an overload creates. -> instance
We have to decide how we want to scale the penalty_cost with growing iterations. We could do linear growth / exponential
growth etc. Additionally, the overload for the "iteration 0" can be set. It should probably not be 0, or we will put
bikes everywhere...
The cost needs to be in relation to the general cost a route creates, so it will change once we add time_cost and
fixed_costs. Also, it should probably depend on maxIterations, since it should grow slower if we run 1.000 iterations
compared to just 100 iterations. A good way to check is to see if the vehicle assignments are all feasible at the end.
If not, we need more penalty!
    penalty_cost(routeObject: RouteObject, instance: Instance, iteration: int) -> float:
        iteration_penalty = **init_penalty** + iteration * **step_penalty**  # penalty in each iteration.
1.4.2 overload_factors: How hard we punish going over a capacity limit. -> Utils.py
Check the compute_overload function in utils to see the exact function. We can for example set it so further deviations
are punished much harder by squaring the overload_factor.
    compute_overload(constraint: int, load: int) -> float:
        # Overload factor can be changed to our will. Probably should get smthing from literature
        **overload_factor** = (max(load - constraint, 0) / constraint)# ** 2  # we normalize the factor by the constraint (to not punish more because values are higher), then we square to punish bigger overloads much more



2. Adaptive Weights -> Construction.py

Adaptive weights decide how often an operation is picked. Operations are the rules used to destroy customers,
insert customer and optimize a solution. These weights need to be chosen in a smart way, because they dictate how fast
the code runs (some operations need more computation time) vs how many iterations we need to find a good solution
(some operations only do random stuff, some operations are pretty smart). The tradeoff is how many iterations we need vs
how much time an iteration needs on average.
Also, different operations can be better or worse depending on how long the algorithm has lasted. In theory, random 
stuff should happen at the start, smart stuff should happen near the end. In practice, I have seen that sometimes near the 
end only a very random operator can find a better solution, because  we are in a deep local minimum.
You can set the initial weights of each operator at the top of ourAlgorithm, before the loop start:
    weight_destroy_random = **50**
    weight_destroy_expensive = **50**
Set the initial weight to 0 to completely turn off an operator.
A formula is set up to pick an operator from a weighted list, so if we add a 3rd operator with for example weight = 100,
it would be chosen 50% of the time compared to destroy_random (25%) and destroy_expensive (25%).
    insert_op_used_list = random.choices(insert_ops, weights=insert_weights) # chooses an option from a weighed list
You can also change how much a weight is changed after an iteration. After the acceptance check, we either:
A) increase the weight if an operator was used in a successful iteration:
        if costThisIteration < bestCost:
            if destroy_op_used == 'random_removal':
                    weight_destroy_random = min(**200**, weight_destroy_random + **iteration**)
b) decrease the weight if the iteration was unsuccessful:
        else:
            if destroy_op_used == 'random_removal':  # pick a destroy operation
                weight_destroy_random = max(**10**, weight_destroy_random - **1**)
I have set it up that these weights can only be 10 < weight < 200. Also, since we don't find improvements very often,
we get more weight for each success than we take away for every fail.
And because it is much harder to find an improvement in a later iteration, we give +iteration (but never more than 200).
You can change all of this, I have not tested it much. There are very fancy ways to compute the weight changes in
literature, like having the change depend on HOW MUCH better/worse the new solution is. Maybe we can implement this later.


3. Inside Destruction 

3.1 numberOfRemoved lower-bound/upper-bound -> DestructionOps.py
In random_removal and expensive_removal we get a numberOfRemoved. This number is random in each iteration. We can
set the upper and lower bound inside the functions. All functions have their separate bounds. Higher bounds will
mean we remove more customers each iteration, which leads to more exploration (chaos).
In the example below the lower bound is 10% of all customers are removed, the upper bound is 50% of all customers.
Testing has shown that 50% is much too chaotic for our algorithm.
    numberOfRemoved = random.randint(round(**0.1** * (len(instance.q) - 1)), round(**0.5** * (len(instance.q) - 1)))