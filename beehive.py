import random
from config import NB_BEES, BEEHIVE_POSITION, MUTATION_RATE
import copy
import math

class Bee:

    def __init__ (self, path, beehive_position=BEEHIVE_POSITION):
        self.path = path
        self.beehive_position = beehive_position
        self.path_length = self.compute_path_length(path)

    def compute_segment(self, bee_path):
        return math.sqrt((bee_path[1][0] - bee_path[0][0]) ** 2 + (bee_path[1][1] - bee_path[0][1]) ** 2)

    def compute_path_length(self, path):
        """
        Beehhive - A - B - ... - Z - Beehive
                    ( path )
        We want the perimeter of a polygon with n + 1 sides, n being the number of flowers, and the last side being the distance from the last flower to the beehive.            
        """
        length = 0
        length += self.compute_segment([self.beehive_position, path[0]]) # distance from beehive to first flower
        length += self.compute_segment([path[-1], self.beehive_position]) # distance from last flower to beehive
        for i in range(len(path) - 1): #i de 0 à 49
            length += self.compute_segment([path[i], path[i + 1]])
        return length

        
class Beehive:
    def __init__(self, flowers, beehive_position=BEEHIVE_POSITION):
        self.flowers = flowers
        self.bees = []
        self.beehive_position = beehive_position

    def init_bee(self):
        path = copy.copy(self.flowers)
        random.shuffle(path)
        return path

    def init_bees(self):
        for i in range(NB_BEES):
            path = self.init_bee()
            bee = Bee(path, self.beehive_position)
            self.bees.append(bee)

    def next_generation(self):
        self.bees.sort(key=lambda x: x.path_length)  # Sort bees by path
        queen = self.bees[0]
        self.bees = self.bees[:len(self.bees) // 2]  # Keep only the best bees
        parents = copy.copy(self.bees)  # Copy the best bees to use as parents 
        # Create new bees for the next generation
        while len(self.bees) < NB_BEES:
            parent1, parent2 = random.sample(parents, 2)
            child_bee = self.crossover(parent1, parent2)
            if random.random() < MUTATION_RATE:  # Mutation probability
                child_bee = self.mutate(child_bee)
            self.bees.append(child_bee)
        self.bees[-1] = queen  # Ensure the queen bee is always in the population

    def get_average_distance(self):
        total_distance = sum(bee.path_length for bee in self.bees)
        average_distance = total_distance / len(self.bees)
        return average_distance

    def crossover(self, parent1, parent2):
        # Create a child path by combining parts of both parents
        child_path = []
        start = random.randint(0, len(parent1.path) - 1)
        # End index should be greater than start index to ensure a valid slice so en starts at least at start and can go up to the last index of parent1.path
        end = random.randint(start, len(parent1.path) - 1)

        # Add a slice from parent1
        # +1 to include the end index in the slice because in Python [a:b] does not include b
        child_path.extend(parent1.path[start:end + 1])

        # Add remaining flowers from parent2 in order
        for flower in parent2.path:
            if flower not in child_path:
                child_path.append(flower)

        return Bee(child_path, self.beehive_position)
        
    def mutate(self, bee):
        # randomly choose 2 hints in the path and swap them with flowers in bee.path then recalculate the path length
        path = copy.copy(bee.path)
        idx1, idx2 = random.sample(range(len(path)), 2)
        path[idx1], path[idx2] = path[idx2], path[idx1]
        return Bee(path, self.beehive_position)
    