from math import sqrt
import random
import time
from gui import make_gui
from kruskal import load_edges
from input_creator import create_input_file

NEW_INDIVIDUALS_PERCENTAGE = 10
MUTATION_PERCENTAGE = 10
CROSSOVER_PERCENTAGE = 90
TOURNAMENT_INDIVIDUALS_PERCENTAGE = 60

NUMBER_OF_TOWNS = 40
NUMBER_OF_INDIVIDUALS = 500
NUMBER_OF_GENERATIONS = 10000


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

    NUMBER_OF_TOWNS = len(loaded_file)


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


# vymeni dve miesta medzi sebou
def swap(chromosome: [], index1: int, index2: int):
    temp = chromosome[index1]
    chromosome[index1] = chromosome[index2]
    chromosome[index2] = temp


# vykona mutaciu dvoch miest vedla seba na jednom chromozome
def do_simple_mutation(chromosome: []) -> list:
    index = int(random.random() * NUMBER_OF_TOWNS) % (NUMBER_OF_TOWNS - 1)
    swap(chromosome, index, index + 1)
    return chromosome


# vykona mutaciu, a to zrotuje sekvenciu miest medzi dvoma mestami na jednom chromozome
def do_difficult_mutation(chromosome: []) -> list:
    reversed_seq = []
    # zvoli nahodnu dlzku retazca, ktory bude obrateny (od 2 po NUMBER_OF_TOWNS-1)
    len_change = int(random.random() * NUMBER_OF_TOWNS) % (NUMBER_OF_TOWNS - 2) + 2
    # zvoli nahodny zaciatok
    start_index = int(random.random() * NUMBER_OF_TOWNS) % (NUMBER_OF_TOWNS - len_change + 1)

    for i in range(start_index, start_index + len_change):
        reversed_seq.insert(0, chromosome[i])

    for i in range(start_index, start_index + len_change):
        chromosome[i] = reversed_seq[i - start_index]

    return chromosome


# vykona mutaciu, ale len vtedy, ak to pomoze k zlepsenie fitness funkcie
def do_intelligent_mutation(chromosome: [], map: {}) -> list:
    for i in range(0, NUMBER_OF_TOWNS-1):
        temp_chromosome = [x for x in chromosome]
        swap(temp_chromosome, i, i+1)
        if fitness(temp_chromosome, map) > fitness(chromosome, map):
            return temp_chromosome
    return do_simple_mutation(chromosome)


# vyrata fitness pre jeden chromozom
def fitness(chromosome: [], map: []) -> float:
    sum = 0
    for i in range(0, NUMBER_OF_TOWNS - 1):
        sum += map[chromosome[i]-1][chromosome[i + 1]-1]

    sum += map[chromosome[NUMBER_OF_TOWNS-1]-1][chromosome[0]-1]
    return 1/sum


# vytvori nahodnu generaciu, pouzitie pri nultej generacii
def create_zero_random_generation(generation: [], map: []):
    for i in range(0, NUMBER_OF_INDIVIDUALS):
        temp = generate_random_chromosome()
        generation.append([fitness(temp, map), temp])


# vytvori nahodnu nultu generaciu, pouzitim kruskalovho algortimu
def create_kruskal_random_generation(generation: [], map: []):
    for i in range(0, NUMBER_OF_INDIVIDUALS):
        temp = do_difficult_mutation(load_edges(map))
        generation.append([fitness(temp, map), temp])


# vytvori novu generaciu pouzitim noych jedincov, mutacie alebo crossover
def create_next_generation_allrandom(generation: [], map: []):
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
def create_next_generation_firstngood(generation: [], map: []):
    generation = sorted(generation, reverse=True)
    new_generation = []
    num_of_best = (random.random()*NUMBER_OF_INDIVIDUALS) % (NUMBER_OF_INDIVIDUALS/2) + 1
    num_of_best = NUMBER_OF_INDIVIDUALS*0.4
    for i in range(0, NUMBER_OF_INDIVIDUALS):
        # replication
        if i < num_of_best:
            temp = do_simple_mutation(generation[i][1])
            #temp = do_intelligent_mutation(generation[i][1], map)
            new_generation.append([fitness(temp, map), temp])
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

    return new_generation


# vytvori novu generaciu vytvorenim turnajov o n jedincoch a vzdy vyhraju dvaja a pouzijem na nich crossover
def create_next_generation_tournament(generation: [], map: []):
    new_generation = []
    for i in range(0, NUMBER_OF_INDIVIDUALS):
        tournament_generation = []

        while len(tournament_generation) < (TOURNAMENT_INDIVIDUALS_PERCENTAGE/100)*NUMBER_OF_INDIVIDUALS:
            tournament_generation.append(generation[random.randint(0, NUMBER_OF_INDIVIDUALS-1)])
        tournament_generation = sorted(tournament_generation)
        fighter = tournament_generation[0]

        tournament_generation = []
        while len(tournament_generation) < (TOURNAMENT_INDIVIDUALS_PERCENTAGE / 100) * NUMBER_OF_INDIVIDUALS:
            tournament_generation.append(generation[random.randint(0, NUMBER_OF_INDIVIDUALS-1)])

        tournament_generation = sorted(tournament_generation)
        temp = do_crossover(fighter[1], tournament_generation[1][1])
        new_generation.append([fitness(temp, map), temp])

    return new_generation


# vrati najlepsieho jedinca v generacii
def find_best_individual(generation: []):
    return sorted(generation, reverse=True)[0]


# vytvara generacie a vypisuje vzdy najlepsieho jedinca
def create_society():
    map_of_towns = []
    file_name = "nahodny.txt"
    load_map(map_of_towns, file_name)
    #load_map(map_of_towns, create_input_file(file_name, 200, NUMBER_OF_TOWNS))

    generation = []
    create_zero_random_generation(generation, map_of_towns)
    #create_kruskal_random_generation(generation, map_of_towns)
    print("Generacia: 0")
    print("Fitness: ", find_best_individual(generation)[0])
    print("Cesta: ", find_best_individual(generation)[1])
    start = time.time()
    best = find_best_individual(generation)
    for i in range(1, NUMBER_OF_GENERATIONS):
        generation = create_next_generation_firstngood(generation, map_of_towns)
        #generation = create_next_generation_allrandom(generation, map_of_towns)
        #generation = create_next_generation_tournament(generation, map_of_towns)
        if find_best_individual(generation)[0] > best[0]:
            best = find_best_individual(generation)
    end = time.time()
    print("Generacia: ", i)
    print("Fitness: ", find_best_individual(generation)[0])
    print("Cesta: ", find_best_individual(generation)[1])
    print()
    print("Generacii: ", NUMBER_OF_GENERATIONS, "| Jedincov: ", NUMBER_OF_INDIVIDUALS,
          "| Mesta: ", NUMBER_OF_TOWNS, "| Cas: ", end - start)
    print()
    print("-----------------------------------------\nNajlepsi:")
    print("Fitness: ", best[0])
    print("Cesta: ", best[1])
    make_gui(best[1], file_name)


#random.seed(0)
create_society()
