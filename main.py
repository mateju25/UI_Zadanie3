#!python3.8
import os
from math import sqrt
import random
import time
from gui_show import make_gui
import matplotlib.pyplot as plt
import threading

CROSSOVER_PERCENTAGE = 0.5  # percenta, kolko jedincov bude vytvorenych pomocou crossover
ELITISM_PERCENTAGE = 0.4  # percenta, kolko jedincov bude vytvorenych pomocou elitizmu
TOURNAMENT_PERCENTAGE = 0  # percenta, kolko jedincov bude vytvorenych pomocou tournamentu
ROULETE_PERCENTAGE = 0  # percenta, kolko jedincov bude vytvorenych pomocou roulete
MUTATION_PERCENTAGE = 0.4  # percenta, kolko jedincov v elitizmu bude zmutovanych
MUTATION_TYPE = 1  # typ mutacie
TOURNAMENT_INDIVIDUAL_PERCENTAGE = 0.4  # kolko percent z generacie bude vybratych do tournamentu

NUMBER_OF_TOWNS = 50  # pocet miest
NUMBER_OF_INDIVIDUALS = 1000  # pocet individualov
NUMBER_OF_GENERATIONS = 500  # pocet generacii


# region Pomocne funkcie a nacitanie vstupu


# nacita mapu zo suboru v tvare {i: [x, y], ...}
def load_map(p_matrix: [], p_filename: ""):
    global NUMBER_OF_TOWNS
    loaded_file = open(p_filename, "r").read().split('\n')
    towns = []
    # vytvori zoznam miest
    for i in range(0, len(loaded_file)):
        towns.append([int(coor) for coor in loaded_file[i].split(' ')])

    # vytvori maticu susednosti
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


# endregion

# region Generovanie novych jedincov(mutacie a crossover)


# vykona crossover chromozomov
def do_crossover(first_parent: [], second_parent: []) -> list:
    seq = []
    new_chromosome = []

    # zvoli nahodnu dlzku vymeneneho retazca
    len_change = random.randint(2, NUMBER_OF_TOWNS - 1)
    # zvoli nahodny zaciatok
    start_index = random.randint(0, NUMBER_OF_TOWNS - len_change)

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


# vymeni dve miesta v chromozome medzi sebou
def swap(chromosome: [], index1: int, index2: int):
    temp = chromosome[index1]
    chromosome[index1] = chromosome[index2]
    chromosome[index2] = temp


# vykona mutaciu dvoch miest vedla seba na jednom chromozome
def do_simple_mutation(chromosome: []) -> list:
    index = random.randint(0, NUMBER_OF_TOWNS - 2)
    swap(chromosome, index, index + 1)
    return chromosome


# vykona mutaciu dvoch nahodnych miest na jednom chromozome
def do_random_mutation(chromosome: []) -> list:
    index1 = random.randint(0, NUMBER_OF_TOWNS - 1)
    index2 = random.randint(0, NUMBER_OF_TOWNS - 1)
    while index2 != index1:
        index2 = random.randint(0, NUMBER_OF_TOWNS - 1)
    swap(chromosome, index1, index2)
    return chromosome


# vykona mutaciu, a to zrotuje sekvenciu miest medzi dvoma mestami na jednom chromozome
def do_difficult_mutation(chromosome: []) -> list:
    reversed_seq = []
    # zvoli nahodnu dlzku retazca, ktory bude obrateny (od 2 po NUMBER_OF_TOWNS-1)
    len_change = random.randint(2, NUMBER_OF_TOWNS - 1)
    # zvoli nahodny zaciatok
    start_index = random.randint(0, NUMBER_OF_TOWNS - len_change)

    # vytvori podsekvenciu
    for i in range(start_index, start_index + len_change - 1):
        reversed_seq.insert(0, chromosome[i])
    # nakopiruje sekvenciu naopak
    for i in range(start_index, start_index + len_change - 1):
        chromosome[i] = reversed_seq[i - start_index]

    return chromosome


# endregion

# region Vyber rodicov a tvorba generacii


# vytvori novu generaciu vytvorenim turnajov o n jedincoch a vzdy vyhraju dvaja a pouzijem na nich crossover
def do_roulete(generation: []):
    first_parent = random.choices([x[1] for x in generation], [x[0] for x in generation], k=1)[0]
    second_parent = random.choices([x[1] for x in generation], [x[0] for x in generation], k=1)[0]
    return do_crossover(first_parent, second_parent)


