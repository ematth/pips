from pips_solver import GraphMultiProcess
import time
import os, json
from tqdm import tqdm
from numba import jit, cuda

DIFFICULTIES = ['easy', 'medium', 'hard']

def run_solver_all_GPU(timeout_limit = 15) -> None:
    total_time: float = 0.0
    for difficulty in DIFFICULTIES:
        total_time += run_solver_GPU(difficulty, timeout_limit)
    print('------------------------')
    print('------------------------')
    print(f'TOTAL TIME: {round(total_time, 3)} seconds')


def run_solver_GPU(difficulty: str = 'easy', timeout_limit = 15) -> float:
    s = time.time()
    matching_solutions = 0
    total_boards = 0
    no_solution_boards = 0
    timeout_boards = 0
    timeout_limit = timeout_limit
    print('\n------------------------')
    print(f'Difficulty: {difficulty}, Timeout: {timeout_limit}s')
    for file in os.listdir('boards_json'):
        if file.endswith('.json'):
            total_boards += 1
            data = json.load(open(f'boards_json/{file}'))
            game = GraphMultiProcessGPU(data, difficulty)
            isSolved = game.solve(timeout=timeout_limit)
            if isSolved is True:
                matching_solutions += 1
            elif isSolved is False:
                no_solution_boards += 1
            else:  # isSolved is None (timeout)
                print(f'Timeout on puzzle {file}\n')
                timeout_boards += 1
    e = time.time()
    print(f'Time taken: {round(e - s, 3)} seconds')
    avg = (e - s) / total_boards
    print(f'Average time/puzzle: {round(avg, 3)} seconds')
    print(f'[✅] {matching_solutions} / {total_boards} matching solutions')
    print(f'[❌] {no_solution_boards} / {total_boards} no solution boards')
    print(f'[🕛] {timeout_boards} / {total_boards} timed out (>{timeout_limit}s)')
    return e - s


def run_solver_all(timeout_limit = 15) -> None:
    total_time: float = 0.0
    for difficulty in DIFFICULTIES:
        total_time += run_solver(difficulty, timeout_limit)
    print('------------------------')
    print('------------------------')
    print(f'TOTAL TIME: {round(total_time, 3)} seconds')


def run_solver(difficulty: str = 'easy', timeout_limit = 15) -> float:
    s = time.time()
    matching_solutions = 0
    total_boards = 0
    no_solution_boards = 0
    timeout_boards = 0
    timeout_limit = timeout_limit
    print('\n------------------------')
    print(f'Difficulty: {difficulty}, Timeout: {timeout_limit}s')
    for file in tqdm(os.listdir('boards_json')):
        if file.endswith('.json'):
            total_boards += 1
            data = json.load(open(f'boards_json/{file}'))
            game = GraphMultiProcess(data, difficulty)
            isSolved = game.solve(timeout=timeout_limit)
            if isSolved is True:
                matching_solutions += 1
            elif isSolved is False:
                no_solution_boards += 1
            else:  # isSolved is None (timeout)
                print(f'Timeout on puzzle {file}\n')
                timeout_boards += 1
    e = time.time()
    print(f'Time taken: {round(e - s, 3)} seconds')
    avg = (e - s) / total_boards
    print(f'Average time/puzzle: {round(avg, 3)} seconds')
    print(f'[✅] {matching_solutions} / {total_boards} matching solutions')
    print(f'[❌] {no_solution_boards} / {total_boards} no solution boards')
    print(f'[🕛] {timeout_boards} / {total_boards} timed out (>{timeout_limit}s)')
    return e - s

if __name__ == '__main__':
    run_solver_all(15)