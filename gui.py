from tkinter import *

CONSTANT = 4
SIZE = CONSTANT*200


def load_map(p_matrix: {}, p_filename: ""):
    loaded_file = open(p_filename, "r").read().split('\n')
    for i in range(0, len(loaded_file)):
        p_matrix[i+1] = [int(coor) for coor in loaded_file[i].split(' ')]


def print_path(canvas, path: [], file_name):
    map_of_points = {}
    load_map(map_of_points, file_name)

    for x in range(10, SIZE, 10):
        canvas.create_line(0, x, SIZE, x, fill='lightgrey')
    for x in range(10, SIZE, 10):
        canvas.create_line(x, 0, x, SIZE, fill='lightgrey')

    for x in map_of_points:
        canvas.create_oval(CONSTANT*(map_of_points[x][0])-2, CONSTANT*(map_of_points[x][1])-2,
                           CONSTANT*(map_of_points[x][0])+2, CONSTANT*(map_of_points[x][1])+2, fill="black")
        canvas.create_text(CONSTANT*(map_of_points[x][0]), CONSTANT*(map_of_points[x][1])+12, fill="red",
                           font="Times 8 italic bold", text=str(x))

    for x in range(0, len(path)-1):
        canvas.create_line(CONSTANT*map_of_points[path[x]][0], CONSTANT*map_of_points[path[x]][1],
                           CONSTANT*map_of_points[path[x+1]][0], CONSTANT*map_of_points[path[x+1]][1], width=2)
    canvas.create_line(CONSTANT*map_of_points[path[len(path)-1]][0], CONSTANT*map_of_points[path[len(path)-1]][1],
                       CONSTANT*map_of_points[path[0]][0], CONSTANT*map_of_points[path[0]][1], width=2)


def make_gui(path: [], file_name):
    master = Tk()
    master.geometry("900x900")
    master.title("Cesta obchodneho cestujuceho")
    canvas = Canvas(master, width=SIZE+15, height=SIZE+15)
    canvas.pack()

    print_path(canvas, path, file_name)

    mainloop()