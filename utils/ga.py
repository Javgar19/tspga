import random 
import math
from haversine import haversine


class Individual:
    """
    Simple class representing an individual in the genetic algorithm context. The genotype is a list 
    containing the order of the locations in the path.
    """
    def __init__(self, genotype: list):
        self.genotype = genotype
        self.fitness = 0


class GASetup:
    """ 
    Class that implements the the basic methods for genetic algorithms: the fitness function of the problem and
    the breeding and mutation methods.
    """
    def __init__(self, locations: list, pop_size: int, mut_rate: float):
        self.locations = locations
        self.chrom_size = len(locations) - 1
        self.pop_size = pop_size
        self.mut_rate = mut_rate

    def fitness_function(self, ind: Individual):
        """
        Returns the fitness of an individual. It is computed as the sum of distances between the cities in the order
        stablished by the chromosome. The first location is added to the chain in the beginning and end of the chromosome
        
        Haversine function has been used to estimate the distance between two points given their angular coordinates
        """

        # Distance between the initial point and the first location in the chromosome
        fitness = haversine((self.locations[0]["lat"], self.locations[0]["lng"]),
                            (self.locations[ind.genotype[0]]["lat"], self.locations[ind.genotype[0]]["lng"]))
        
        # Distance between each location in the chromosome
        for i in range(0, self.chrom_size - 1): 
            fitness += haversine((self.locations[ind.genotype[i]]["lat"], self.locations[ind.genotype[i]]["lng"]),
                                 (self.locations[ind.genotype[i+1]]["lat"], self.locations[ind.genotype[i+1]]["lng"]))

        # Distance between the last location in the chromosome and the initial point 
        fitness += haversine((self.locations[ind.genotype[self.chrom_size-1]]["lat"], self.locations[ind.genotype[self.chrom_size-1]]["lng"]),
                            (self.locations[0]["lat"], self.locations[0]["lng"]))
        
        return 1/fitness

    def breed(self, parent1: Individual, parent2: Individual) -> Individual:
        """
        Produce an offspring from the order crossover of two individuals
        """
        # Crossover points
        gene1 = int(random.random() * self.chrom_size)
        gene2 = int(random.random() * self.chrom_size)
        start_gen = min(gene1, gene2)
        end_gen = max(gene1, gene2)

        child_genotype = [0] * self.chrom_size
        for i in range(start_gen, end_gen+1):
            child_genotype[i] = parent1.genotype[i]

        i_child = 0
        i_parent = 0
        while i_child < self.chrom_size:
            # Check if we are adding a city in the already filled part of the offspring
            if i_child in range(start_gen, end_gen + 1):
                i_child += 1
                continue

            city = parent2.genotype[i_parent]
            if city not in child_genotype:
                child_genotype[i_child] = city
                i_child += 1
                
            i_parent += 1    

        return Individual(child_genotype)


    def mutate(self, ind: Individual):
        """
        Mutate an individual by swapping two cities in the chromosome
        """
        # Check if the individual is being mutated
        if random.random() > self.mut_rate:
            return
        
        # Select genes to swap at random
        first_gene = random.randint(0, self.chrom_size-1)
        second_gene = random.randint(0, self.chrom_size-1)
        while second_gene == first_gene:
            second_gene = random.randint(0, self.chrom_size-1)

        # Swap the genes
        aux = ind.genotype[first_gene]
        ind.genotype[first_gene] = ind.genotype[second_gene]
        ind.genotype[second_gene] = aux


        
class GA(GASetup):
    def __init__(self, locations: list, pop_size: int, mut_rate: float, elitism_rate: float):
        super().__init__(locations, pop_size, mut_rate)
        self.elitism_rate = elitism_rate
        self.population = []

    def random_population(self):
        """ 
        Generate a population of random individuals
        """
        base_chromosome = list(range(1, len(self.locations)))
        for _ in range(self.pop_size):
            # Create a random permutation of locations
            random_chromosome = random.sample(range(1, self.chrom_size + 1), k=self.chrom_size)

            # Create the random individual, compute its fitness and store it in the population list
            random_individual = Individual(random_chromosome)
            random_individual.fitness = super().fitness_function(random_individual)
            self.population.append(random_individual)

    def roulette_selection(self, fitness_list):
        """ 
        Choose a random individual from the population with a probability proportional to its fitness
        """
        return random.choices(self.population, weights=fitness_list, k=1)[0]
    
    def next_generation(self):
        """ 
        Method that produces the next generation of the population. It performs the selection of the fitest
        individuals, their breeding and the mutation of the offspring
        """
        # Order the population by fitness
        self.population = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        fitness_list = [ind.fitness for ind in self.population]

        next_population = []

        # Elitist conservation of the best individuals
        for ind in self.population[:self.elitism_rate]:
            next_population.append(ind)

        while len(next_population) < self.pop_size:
            # Selection of the parents
            parent1 = self.roulette_selection(fitness_list)
            parent2 = self.roulette_selection(fitness_list)
            
            # Crossover of the parents
            offspring = super().breed(parent1, parent2)

            # Mutation of the offsprings
            super().mutate(offspring)

            # Compute offspring fitness
            offspring.fitness = super().fitness_function(offspring)
            
            next_population.append(offspring)
            

        # Substitute the population with the new generation
        self.population = next_population

    def get_best_individual(self):
        return max(self.population, key = lambda ind: ind.fitness)
    
    def run_ga(self, termination_criteria):
        """ 
        Run the Genetic Algorithm with a certain termination criteria: the amount of generation in a row
        with no change in the best fitness that we allow the algorithm to run

            return: the genotype of the best individual and the inverse of it fitness i.e. the total distance
        """
        if self.chrom_size < 3:
            return (list(range(1, self.chrom_size + 1)), 
                    1/super().fitness_function(Individual(list(range(1, self.chrom_size + 1)))))
        
        # Generate the initial random population
        self.random_population()

        best_individual = self.get_best_individual()
        termination_counter = 0

        while termination_counter < termination_criteria:
            self.next_generation()
            new_best_individual = self.get_best_individual()

            # If the best individual hasn't changed, add one to the termination counter
            if new_best_individual.genotype == best_individual.genotype:
                termination_counter += 1
            else:
                best_individual = new_best_individual
                termination_counter = 0

        return (best_individual.genotype, 1/best_individual.fitness)




    
        



