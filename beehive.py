import random
from config import NB_BEES, BEEHIVE_POSITION, MUTATION_RATE, SELECTION_RATE
import copy
import math
import networkx as nx

class Bee:

    def __init__ (self, path, beehive_position=BEEHIVE_POSITION, bee_id=None, parent1=None, parent2=None):
        self.path = path
        self.beehive_position = beehive_position
        self.path_length = self.compute_path_length(path)
        self.bee_id = bee_id
        self.parent1 = parent1
        self.parent2 = parent2
        
    def compute_segment(self, bee_path):
        return math.sqrt((bee_path[1][0] - bee_path[0][0]) ** 2 + (bee_path[1][1] - bee_path[0][1]) ** 2)

    def compute_path_length(self, path):
        """
        Beehive - A - B - ... - Z - Beehive
                    ( path )
        We want the perimeter of a polygon with n + 1 sides, n being the number of flowers, and the last side being the distance from the last flower to the beehive.            
        """
        length = 0
        length += self.compute_segment([self.beehive_position, path[0]]) # distance from beehive to first flower
        length += self.compute_segment([path[-1], self.beehive_position]) # distance from last flower to beehive
        for i in range(len(path) - 1): 
            length += self.compute_segment([path[i], path[i + 1]])
        return length

        
class Beehive:
    def __init__(self, flowers, beehive_position=BEEHIVE_POSITION, mutation_rate=MUTATION_RATE, selection_rate=SELECTION_RATE, all_bees=None):
        self.flowers = flowers
        self.bees = []
        self.beehive_position = beehive_position
        self.mutation_rate = mutation_rate
        self.selection_rate = selection_rate
        if all_bees is None:
            self.all_bees = {}
        else:
            self.all_bees = all_bees
        self.next_id = 0

    def init_bee(self):
        path = copy.copy(self.flowers)
        random.shuffle(path)
        return path

    def init_bees(self):
        for i in range(NB_BEES):
            path = self.init_bee()
            self.next_id += 1
            bee = Bee(path, self.beehive_position, bee_id=self.next_id)
            self.bees.append(bee)
            self.all_bees[bee.bee_id] = bee

    def next_generation(self):
        self.bees.sort(key=lambda x: x.path_length)  # Sort bees by path
        # The best bee is kept inside the parent pool below, so elitism is implicit.
        n_parents = max(2, int(len(self.bees) * self.selection_rate))  # Select top bees as parents
        self.bees = self.bees[:n_parents]  # Keep only the best bees
        parents = copy.copy(self.bees)  # Copy the best bees to use as parents 
        # Create new bees for the next generation
        while len(self.bees) < NB_BEES:
            parent1, parent2 = random.sample(parents, 2)
            child_bee = self.crossover(parent1, parent2)
            if random.random() < self.mutation_rate:  # Mutation probability
                child_bee = self.mutate(child_bee)
            self.all_bees[child_bee.bee_id] = child_bee
            self.bees.append(child_bee)

    def get_average_distance(self):
        total_distance = sum(bee.path_length for bee in self.bees)
        average_distance = total_distance / len(self.bees)
        return average_distance

    def crossover(self, parent1, parent2):
        # Create a child path by combining parts of both parents
        child_path = []
        # Increment global id for the new bee
        self.next_id += 1
        # Randomly select a start and end index for the slice from parent1
        start = random.randint(0, len(parent1.path) - 1)
        # End index should be greater than start index to ensure a valid slice so en starts at least at start and can go up to the last index of parent1.path
        end = random.randint(start, len(parent1.path) - 1)

        # Add a slice from parent1
        # +1 to include the end index in the slice because in Python [a:b] does not include b
        child_path.extend(parent1.path[start:end + 1])
        used = set(child_path)  # Keep track of flowers already in the child path
        # Add remaining flowers from parent2 in order
        for flower in parent2.path:
            if flower not in used:
                child_path.append(flower)
                used.add(flower)

        return Bee(child_path, self.beehive_position, bee_id=self.next_id, parent1=parent1.bee_id, parent2=parent2.bee_id)
        
    def mutate(self, bee):
        # randomly choose 2 hints in the path and swap them with flowers in bee.path then recalculate the path length
        path = copy.copy(bee.path)
        idx1, idx2 = random.sample(range(len(path)), 2)
        path[idx1], path[idx2] = path[idx2], path[idx1]
        return Bee(path, self.beehive_position, bee_id=bee.bee_id, parent1=bee.parent1, parent2=bee.parent2)

    def get_best_bee(self):
        # min() instead of sorting self.bees in place: no side effect on the population
        return min(self.bees, key=lambda bee: bee.path_length)

    def add_to_tree(self, G, bee, max_depth, best_depth):
        """Add bee and its ancestors to G, up to max_depth generations back.

        best_depth maps a bee id to the largest remaining depth it was reached with.
        The ancestry is a DAG (a bee can be a parent in several couples), so a bee
        first seen with little depth left must still be expanded when reached again
        with more depth left, otherwise whole branches are silently dropped.
        """
        if bee is None:
            return
        # Skip only if this bee was already expanded with at least as much depth left.
        if best_depth.get(bee.bee_id, -1) >= max_depth:
            return
        best_depth[bee.bee_id] = max_depth
        G.add_node(bee.bee_id, path_length=bee.path_length)
        if max_depth == 0:
            return
        for parent_id in (bee.parent1, bee.parent2):
            if parent_id is not None:
                # The recursive call adds the parent as a node right after.
                G.add_edge(parent_id, bee.bee_id)
                self.add_to_tree(G, self.all_bees[parent_id], max_depth - 1, best_depth)

    def get_genealogy_tree (self, root_bee, max_depth):
        G = nx.DiGraph()
        self.add_to_tree(G, root_bee, max_depth, {})
        return G