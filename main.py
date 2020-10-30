from math import sqrt
import random

NEW_INDIVIDUALS_PERCENTAGE = 10
MUTATION_PERCENTAGE = 30
CROSSOVER_PERCENTAGE = 50

NUMBER_OF_TOWNS = 10
NUMBER_OF_INDIVIDUALS = 1000
NUMBER_OF_GENERATIONS = 200


# nacita mapu zo suboru v tvare {i: [x, y], ...}
def load_map(p_matrix: [], p_filename: ""):
    global NUMBER_OF_TOWNS
    loaded_file = open(p_filename, "r").read().split('\n')
    towns = []
    for i in range(0, len(loaded_file)):
        towns.append([int(coor) for coor in loaded_file[i].split(' ')])

    for i in range(0, len(towns)):
        p_matrix.append([])
        for j in range(0, len(towns)):
            if i == j:
                p_matrix[i].append(0)
            else:
                p_matrix[i].append(euclid_distance(towns[i], towns[j]))

    NUMBER_OF_TOWNS= len(loaded_file)


# vrati euklidovnsku vzdialenost dvoch bodov
def euclid_distance(first: [], second: []) -> float:
    return sqrt(abs(first[0] - second[0]) ** 2 + abs(first[1] - second[1]) ** 2)


# vygeneruje sekvenciu navstivenych miest - cestu
def generate_random_chromosome() -> list:
    generated_array = []
    for i in range(0, NUMBER_OF_TOWNS):
        generated_array.append([random.random(), i + 1])
    return list(x[1] for x in sorted(generated_array))


# vykona crossover chromozomov
def do_crossover(first_parent: [], second_parent: []) -> list:
    seq = []
    new_chromosome = []

    # zvoli nahodnu dlzku vymeneneho retazca
    len_change = int(random.random() * NUMBER_OF_TOWNS) % (NUMBER_OF_TOWNS - 2) + 2
    # zvoli nahodny zaciatok
    start_index = int(random.random() * NUMBER_OF_TOWNS) % (NUMBER_OF_TOWNS - len_change + 1)

    # vytvorti prazdny chromozom
    for i in range(0, NUMBER_OF_TOWNS):
        new_chromosome.append(0)

    # vlozi sekvenciu z prveho rodica do potomka
    for i in range(start_index, start_index + len_change):
        new_chromosome[i] = first_parent[i]
        seq.append(first_parent[i])

    # vlozi ostatne mesta z druheho rodica do potomka v poradi, v akom boli v druhom rodicovi
    j = 0
    for i in range(0, len(new_chromosome)):
        if new_chromosome[i] != 0:
            continue
        while second_parent[j] in seq:
            j += 1
        new_chromosome[i] = second_parent[j]
        j += 1

    return new_chromosome


# vykona mutaciu dvoch miest vedla seba na jednom chromozome
def do_simple_mutation(chromosome: []) -> list:
    index = int(random.random() * NUMBER_OF_TOWNS) % (NUMBER_OF_TOWNS - 1)
    temp = chromosome[index]
    chromosome[index] = chromosome[index + 1]
    chromosome[index + 1] = temp
    return chromosome


# vykona mutaciu, a to zrotuje sekvenciu miest medzi dvoma mestami na jednom chromozome
def do_difficult_mutation(chromosome: []) -> list:
    reversed_seq = []
    # zvoli nahodnu dlzku retazca, ktory bude obrateny (od 2 po NUMBER_OF_TOWNS-1)
    len_change = int(random() * NUMBER_OF_TOWNS) % (NUMBER_OF_TOWNS - 2) + 2
    # zvoli nahodny zaciatok
    start_index = int(random() * NUMBER_OF_TOWNS) % (NUMBER_OF_TOWNS - len_change + 1)

    for i in range(start_index, start_index + len_change):
        reversed_seq.insert(0, chromosome[i])

    for i in range(start_index, start_index + len_change):
        chromosome[i] = reversed_seq[i - start_index]

    return chromosome


# vyrata fitness pre jeden chromozom
def fitness(chromosome: [], map: []) -> float:
    sum = 0
    for i in range(0, NUMBER_OF_TOWNS - 1):
        sum += map[chromosome[i]-1][chromosome[i + 1]-1]

    sum += map[chromosome[NUMBER_OF_TOWNS-1]-1][chromosome[0]-1]
    return 1/sum


