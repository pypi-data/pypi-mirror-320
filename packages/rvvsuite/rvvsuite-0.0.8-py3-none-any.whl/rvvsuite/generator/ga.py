from random import choice, choices, randint, random
from ..common.supported_features import V_ALL, V_ARITH, V_LOAD, V_STORE

def _init_population(population_size, chromosome_len, gene_pool):
    population = []
    for _ in range(population_size):
        chromosome = choices(gene_pool, k=chromosome_len)
        population.append(chromosome)

    return population


def _evaluate_fitness(chromosome, configs):
    counters = {
        'v_load': 0,
        'v_store': 0,
        'v_arith': 0
    }

    for gene in chromosome:
        if gene in V_ARITH:
            counters['v_arith'] += 1
        elif gene in V_LOAD:
            counters['v_load'] += 1
        elif gene in V_STORE:
            counters['v_store'] += 1

    difference = sum(abs(counters[key] - configs[key]) for key in counters)

    return difference


def _crossover_1_point(parent_1, parent_2):
    p = randint(1, len(parent_1) - 1)
    offspring_1 = parent_1[:p] + parent_2[p:]
    offspring_2 = parent_2[:p] + parent_1[p:]

    return offspring_1, offspring_2


def _let_it_be_mutated(MUTATE_RATE):
    r = random()
    return (r <= MUTATE_RATE)


def _mutate(chromosome, gene_pool):
    mutate_point = randint(0, len(chromosome) - 1)
    while True:
        newGene = choice(gene_pool)
        if newGene != chromosome[mutate_point]:
            chromosome[mutate_point] = newGene
            break

    return chromosome

def run_evolution(configs):
    POPULATION_SIZE = configs['rtg']['population_size']
    CHROMOSOME_LEN = configs['num_of_insts']
    generation_counter = 0
    population = _init_population(
        population_size=POPULATION_SIZE,
        chromosome_len=CHROMOSOME_LEN,
        gene_pool=V_ALL
    )
    
    while (True):
        population.sort(key=lambda chromosome: _evaluate_fitness(chromosome, configs))
        
        if _evaluate_fitness(population[0], configs) == 0:
            break

        new_generation = []

        # Perform Elitism, that mean 10% of fittest population 
        # goes to the next generation 
        s = round((10 * configs['rtg']['population_size'] ) / 100)
        if s < 1: s = 1
        new_generation.extend(population[:s]) 
        
        rest = configs['rtg']['population_size'] - s
        half = round((50 * configs['rtg']['population_size']) / 100) 
        for _ in range(rest): 
            parent_1 = choice(population[:half+1])
            while True:
                parent_2 = choice(population[:half+1])
                if parent_2 != parent_1:
                    break

            offspring_1, offspring_2 = _crossover_1_point(parent_1, parent_2)

            if _let_it_be_mutated(configs['rtg']['mutate_rate']):
                offspring_1 = _mutate(offspring_1, V_ALL)
            if _let_it_be_mutated(configs['rtg']['mutate_rate']):
                offspring_2 = _mutate(offspring_2, V_ALL)
            
            new_generation.append(offspring_1) 
            new_generation.append(offspring_2) 
  
        population = new_generation 
  
        generation_counter += 1

    return population[0], generation_counter
    
