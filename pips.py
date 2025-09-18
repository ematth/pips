OPERATIONS: list[str] = ['=', '!', '>', '<', '']
import csv, sys, os, ast

class PipGame():
    def __init__(self, board: str) -> None:
        self.board_path = board
        with open(board, 'r') as f:
            lines = f.readlines()
            
            # Parse dominoes
            domino_line = lines[0]
            domino_values = [d.strip() for d in domino_line.split(',')]
            self.dominoes = [(domino_values[i], domino_values[i+1]) for i in range(0, len(domino_values), 2)]
            
            # Parse board
            self.board = []
            board_lines = lines[1:]
            for line in board_lines:
                # Handle trailing newlines
                line = line.strip()
                if line:
                    self.board.append([c.strip() for c in line.split(',')])

    @staticmethod
    def get_numeric_constraint(constraint_str):
        num_str = ""
        for char in constraint_str:
            if char.isdigit():
                num_str += char
            else:
                break # stop at first non-digit
        if num_str:
            return int(num_str)
        return None

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
    
    def solution(self) -> tuple[list[list[str]] | None, bool]:
        num_tiles = sum(len(r) - r.count('') for r in self.board)
        #print('Num tiles: ', num_tiles)
        if len(self.dominoes) * 2 != num_tiles:
            print("Invalid game: number of nodes is not even")
            return None, False

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

        # Function to check if a domino can be placed at (x1, y1) and (x2, y2)
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
            def find_region(start_x, start_y):
                constraint = self.board[start_x][start_y]
                if constraint == '-':
                    return [(start_x, start_y)]
                
                q = [(start_x, start_y)]
                visited = set([(start_x, start_y)])
                
                head = 0
                while head < len(q):
                    cx, cy = q[head]
                    head += 1
                    
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < n and 0 <= ny < len(self.board[nx]) and (nx, ny) not in visited:
                            if self.board[nx][ny] == constraint:
                                visited.add((nx, ny))
                                q.append((nx, ny))
                return q

            d1 = find_region(x1, y1)
            d2 = find_region(x2, y2)

            vals1 = [int(board[x][y]) for x, y in d1 if board[x][y] not in ['X', '_'] and board[x][y].isdigit()]
            vals2 = [int(board[x][y]) for x, y in d2 if board[x][y] not in ['X', '_'] and board[x][y].isdigit()]
            
            b = [True, True]
            # Check for region 1
            if c1 != '-':
                all_vals = list(vals1) # copy
                all_vals.append(int(domino[0]))
                if c1 == c2:
                    all_vals.append(int(domino[1]))
                
                open_count = sum(1 for x,y in d1 if board[x][y] == 'X')
                is_full = (open_count == (2 if c1 == c2 else 1))

                if '=' in c1 and len(set(all_vals)) > 1: b[0] = False
                if '!' in c1 and len(set(all_vals)) != len(all_vals): b[0] = False
                if '<' in c1:
                    num_str = "".join(filter(str.isdigit, c1))
                    if num_str and sum(all_vals) >= int(num_str):
                        b[0] = False
                if '>' in c1:
                    num_str = "".join(filter(str.isdigit, c1))
                    if num_str and sum(all_vals) <= int(num_str) and is_full:
                        b[0] = False
                target = self.get_numeric_constraint(c1)
                if target is not None:
                    s = sum(all_vals)
                    if s > target or (is_full and s != target): b[0] = False
            
            # Check for region 2 (if different)
            if c2 != '-' and c1 != c2:
                all_vals = list(vals2) # copy
                all_vals.append(int(domino[1]))

                open_count = sum(1 for x,y in d2 if board[x][y] == 'X')
                is_full = (open_count == 1)

                if '=' in c2 and len(set(all_vals)) > 1: b[1] = False
                if '!' in c2 and len(set(all_vals)) != len(all_vals): b[1] = False
                if '<' in c2:
                    num_str = "".join(filter(str.isdigit, c2))
                    if num_str and sum(all_vals) >= int(num_str):
                        b[1] = False
                if '>' in c2:
                    num_str = "".join(filter(str.isdigit, c2))
                    if num_str and sum(all_vals) <= int(num_str) and is_full:
                        b[1] = False
                target = self.get_numeric_constraint(c2)
                if target is not None:
                    s = sum(all_vals)
                    if s > target or (is_full and s != target): b[1] = False
            elif c1 == c2:
                b[1] = b[0]

            return b[0] and b[1]

        # Function to place a domino on the board
        def place(board, dominoes, i, j) -> list[list[str]] | None:
            m: int = len(board[i])
            for d in dominoes:
                
                orientations = [d]
                if d[0] != d[1]:
                    orientations.append(d[::-1])

                for current_d in orientations:
                    # Horizontal placement
                    if j + 1 < m and board[i][j + 1] == 'X':
                        if check(board, current_d, i, j, i, j + 1):
                            board[i][j] = current_d[0]
                            board[i][j + 1] = current_d[1]
                            new_dominoes = dominoes[:]
                            new_dominoes.remove(d)
                            res = backtrack(board, new_dominoes)
                            if res:
                                return res
                            board[i][j] = 'X'
                            board[i][j + 1] = 'X'

                    # Vertical placement
                    if i + 1 < n and j < len(board[i + 1]) and board[i + 1][j] == 'X':
                        if check(board, current_d, i, j, i + 1, j):
                            board[i][j] = current_d[0]
                            board[i + 1][j] = current_d[1]
                            new_dominoes = dominoes[:]
                            new_dominoes.remove(d)
                            res = backtrack(board, new_dominoes)
                            if res:
                                return res
                            board[i][j] = 'X'
                            board[i + 1][j] = 'X'
            return None

        # Function to find the next empty tile on the board
        def find_next_empty(board):
            for r in range(n):
                for c in range(len(board[r])):
                    if board[r][c] == 'X':
                        return (r, c)
            return None

        # Function to backtrack and place dominoes on the board
        def backtrack(board, dominoes) -> list[list[str]] | None:
            pos = find_next_empty(board)
            if not pos:
                return board if not dominoes else None
            
            i, j = pos
            return place(board, dominoes, i, j)

        sol = backtrack(sol, self.dominoes)
        self.print_sol(sol)

        matches_file = False
        if sol:
            # Check for a corresponding solution file
            board_filename = os.path.basename(self.board_path)
            solution_filename = board_filename.replace('board-', 'solution-').replace('.pips', '.txt')
            solution_path = os.path.join('solutions', solution_filename)

            if os.path.exists(solution_path):
                with open(solution_path, 'r') as f:
                    solution_from_file = [ast.literal_eval(line.strip()) for line in f]
                
                # Convert all elements to string for consistent comparison
                sol_str = [[str(item) for item in row] for row in sol]
                solution_from_file_str = [[str(item) for item in row] for row in solution_from_file]

                if sol_str == solution_from_file_str:
                    print("\nSolution matches the one on file.")
                    matches_file = True
                else:
                    print("\nSolution does not match the one on file (but other solutions may exist).")
            else:
                print("\nNo corresponding solution file found.")

        return sol, matches_file

if __name__ == '__main__':
    game = PipGame(sys.argv[1])
    print(game)
    game.solution()

