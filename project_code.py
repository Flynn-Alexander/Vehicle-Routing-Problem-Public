#initial imports
from matplotlib import pyplot as plt
import networkx as nx
import numpy as np

#----------------------------------------------------------------
# SUPPLIED FUNCTIONS
#----------------------------------------------------------------
def read_network(filename):
    """ Reads in a file to a netowrkx.Graph object

    Parameters
    ----------
    filename : str
        Path to the file to read. File should be in graphml format

    Returns
    -------
    network : networkx.Graph
        representation of the file as a graph/network

    """

    network = nx.read_graphml(filename)
    # relabel all integer nodes if possible
    def relabeller(x):
        try:
            return int(x)
        except ValueError:
            return x
    nx.relabel_nodes(network, relabeller, copy=False)
    return network

def get_rest_homes(filename):
    """ Reads in the list of rest home names

    Parameters
    ----------
    filename : str
        Path to the file to read

    Returns
    -------
    rest_homes : list of strings
        list of all rest homes
    """

    rest_homes = []
    with open(filename, 'r') as fp:
        for line in fp:
            rest_homes.append(line.strip())
    return rest_homes

def plot_path(network, path, save=None):
    """ Plots a given path of the Auckland network

    Parameters
    ----------
    network : networkx.Graph
        The graph that contains the node and edge information
    path : list
        A list of node names
    save: str or None
        If a string is provided, then saves the figure to the path given by the string
        If None, then displays the figure to the screen
    """
    lats = [network.nodes[p]['lat'] for p in path]
    lngs = [network.nodes[p]['lng'] for p in path]
    plt.figure(figsize=(8,6))
    ext = [174.48866, 175.001869, -37.09336, -36.69258]
    plt.imshow(plt.imread("akl_zoom.png"), extent=ext)
    plt.plot(lngs, lats, 'r.-')
    if save:
        plt.savefig(save, dpi=300)
    else:
        plt.show()

#----------------------------------------------------------------
#MY FUNCTIONS:
#----------------------------------------------------------------

def nearest_neighbor(network, source_name, destination_names):
    ''' Finds the closest neighboring node to the source node and the distance between the two nodes.
	
		Parameters
		----------
		network : Network
			Network object containing information about nodes and weights.
		source_name : string
			Name of node object where path begins.
        destination_names : List
            List of location names (strings) to be evaluated.
			
		Returns
		-------
		nearest_node : string
			Name of node object closest to the source node.
        min_distance : float
            Time to the nearest node from the source node.
	
		Notes
		-----
		Node objects have weights that represent the time to travel along an edge.
        These weights determine the time to travel between locations.
    '''
    #initial Setup:
    min_distance = float('inf')
    
    #MAIN
    #cycles through all possible destinations and finds the closest one to the source.
    for destination in destination_names:
        distance = nx.shortest_path_length(network, source_name, destination, weight = 'weight')
        if distance < min_distance:
            min_distance = distance
            nearest_node = destination
    
    return nearest_node, min_distance

def path_finder(network, start, locations):
    ''' Determines a short path through a network of locations, going through every 
        location before returning to the start.
	
		Parameters
		----------
		network : Network
			Network object containing information about arcs and nodes.
		start : string
			Name of the starting and ending location of the path.
        locations : List
            List of all locations (strings) to pass through.
			
		Returns
		-------
		final_path : List
			Complete list of ordered network nodes detailing a path through every 
            location before returning to the starting location.
        txt_file_path : List
            List of location names in the order in which they are visited
            along the created path.
        total_distance : float
            Total time to travel along the created path.
	
		Notes
		-----
		Final path contains both strings(location names) and integers (transport node names).
        Finds a pathway by repeating iterations of the nearest neighbour function.
    '''
    #initialise variables
    final_path = []
    txt_file_path = [start]
    total_distance = 0
    check = False

    #MAIN
    #if starting location is on the list of destinations, remove it
    #(only useful if not starting at Auckland Airport)
    source = start
    if start != 'Auckland Airport':
        locations.remove(start)

    #cycle through list until all locations have been visited
    while len(locations) > 0:
        #find and store path to nearest neighboring location 
        nearest_node, path_distance = nearest_neighbor(network, source, locations)
        path = nx.shortest_path(network, source, nearest_node, weight = 'weight')
        final_path += path
        txt_file_path.append(path[-1])
        #keep tally of distance
        total_distance = total_distance + path_distance
        #reset the source location and remove previous source from list
        source = nearest_node
        locations.remove(source)

        #return to starting location
        if len(locations) == 0:
            if check:
                break
            locations.append(start)
            check = True

    return final_path, txt_file_path, total_distance

