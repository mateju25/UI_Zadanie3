from tkinter import *


CONSTANT = 4


def load_map(p_matrix: {}, p_filename: ""):
    loaded_file = open(p_filename, "r").read().split('\n')
    for i in range(0, len(loaded_file)):
        p_matrix[i] = [int(coor) for coor in loaded_file[i].split(' ')]


def print_path(canvas, path: []):
    map_of_points = {}
    load_map(map_of_points, "vstup.txt")
    for x in map_of_points:
        canvas.create_oval(CONSTANT*(map_of_points[x][0])-2, CONSTANT*(map_of_points[x][1])-2, CONSTANT*(map_of_points[x][0])+2, CONSTANT*(map_of_points[x][1])+2, fill="black")
        canvas.create_text(CONSTANT*(map_of_points[x][0]), CONSTANT*(map_of_points[x][1])+8, fill="blue", font="Times 8 italic bold",
                           text=str(x+1))
    for x in range(0, len(path)-1):
        canvas.create_line(CONSTANT*map_of_points[x][0], CONSTANT*map_of_points[x][1], CONSTANT*map_of_points[x+1][0], CONSTANT*map_of_points[x+1][1])
    canvas.create_line(CONSTANT*map_of_points[len(path)-1][0], CONSTANT*map_of_points[len(path)-1][1], CONSTANT*map_of_points[0][0],
                       CONSTANT*map_of_points[0][1])


def make_gui(path: []):
    master = Tk()
    master.geometry("900x900")
    canvas = Canvas(master, width=CONSTANT*200+10, height=CONSTANT*200+10)
    canvas.pack()

    print_path(canvas, path)

    mainloop()