OPERATIONS: list[str] = ['=', '=/=', '>', '<', '']
import csv, sys

class PipGame():
    def __init__(self, board: str) -> None:
        
        with open(board, 'r') as f:
            reader = csv.reader(f)
            self.board: list[list[str]] = []
            self.dominoes = list(next(reader))

            for r in reader:
                row: list[str] = []
                for c in r:
                    row.append(c.strip())
                self.board.append(row)

    def __str__(self) -> str:
        out = ''
        for r in self.board:
            out += ', '.join(r) + '\n'
        out += f'Dominoes: {self.dominoes}\n'
        return out
    
    def print_sol(self, sol) -> None:
        for r in sol:
            print(r)
    
    def solution(self) -> bool:
        print('Num tiles: ', sum(len(r) - r.count('') for r in self.board))
        if len(self.dominoes) != sum(len(r) - r.count('') for r in self.board):
            print("Invalid game: number of nodes is not even")
            return False

        sol = []
        for r in self.board:
            row = []
            for c in r:
                if c:
                    row.append('X')
                else:
                    row.append('_')
            sol.append(row)

        n: int = len(self.board)
        print('n: ', n)
        i, j = 0, 0
        while i < n:
            m: int = len(sol[i])

            # if sol[i][j] == -1:
            #     # try to place a domino horizontally or vertically
            #     if j < m - 1 and sol[i][j + 1] == -1:
            #         # place horizontally
            #         d = self.dominoes.pop(0)
            #         sol[i][j], sol[i][j + 1] = d[0], d[1]

            #     elif i < n - 1 and j < m - 1 and sol[i+1][j] == -1:
            #         # place vertically
            #         d = self.dominoes.pop(0)
            #         sol[i][j], sol[i+1][j] = d[0], d[1]
            
            j += 1
            if j >= m:
                j = 0
                i += 1
                        
        self.print_sol(sol)
        return False
    



# is valid Pips game?
# 1. Number of nodes % 2 == 0
# 2. A solution exists given bag of dominoes

if __name__ == '__main__':
    game = PipGame(sys.argv[1])
    print(game)
    game.solution()

