OPERATIONS: list[str] = ['=', '=/=', '>', '<', '']
import csv, sys

class PipGame():
    def __init__(self, board: str) -> None:
        
        with open(board, 'r') as f:
            reader = csv.reader(f)
            self.board: list[list[str]] = []
            self.dominoes = list(next(reader))
            self.dominoes = [(self.dominoes[i].strip(), self.dominoes[i+1].strip()) for i in range(0, len(self.dominoes), 2)]

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
        if not sol:
            print("No solution found")
            return
        for r in sol:
            print(r)
    
    def solution(self) -> list[list[str]] | None:
        print('Num tiles: ', sum(len(r) - r.count('') for r in self.board))
        if len(self.dominoes) * 2 != sum(len(r) - r.count('') for r in self.board):
            print("Invalid game: number of nodes is not even")
            return False

        # create a copy of the board for returning solution
        sol = []
        for r in self.board:
            row = []
            for c in r:
                if c:
                    row.append('X')
                else:
                    row.append('_')
            sol.append(row)

        n: int = len(sol)
        def backtrack(board, dominoes, i, j) -> list[list[str]] | None:
            if i == n:
                return board
            
            m: int = len(board[i])
            if j >= m:
                return backtrack(board, dominoes, i + 1, 0)
            if board[i][j] != 'X':
                return backtrack(board, dominoes, i, j + 1)
            for d in dominoes:
                # try horizontal
                if j + 1 < m and board[i][j + 1] == 'X':
                    board[i][j] = d[0]
                    board[i][j + 1] = d[1]
                    new_dominoes = dominoes[:]
                    new_dominoes.remove(d)
                    res = backtrack(board, new_dominoes, i, j + 2)
                    if res:
                        return res
                    board[i][j] = 'X'
                    board[i][j + 1] = 'X'
                # try vertical
                if i + 1 < n and j < len(board[i + 1]) and board[i + 1][j] == 'X':
                    board[i][j] = d[0]
                    board[i + 1][j] = d[1]
                    new_dominoes = dominoes[:]
                    new_dominoes.remove(d)
                    res = backtrack(board, new_dominoes, i, j + 1)
                    if res:
                        return res
                    board[i][j] = 'X'
                    board[i + 1][j] = 'X'
            # no domino fits here
            return None

        sol = backtrack(sol, self.dominoes, 0, 0)                
        self.print_sol(sol)
        return sol

# is valid Pips game?
# 1. Number of nodes % 2 == 0
# 2. A solution exists given list of dominoes

if __name__ == '__main__':
    game = PipGame(sys.argv[1])
    print(game)
    game.solution()

