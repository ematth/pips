from pips import PipGame
import time

if __name__ == '__main__':
    for i in range(1, 20):
        print(f'GAME #{i}:')
        game = PipGame(f'boards/board{i}.pips')
        print(game)
        game.solution()
        print('------------------------')