# vytvori nahodnu generaciu, pouzite pri nultej generacii
def create_new_random_generation(generation: [], map: {}):
    for i in range(0, NUMBER_OF_INDIVIDUALS):
        temp = generate_random_chromosome()
        generation.append([fitness(temp, map), temp])


# vytvori novu generaciu pouzitim noych jedincov, mutacie alebo crossover
def create_next_generation_allrandom(generation: [], map: {}):
    generation = sorted(generation, reverse=True)
    new_generation = []
    for i in range(0, NUMBER_OF_INDIVIDUALS):
        x = random.random()*(CROSSOVER_PERCENTAGE + MUTATION_PERCENTAGE + NEW_INDIVIDUALS_PERCENTAGE)

        # crossover
        if x <= CROSSOVER_PERCENTAGE:
            first_parent = int(random.random() * NUMBER_OF_INDIVIDUALS) % NUMBER_OF_INDIVIDUALS
            second_parent = int(random.random() * NUMBER_OF_INDIVIDUALS) % NUMBER_OF_INDIVIDUALS
            while second_parent == first_parent:
                second_parent = int(random.random() * NUMBER_OF_INDIVIDUALS) % NUMBER_OF_INDIVIDUALS
            temp = do_crossover(generation[first_parent][1], generation[second_parent][1])
            new_generation.append([fitness(temp, map), temp])

        # mutation
        elif x <= CROSSOVER_PERCENTAGE + MUTATION_PERCENTAGE:
            temp = do_simple_mutation(generation[i][1])
            new_generation.append([fitness(temp, map), temp])

        # new random individuals
        elif x <= CROSSOVER_PERCENTAGE + MUTATION_PERCENTAGE + NEW_INDIVIDUALS_PERCENTAGE:
            temp = generate_random_chromosome()
            new_generation.append([fitness(temp, map), temp])

    return new_generation


# vytvori novu generaciu pouzitim vyberu n najlepsich, crossover a novych jedincov a nasledne pouzije mutacie na vsetky
def create_next_generation_firstngood(generation: [], map: {}):
    generation = sorted(generation, reverse=True)
    new_generation = []
    num_of_best = (random.random()*NUMBER_OF_INDIVIDUALS) % (NUMBER_OF_INDIVIDUALS/2) + 1
    num_of_best = NUMBER_OF_INDIVIDUALS*0.4
    for i in range(0, NUMBER_OF_INDIVIDUALS):
        # replication
        if i < num_of_best:
            new_generation.append(generation[i])
            continue

        x = random.random()*(CROSSOVER_PERCENTAGE + NEW_INDIVIDUALS_PERCENTAGE)

        # crossover
        if x <= CROSSOVER_PERCENTAGE:
            first_parent = int(random.random() * NUMBER_OF_INDIVIDUALS) % NUMBER_OF_INDIVIDUALS
            second_parent = int(random.random() * NUMBER_OF_INDIVIDUALS) % NUMBER_OF_INDIVIDUALS
            while second_parent == first_parent:
                second_parent = int(random.random() * NUMBER_OF_INDIVIDUALS) % NUMBER_OF_INDIVIDUALS
            temp = do_crossover(generation[first_parent][1], generation[second_parent][1])

        # new random individuals
        elif x <= CROSSOVER_PERCENTAGE + NEW_INDIVIDUALS_PERCENTAGE:
            temp = generate_random_chromosome()

        new_generation.append([fitness(temp, map), temp])

    generation = new_generation
    new_generation = []

    for i in range(0, NUMBER_OF_INDIVIDUALS):
        temp = do_simple_mutation(generation[i][1])
        new_generation.append([fitness(temp, map), temp])

    return new_generation


# vrati najlepsieho jedinca v generacii
def find_best_individual(generation: []):
    return sorted(generation, reverse=True)[0]


# vytvara generacie a vypisuje vzdy najlepsieho jedinca
def create_society():
    map_of_towns = []
    load_map(map_of_towns, "vstup.txt")

    generation = []
    create_new_random_generation(generation, map_of_towns)
    print("Generacia: 0")
    print("Fitness: ", find_best_individual(generation)[0])
    print("Cesta: ", find_best_individual(generation)[1])

    for i in range(1, NUMBER_OF_GENERATIONS):
        generation = create_next_generation_firstngood(generation, map_of_towns)
        #generation = create_next_generation_allrandom(generation, map_of_towns)

    print("Generacia: ", i)
    print("Fitness: ", find_best_individual(generation)[0])
    print("Cesta: ", find_best_individual(generation)[1])


random.seed(0)
create_society()
