# Pseudocode for Class Route
from typing import List

from instances.Trucks import Vehicle


class RouteObject:
    def __init__(self, customer_list: list, vehicle: Vehicle):
        self.customer_list: list = customer_list
        self.vehicle: Vehicle = vehicle
        self.currently_feasible: bool = False
        self.current_cost: float = 0
        # list customer_list = [0,0] # the list of customers (+depots)
        # Vehicle vehicle = "" # each route should know the vehicle object assigned to it. not just the vehicle type, but the vehicles unique ID / numberplate
        # boolean currently_feasible = false # each route should know if it is currently feasible. Everytime the route_cost is updated, we should also be told if the route is feasible (penalty_cost = 0)
        # int current_cost = 0 # whenever we update the route_cost, we should store it in the route. We will often compare against the cost of the unchanged route (e.g. for insert-operations), so it makes sense to have it stored
