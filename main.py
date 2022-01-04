import multiprocessing as mp
import csv
import os
import random
from typing import List
from colorama import Fore, Style, init


def print_matrix(matrix: List[List[int]]) -> None:
    print("\n" + "\n".join(["\t".join([str(cell) for cell in row]) for row in matrix]))


def matrix_reader(file_name: str) -> List[List[int]]:
    with open(file_name, "r") as file:
        file_reader = csv.reader(file, delimiter="\t")
        result = []
        for i in file_reader:
            if i:
                result.append([int(j) for j in i])
        return result


def matrix_writer(matrix: List[List[int]], file_name: str) -> None:
    with open(file_name, "w") as file:
        file_writer = csv.writer(file, delimiter="\t")
        file_writer.writerows(matrix)


def matrix_gen(n: int, m: int) -> List[List[int]]:
    matrix = []
    for i in range(n):
        matrix.append([])
        for j in range(m):
            matrix[i].append(random.randint(1, 100))
    return matrix


def worker(i: int, j: int, a: list, b: list, que: mp.Queue) -> None:
    buffer_list = []
    for k in range(len(a[0]) or len(b)):
        buffer_list.append(a[i][k] * b[k][j])

    result_dict = {"result": sum(buffer_list), "i": i, "j": j}

    que.put(result_dict)


def new_matrix_input():
    while True:
        try:
            n = int(input("Enter the number of lines: "))
            break
        except ValueError:
            print(Fore.RED + "\nInvalid input\n" + Fore.RESET)
    while True:
        try:
            m = int(input("Enter the number of columns: "))
            break
        except ValueError:
            print(Fore.RED + "\nInvalid input\n" + Fore.RESET)

    matrix1 = matrix_gen(n, m)
    matrix2 = matrix_gen(m, n)

    matrix_writer(matrix1, MATRIX1_FILE)
    matrix_writer(matrix2, MATRIX2_FILE)
    return matrix1, matrix2


def old_matrix_input():
    if not os.path.exists(MATRIX1_FILE) or not os.path.exists(MATRIX2_FILE):
        print(Fore.RED + "\nFiles not exist" + Fore.RESET)
        return None, None
    return matrix_reader(MATRIX1_FILE), matrix_reader(MATRIX2_FILE)


def main():
    manager = mp.Manager()
    commands_dict = {"1": old_matrix_input, "2": new_matrix_input, "3": exit}

    while True:
        command_input = input(Style.BRIGHT + "\nSelecting a data source\n" + Style.RESET_ALL +
                              "1. Load from files\n2. Generate new values\n3. Exit\n")
        if command_input in commands_dict:
            matrix1, matrix2 = commands_dict[command_input]()
            if matrix1 is not None and matrix2 is not None:
                matrix_result = [[0 for _ in range(len(matrix2[0]))] for _ in range(len(matrix2[0]))]

                print_matrix(matrix1)
                print_matrix(matrix2)

                processes_list = []
                que = manager.Queue()

                for i in range(len(matrix_result)):
                    for j in range(len(matrix_result[i])):
                        p = mp.Process(target=worker, args=(i, j, matrix1, matrix2, que,), )
                        processes_list.append(p)

                for p in processes_list:
                    p.start()
                for p in processes_list:
                    p.join()

                for i in range(len(matrix_result)):
                    for j in range(len(matrix_result[i])):
                        r = que.get()
                        matrix_result[r["i"]][r["j"]] = r["result"]

                print_matrix(matrix_result)
                matrix_writer(matrix_result, RESULT_FILE)

        else:
            print(Fore.RED + "\nCommand not found\n" + Fore.RESET)


if __name__ == "__main__":
    init()
    MATRIX1_FILE = "matrix1.csv"
    MATRIX2_FILE = "matrix2.csv"
    RESULT_FILE = "result.csv"
    main()
