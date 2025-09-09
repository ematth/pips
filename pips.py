OPERATIONS: list[str] = ['=', '!', '>', '<', '']
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

        self.print_sol(sol)
        print('')

        def check(board, domino, x1, y1, x2, y2) -> bool:
            # check contraints for placing domino at (x1, y1) and (x2, y2)
            if board[x1][y1] == '_' or board[x2][y2] == '_':
                return False
            c1, c2 = self.board[x1][y1], self.board[x2][y2]
            # For each tile (x1, y1) and (x2, y2), recurse through its neighbors to find all connected tiles
            # and check if they satisfy the constraints of the region they are in
            # if '-', no constraints
            # if capital letter included, include only neighbor tiles with the same condition and letter
            # if #, all numbers in region must sum to #
            # if =, all numbers in region must be the same
            # if !, all numbers in region must be different
            # if <#, all numbers in region must sum to less than #
            # if >#, all numbers in region must sum to greater than #
            seen: list[tuple[int, int]] = [(x1, y1), (x2, y2)]
            for c, x, y in [(c1, x1, y1), (c2, x2, y2)]:
                stack: list[tuple[int, int]] = [(x, y)]
                while stack:
                    cx, cy = stack.pop()
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < n and 0 <= ny < len(board[nx]) and (nx, ny) not in seen:
                            if self.board[nx][ny] == c and c != '-':
                                seen.append((nx, ny))
                                stack.append((nx, ny))
            print(f'Regions for ({x1}, {y1}) & ({x2}, {y2}): {[(x, y, self.board[x][y]) for x, y in seen]}')
            d1 = [(x, y) for x, y in seen if self.board[x][y] == c1]
            d2 = [(x, y) for x, y in seen if self.board[x][y] == c2]

            vals1 = [int(board[x][y]) for x, y in d1 if board[x][y] not in ['X', '_'] and board[x][y].isdigit()]
            vals2 = [int(board[x][y]) for x, y in d2 if board[x][y] not in ['X', '_'] and board[x][y].isdigit()]
            
            b = [True, True]
            print(f'D1: {d1}, D2: {d2}')
            for i, (c, v, t) in enumerate(zip([c1, c2], [vals1, vals2], [domino[0], domino[1]])):
                if c == '-':
                    continue
                if '=' in c:
                    b[i] = (len(set(v + [t])) == 1)
                if '!' in c:
                    b[i] = (len(set(v + [t])) == len(v) + 1)
                if '<' in c:
                    b[i] = (sum(v) + int(t) < int(c[1:]))
                if '>' in c:
                    b[i] = (sum(v) + int(t) > int(c[1:]))
                if c.isdigit():
                    if c == c1 and sum(vals1) + int(domino[0]) > int(c):
                        return False
                    if c == c2 and sum(vals2) + int(domino[1]) > int(c):
                        return False
            return b[0] and b[1]

        def place(board, dominoes, i, j) -> list[list[str]] | None:
            # try horizontal
            m: int = len(board[i])
            for d in dominoes:
                if j + 1 < m and board[i][j + 1] == 'X':
                    if check(board, d, i, j, i, j + 1):
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
                    if check(board, d, i, j, i + 1, j):
                        board[i][j] = d[0]
                        board[i + 1][j] = d[1]
                        new_dominoes = dominoes[:]
                        new_dominoes.remove(d)
                        res = backtrack(board, new_dominoes, i, j + 1)
                        if res:
                            return res
                        board[i][j] = 'X'
                        board[i + 1][j] = 'X'

        def backtrack(board, dominoes, i, j) -> list[list[str]] | None:
            if i == n:
                return board
            
            m: int = len(board[i])
            if j >= m:
                return backtrack(board, dominoes, i + 1, 0)
            if board[i][j] != 'X':
                return backtrack(board, dominoes, i, j + 1)
            else:
                return place(board, dominoes, i, j)

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