def location_divider(network, locations_raw):
    ''' Divides the total number of locations to visit into four separate regions/lists.
	
		Parameters
		----------
		network : Network
			Network object containing information about arcs and nodes.
		locations_raw : List
			List of every location name (strings) to be visited by one of the four couriers.
			
		Returns
		-------
		clusters : 2-D Array
			Contains four separate lists of locations (strings) to visit, one for each of the 
            four couriers. 
	
		Notes
		-----
		Each list within clusters may be a different length. (depends on the total number of locations to visit)
    '''
    #initialise variables:
    lat_groups = [[],[]]
    check = False
    indices = [0, 1]
    temp = []
    medians = []
    clusters = [[],[],[],[]]

    #split locations into two groups by median latitude
    for i in range(2):
        for location in locations_raw:
            if check:
                #group locations above lat median, and below lat median.
                if network.nodes[location]['lat'] > medians[0]:
                    lat_groups[0].append(location)
                else:
                    lat_groups[1].append(location)
            else:
                #collect all location latitudes in a list
                temp.append(network.nodes[location]['lat'])
        if not check:
            #find the median latitude
            medians.append(np.median(temp))
            check = True
    temp = []

    #find the median longitude for the locations above median lat, then below median lat
    for index in indices:
        for location in lat_groups[index]:
            temp.append(network.nodes[location]['lng'])
        medians.append(np.median(temp))
        temp = []

    #assign each location to a region/list dependent on location's lat and lng relative to the median lat and lng
    for location in locations_raw:
        if network.nodes[location]['lat'] > medians[0]:
            if network.nodes[location]['lng'] > medians[1]:
                clusters[1].append(location)
            else:
                clusters[0].append(location)
        else:
            if network.nodes[location]['lng'] > medians[2]:
                clusters[3].append(location)
            else:
                clusters[2].append(location)

    return clusters

#----------------------------------------------------------------
#SETUP
#----------------------------------------------------------------

#intial variables
print("Reading the transport network")
auckland = read_network('network.graphml')
locations_raw = get_rest_homes('rest_homes.txt')
filenames_txt = ['path_1.txt','path_2.txt','path_3.txt','path_4.txt']

#set the start location
start = 'Auckland Airport'

#----------------------------------------------------------------
#MAIN
#----------------------------------------------------------------
#Divide locations between four couriers
print("Grouping Destinations")
locations = location_divider(auckland, locations_raw)

#find the pathways for each courier:
print("Finding Route 1")
path1, path1_txt, path_time1 = path_finder(auckland, start, locations[0])
print("Finding Route 2")
path2, path2_txt, path_time2 = path_finder(auckland, start, locations[1])
print("Finding Route 3")
path3, path3_txt, path_time3 = path_finder(auckland, start, locations[2])
print("Finding Route 4")
path4, path4_txt, path_time4 = path_finder(auckland, start, locations[3])
all_paths = [path1, path2, path3, path4]
all_paths_txt = [path1_txt, path2_txt, path3_txt, path4_txt]

#Write paths to separate files and create plots of each courier
print("Saving Files")
for i in range(4):
    fp = open(filenames_txt[i], 'w')
    for j in range(len(all_paths_txt[i])):
        fp.write(all_paths_txt[i][j])
        fp.write('\n')
    fp.close()
    plot_path(auckland, all_paths[i], save = filenames_txt[i][:6])