# vytvori novu generaciu vytvorenim turnajov o n jedincoch a vzdy vyhraju dvaja a pouzijem na nich crossover
def do_tournament(generation: []):
    first_parent = \
        sorted(random.choices(generation, k=int(TOURNAMENT_INDIVIDUAL_PERCENTAGE * NUMBER_OF_INDIVIDUALS)),
               reverse=True)[
            0][1]
    second_parent = \
        sorted(random.choices(generation, k=int(TOURNAMENT_INDIVIDUAL_PERCENTAGE * NUMBER_OF_INDIVIDUALS)),
               reverse=True)[
            0][1]
    return do_crossover(first_parent, second_parent)


# vyrata fitness pre jeden chromozom
def fitness(chromosome: [], p_map: []) -> float:
    sum_of_nums = 0
    for i in range(0, NUMBER_OF_TOWNS - 1):
        sum_of_nums += p_map[chromosome[i] - 1][chromosome[i + 1] - 1]

    sum_of_nums += p_map[chromosome[NUMBER_OF_TOWNS - 1] - 1][chromosome[0] - 1]
    return 1 / sum_of_nums


# vytvori nahodnu generaciu, pouzitie pri nultej generacii
def create_zero_random_generation(generation: [], p_map: []):
    for i in range(0, NUMBER_OF_INDIVIDUALS):
        temp = generate_random_chromosome()
        generation.append([fitness(temp, p_map), temp])


# vytvori novu generaciu pouzitim vyberu n najlepsich, crossover a novych jedincov a nasledne pouzije mutacie na vsetky
def create_next_generation(generation: [], p_map: []):
    generation = sorted(generation, reverse=True)
    new_generation = []

    # elitism
    for i in range(0, int(NUMBER_OF_INDIVIDUALS * ELITISM_PERCENTAGE)):
        if random.random() < MUTATION_PERCENTAGE:
            if MUTATION_TYPE == 1:
                temp = do_simple_mutation(generation[i][1])
            elif MUTATION_TYPE == 2:
                temp = do_random_mutation(generation[i][1])
            else:
                temp = do_difficult_mutation(generation[i][1])
            new_generation.append([fitness(temp, p_map), temp])
        else:
            new_generation.append(generation[i])

    # pure crossover
    for i in range(0, int(NUMBER_OF_INDIVIDUALS * CROSSOVER_PERCENTAGE)):
        first_parent = random.randint(0, NUMBER_OF_INDIVIDUALS - 1)
        second_parent = random.randint(0, NUMBER_OF_INDIVIDUALS - 1)
        while second_parent == first_parent:
            second_parent = random.randint(0, NUMBER_OF_INDIVIDUALS - 1)
        temp = do_crossover(generation[first_parent][1], generation[second_parent][1])
        new_generation.append([fitness(temp, p_map), temp])

    # tournament
    for i in range(0, int(NUMBER_OF_INDIVIDUALS * TOURNAMENT_PERCENTAGE)):
        temp = do_tournament(generation)
        new_generation.append([fitness(temp, p_map), temp])

    # roulete
    for i in range(0, int(NUMBER_OF_INDIVIDUALS * ROULETE_PERCENTAGE)):
        temp = do_roulete(generation)
        new_generation.append([fitness(temp, p_map), temp])

    # ak nie je generacia dost plna, dopln len nahodnymi
    while len(new_generation) < NUMBER_OF_INDIVIDUALS:
        temp = generate_random_chromosome()
        new_generation.append([fitness(temp, p_map), temp])

    return new_generation


# endregion

# region Vstupy a hlavny cyklus programu
# vrati najlepsieho jedinca v generacii
def find_best_individual(generation: []):
    return sorted(generation, reverse=True)[0]


# vrati priemer fitness funkcii
def find_average_fitness(generation: []):
    sum_of_nums = 0
    for x in generation:
        sum_of_nums += x[0]
    return sum_of_nums / NUMBER_OF_GENERATIONS


# vypise info o generacii
def print_generation_info(pos: int, generation: []):
    print("Generácia:", pos)
    print("Fitness najlepšieho: ", find_best_individual(generation)[0])
    print("Cesta: ", find_best_individual(generation)[1])
    print()


