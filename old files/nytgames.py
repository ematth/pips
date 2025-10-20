import requests
import json
import sys
from collections import defaultdict
import os

DATE: str = sys.argv[1] if len(sys.argv) > 1 else '2025-09-16'
URL: str = f'https://www.nytimes.com/svc/pips/v1/{DATE}.json'
HTML: str = requests.get(URL).text
DATA = json.loads(HTML)

SOLUTIONS_DIR = 'solutions'
if not os.path.exists(SOLUTIONS_DIR):
    os.makedirs(SOLUTIONS_DIR)

for d in ['easy', 'medium', 'hard']:
    # --- Generate Board File ---
    with open(f'boards/board-{DATE}-{d}.pips', 'w') as f:
        dominoes = DATA[d]['dominoes']
        domino_line = ', '.join([str(item) for sublist in dominoes for item in sublist])
        f.write(domino_line + '\n')
        regions = DATA[d]['regions']
        # Pre-process regions to add IDs and initial constraint strings
        for i, region in enumerate(regions):
            region['id'] = i
            constraint = ''
            if region['type'] == 'equals':
                constraint = '='
            elif region['type'] == 'sum':
                constraint = str(region['target'])
            elif region['type'] == 'greater':
                constraint = f">{region['target']}"
            elif region['type'] == 'less':
                constraint = f"<{region['target']}"
            elif region['type'] == 'empty':
                constraint = '-'
            region['constraint_str'] = constraint
        # Map coordinates to regions for efficient adjacency checking
        coord_to_region = {
            (r, c): region 
            for region in regions 
            for r, c in region['indices']
        }
        # Build adjacency graph for regions with the same constraint
        adj = defaultdict(set)
        for region in regions:
            if region['constraint_str'] == '-':
                continue
            for r, c in region['indices']:
                for dr, dc in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                    neighbor_coord = (r + dr, c + dc)
                    if neighbor_coord in coord_to_region:
                        neighbor_region = coord_to_region[neighbor_coord]
                        if neighbor_region['id'] != region['id'] and neighbor_region['constraint_str'] == region['constraint_str']:
                            adj[region['id']].add(neighbor_region['id'])
                            adj[neighbor_region['id']].add(region['id'])
        # Find connected components and assign unique letters
        capital_letter_ord = ord('A')
        visited = set()
        region_map = {r['id']: r for r in regions}
        for region_id in region_map:
            if region_id not in visited and region_id in adj:
                component_ids = []
                q = [region_id]
                visited.add(region_id)
                head = 0
                while head < len(q):
                    curr_id = q[head]; head += 1
                    component_ids.append(curr_id)
                    for neighbor_id in adj[curr_id]:
                        if neighbor_id not in visited:
                            visited.add(neighbor_id)
                            q.append(neighbor_id)
                if len(component_ids) > 1:
                    for comp_id in component_ids:
                        suffix = chr(capital_letter_ord)
                        region_map[comp_id]['constraint_str'] += suffix
                        capital_letter_ord += 1
        board = []
        for region in regions:
            for r, c in region['indices']:
                while len(board) <= r:
                    board.append([])
                while len(board[r]) <= c:
                    board[r].append('')
                board[r][c] = region['constraint_str']
        for row in board:
            f.write(','.join(row) + '\n')

    # --- Generate Solution File ---
    with open(os.path.join(SOLUTIONS_DIR, f'solution-{DATE}-{d}.txt'), 'w') as f:
        regions = DATA[d]['regions']
        dominoes = DATA[d]['dominoes']
        solution_placements = DATA[d]['solution']
        # 1. Build the board with the correct shape and placeholders
        sol_board = []
        playable_coords = set()
        max_r, max_c = 0, 0
        for region in regions:
            for r, c in region['indices']:
                playable_coords.add((r, c))
                if r > max_r: max_r = r
                if c > max_c: max_c = c
        for r in range(max_r + 1):
            row = []
            max_c_for_row = -1
            for pr, pc in playable_coords:
                if pr == r and pc > max_c_for_row:
                    max_c_for_row = pc
            if max_c_for_row > -1:
                for c in range(max_c_for_row + 1):
                    row.append('_')
            sol_board.append(row)
        # 2. Place dominoes onto the board
        for i, placement in enumerate(solution_placements):
            domino = dominoes[i]
            (r1, c1), (r2, c2) = placement
            sol_board[r1][c1] = str(domino[0])
            sol_board[r2][c2] = str(domino[1])
        # 3. Write the final board to the file
        for row in sol_board:
            f.write(str(row) + '\n')