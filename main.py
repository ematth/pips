from pips import PipGame

if __name__ == '__main__':
    for i in range(1, 16):
        print(f'GAME #{i}:')
        game = PipGame(f'boards/board{i}.pips')
        print(game)
        game.solution()
        print('------------------------')