# vytvara generacie a vypisuje vzdy najlepsieho jedinca
def create_society(file_name, choice):
    map_of_towns = []
    generation = []
    average = []
    bests = []

    # nacita vstup
    load_map(map_of_towns, file_name)

    # vytvori nultu generaciu
    create_zero_random_generation(generation, map_of_towns)
    best = find_best_individual(generation)
    bests.append(best[0])
    average.append(find_average_fitness(generation))
    print_generation_info(0, generation)

    start = time.time()

    # vytvara postupne generacie
    for i in range(1, NUMBER_OF_GENERATIONS):
        generation = create_next_generation(generation, map_of_towns)
        if choice == 'y':
            print_generation_info(i, generation)
        average.append(find_average_fitness(generation))
        bests.append(find_best_individual(generation)[0])
        # pamata si najlepsieho
        if find_best_individual(generation)[0] > best[0]:
            best = find_best_individual(generation)

    end = time.time()

    # vypise koncove zhodnotenie
    print("-----------------------------------------")
    print("Generacii: ", NUMBER_OF_GENERATIONS, "| Jedincov: ", NUMBER_OF_INDIVIDUALS,
          "| Mesta: ", NUMBER_OF_TOWNS, "| Cas: ", end - start, "s")
    print("\nNajlepsi: ")
    print("Fitness: ", best[0])
    print("Cesta: ", best[1])

    # vytvori thread pre gui zobrazenie cesty
    t1 = threading.Thread(target=make_gui, args=(best[1], file_name))
    t1.start()

    # vytvori graf priemerne a najlepsie fitness
    f, axis = plt.subplots()
    axis.plot(average, label="Priemerne")
    axis.plot(bests, label="Najlepsi")
    axis.set(xlabel='Generations', ylabel='Fitness',
             title='Generation with {} individuals vs. Fitness '.format(NUMBER_OF_INDIVIDUALS))
    axis.grid()
    plt.legend()
    plt.show()

    t1.join()


# vypise hlavicku
def print_header():
    print()
    print("*****************************************************************************")
    print("                             Obchodný cestujúci                              ")
    print("                           Autor: Matej Delinčák                             ")
    print("*****************************************************************************")
    print()


# zisti ci subor existuje
def checks_existency():
    filename = input("Zadaj meno vstupného súboru: ")
    while not os.path.exists(filename):
        print("Súbor neexistuje.")
        filename = input("Zadaj meno vstupného súboru: ")
    return filename


# zisti ci vstup
def is_input_number(string, no_zero=False):
    lines = input(string)
    while (not lines.isdigit()) or (int(lines) < 0) or (no_zero and int(lines) == 0):
        print("Chybný vstup.")
        lines = input(string)
    return int(lines)


# vypise menu
def menu():
    global MUTATION_TYPE, NUMBER_OF_INDIVIDUALS, NUMBER_OF_GENERATIONS, ELITISM_PERCENTAGE, \
        CROSSOVER_PERCENTAGE, TOURNAMENT_PERCENTAGE, TOURNAMENT_INDIVIDUAL_PERCENTAGE, ROULETE_PERCENTAGE

    file_name = checks_existency()
    print()
    NUMBER_OF_GENERATIONS = is_input_number("Zadaj počet generácií: ", True)
    NUMBER_OF_INDIVIDUALS = is_input_number("Zadaj počet jedincov: ", True)
    ELITISM_PERCENTAGE = is_input_number("Zadaj percentá pre elitizmus: ") / 100
    CROSSOVER_PERCENTAGE = is_input_number("Zadaj percentá pre crossover: ") / 100
    TOURNAMENT_PERCENTAGE = is_input_number("Zadaj percentá pre tournament: ") / 100
    if TOURNAMENT_PERCENTAGE != 0.0:
        TOURNAMENT_INDIVIDUAL_PERCENTAGE = is_input_number("Zadaj percentá pre vyber jedincov pre tournament: ") / 100
    ROULETE_PERCENTAGE = is_input_number("Zadaj percentá pre ruletu: ") / 100
    if ELITISM_PERCENTAGE + CROSSOVER_PERCENTAGE + TOURNAMENT_PERCENTAGE + ROULETE_PERCENTAGE > 1:
        print("Súčet percent pravdepodobnosti je viac ako 100.")
        print()
        menu()
        return
    print()
    print("Vyber typ mutácie:")
    print("1 - jednoduchá mutácia")
    print("2 - náhodná mutácia")
    print("iné - zložitá mutácia")
    MUTATION_TYPE = is_input_number("Zadaj možnosť: ", True)
    print()
    choice = input("Chceš vypísať všetky generacie? y/iné: ")
    print()

    create_society(file_name, choice)


# endregion


print_header()
menu()
