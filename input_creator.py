import random


def create_input_file(file_name: '', size_of_map, num_of_towns):
    f = open(file_name, "w")
    for i in range(num_of_towns):
        f.write("{} {}".format(random.randint(0, size_of_map), random.randint(0, size_of_map)))
        if i != num_of_towns-1:
            f.write("\n")
    f.close()
    return file_name
