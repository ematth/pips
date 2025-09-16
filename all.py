from pips import PipGame
import time
import os

if __name__ == '__main__':
    s = time.time()
    matching_solutions = 0
    total_boards = 0
    for file in os.listdir('boards'):
        if file.endswith('.pips'):
            total_boards += 1
            print(f'{file}:')
            game = PipGame(f'boards/{file}')
            print(game)
            _, matches = game.solution()
            if matches:
                matching_solutions += 1
            print('------------------------')
    e = time.time()
    print(f'Time taken: {round(e - s, 3)} seconds')
    avg = (e - s) / len(os.listdir('boards'))
    print(f'Average time/puzzle: {round(avg, 3)} seconds')
    print(f'{matching_solutions} / {total_boards} matching solutions')