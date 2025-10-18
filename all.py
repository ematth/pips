from pips3 import Graph
import time
import os, json, sys
from tqdm import tqdm

if __name__ == '__main__':
    s = time.time()
    matching_solutions = 0
    total_boards = 0
    no_solution_boards = 0
    timeout_boards = 0
    timeout_limit = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    for difficulty in ['easy', 'medium', 'hard']:
        print(f'Difficulty: {difficulty}, Timeout: {timeout_limit}s')
        for file in tqdm(os.listdir('boards_json')):
            if file.endswith('.json'):
                total_boards += 1
                data = json.load(open(f'boards_json/{file}'))
                game = Graph(data, difficulty)
                isSolved = game.solve(timeout=timeout_limit)
                if isSolved is True:
                    matching_solutions += 1
                elif isSolved is False:
                    no_solution_boards += 1
                else:  # isSolved is None (timeout)
                    print(f'Timeout on puzzle {file}\n')
                    timeout_boards += 1
    print('------------------------')
    e = time.time()
    print(f'Time taken: {round(e - s, 3)} seconds')
    avg = (e - s) / total_boards
    print(f'Average time/puzzle: {round(avg, 3)} seconds')
    print(f'[OK] {matching_solutions} / {total_boards} matching solutions')
    print(f'[FAIL] {no_solution_boards} / {total_boards} no solution boards')
    print(f'[TIMEOUT] {timeout_boards} / {total_boards} timed out (>{timeout_limit}s)')