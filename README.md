# Vehicle-Routing-Problem-Public
This program was a past project I completed in part II engineering at the University of Auckland. The program creates four different routes for four different couriers to deliver supplies from the Auckland Airport
to 143 rest homes in Auckland. Each route uses the Auckland City bus network to get to its destinations. This problem is commonly known as the vehicle routing problem. 

Method:

My solution values computation time over route optimality (finding a perfect solution to this problem could take hours of computation). My solution divides the destinations into four geographic groups
with an approximately equal number of destinations in each group. One courier is assigned to each group and an implementation of djikstra's algorithm finds an optimal route for each group. The final solution is provided in ordered lists of destinations visited, and plots showing each route on a map of Auckland.

Typically this program takes ~10 minutes to provide a route for all four couriers.
