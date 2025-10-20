import json, sys, time, random
from multiprocessing import Process, Queue, cpu_count

"""
Attempt to construct and solve boards from the provided JSON files.
Compared to pips2.py, this version uses multiprocessing to attempt multiple deep searches in parallel.
This SIGNIFICANTLY improves the solve rate for hard puzzles, and what allows it to use as much time as needed for medium puzzles.
"""

class GraphMultiProcess:

    class Node:
        def __init__(self, point, _type = None, target = None):
            self.p = point
            self.type = _type
            self.target = target
            self.neighbors = []
            self.value = None

        def __repr__(self) -> str:
            return f"Node(point={self.p}, type={self.type}, target={self.target}, neighbors={[n.p for n in self.neighbors]})"

    def __init__(self, data, difficulty = 'easy'):
        self.nodes = []
        self.difficulty_data = data[difficulty]  # Store for region precomputation
        self.construct_nodes(data, difficulty)
        self.construct_edges()
        self.dominoes = data[difficulty]['dominoes']
        self.node_to_region = {}  # Cache: maps each node to its region
        self._precompute_regions()

    def __repr__(self) -> str:
        res: str = ''
        for n in self.nodes:
            res += str(n.__repr__()) + '\n'
        return res

    def construct_nodes(self, data, difficulty = 'easy'):
        for r in data[difficulty]['regions']:
            for i in r['indices']:
                self.nodes.append(self.Node(i, (r['type'] if 'type' in r else None), (r['target'] if 'target' in r else None)))
        return self.nodes

    def construct_edges(self):
        # iterate through all nodes and add edges to neighbors
        for node in self.nodes:
            for neighbor in self.nodes:
                dx = abs(node.p[0] - neighbor.p[0])
                dy = abs(node.p[1] - neighbor.p[1])
                if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
                    node.neighbors.append(neighbor)
        return self.nodes
    
    def _precompute_regions(self):
        """Pre-compute all regions once during initialization using JSON definitions."""
        # Create a position-to-node mapping for quick lookup
        pos_to_node = {tuple(node.p): node for node in self.nodes}
        
        # Use the explicit region definitions from the JSON
        for region_def in self.difficulty_data['regions']:
            # Get all nodes in this region
            region_nodes = []
            for pos in region_def['indices']:
                pos_tuple = tuple(pos)
                if pos_tuple in pos_to_node:
                    region_nodes.append(pos_to_node[pos_tuple])
            
            # Map each node in this region to the region list
            for node in region_nodes:
                self.node_to_region[tuple(node.p)] = region_nodes

    def visualize(self):
        visual_dict = {'unequal': '!', 'equals': '=', 'less': '<', 'greater': '>', 'empty': '_', 'sum': '+'}
        
        if not self.nodes:
            print("No nodes to visualize")
            return
        
        # Find the bounds of the grid
        min_row = min(node.p[0] for node in self.nodes)
        max_row = max(node.p[0] for node in self.nodes)
        min_col = min(node.p[1] for node in self.nodes)
        max_col = max(node.p[1] for node in self.nodes)
        
        # Create a grid filled with None
        grid = [[None for _ in range(max_col - min_col + 1)] for _ in range(max_row - min_row + 1)]
        
        # Place nodes in the grid
        for node in self.nodes:
            row = node.p[0] - min_row
            col = node.p[1] - min_col
            grid[row][col] = node
        
        # Print the grid
        for row in grid:
            row_str = ""
            for cell in row:
                if cell is None:
                    row_str += "     "
                else:
                    # If the cell has a value (solved), show it instead
                    if cell.value is not None:
                        row_str += f" {cell.value}   "
                    else:
                        # Format: symbol followed by target (if exists)
                        type_symbol = visual_dict.get(cell.type, '?')
                        if cell.target is not None:
                            row_str += f" {type_symbol}{cell.target:<2} "
                        else:
                            row_str += f" {type_symbol}   "
            print(row_str)
        print()

# ------------------------------------------------------------------------------------------------

    def solve(self, timeout=60, max_attempts=7, use_parallel=True):
        """Solve the puzzle by placing dominoes on the graph.
        
        Args:
            timeout: Maximum time in seconds to attempt solving (default: 60)
            max_attempts: Number of random attempts to try (default: 7)
            use_parallel: Use parallel processing for attempts (default: True)
            
        Returns:
            True if solved, False if failed, None if timeout
        """
        if use_parallel and max_attempts > 1:
            return self._solve_parallel(timeout, max_attempts)
        else:
            return self._solve_sequential(timeout, max_attempts)
    
    def _apply_solution(self, solution):
        """Apply a solution dictionary to the graph nodes."""
        for node in self.nodes:
            key = tuple(node.p)
            if key in solution:
                node.value = solution[key]
    
    def _solve_parallel(self, timeout, max_attempts):
        """Solve using parallel processes for multiple attempts."""
        overall_start = time.time()
        
        # Use up to 4 processes or max_attempts, whichever is smaller
        num_processes = min(max_attempts, cpu_count(), 4)
        
        # Create a queue to collect results
        result_queue = Queue()
        processes = []
        
        # Start parallel attempts
        for attempt in range(num_processes):
            p = Process(target=self._solve_attempt_worker, 
                       args=(attempt, timeout, result_queue))
            p.start()
            processes.append(p)
        
        # Wait for first success or all to finish
        solution_data = None
        while time.time() - overall_start < timeout:
            # Check if any process has found a solution
            if not result_queue.empty():
                result, solution = result_queue.get()
                if result is True:
                    solution_data = solution
                    break
            
            # Check if all processes are done
            if all(not p.is_alive() for p in processes):
                break
            
            time.sleep(0.01)  # Small sleep to avoid busy waiting
        
        # Terminate remaining processes
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join(timeout=0.1)
        
        # If we found a solution in the queue, apply it and return
        if solution_data:
            self._apply_solution(solution_data)
            return True
        
        # Check queue one more time for any late results
        while not result_queue.empty():
            result, solution = result_queue.get()
            if result is True:
                self._apply_solution(solution)
                return True
        
        return None  # Timeout or all failed
    
    def _solve_attempt_worker(self, attempt_num, timeout, result_queue):
        """Worker function for parallel solving attempts."""
        try:
            # Set unique random seed
            random.seed(attempt_num * 1000 + len(self.nodes))
            
            # Try solving
            result = self._solve_once(timeout)
            
            # If solved, serialize and return the solution
            if result is True:
                solution = {tuple(node.p): node.value for node in self.nodes}
                result_queue.put((True, solution))
            else:
                result_queue.put((result if result is not None else False, None))
        except Exception:
            result_queue.put((False, None))
    
    def _solve_sequential(self, timeout, max_attempts):
        """Original sequential solving (fallback)."""
        overall_start = time.time()
        
        for attempt in range(max_attempts):
            if time.time() - overall_start >= timeout:
                return None
            
            random.seed(attempt * 1000 + len(self.nodes))
            
            time_per_attempt = (timeout - (time.time() - overall_start)) / (max_attempts - attempt)
            remaining_time = min(timeout - (time.time() - overall_start), time_per_attempt * 1.5)
            
            result = self._solve_once(remaining_time)
            
            if result is True:
                return True
        
        return None
    
    def _solve_once(self, timeout):
        """Single solve attempt with given timeout using advanced constraint propagation."""
        num_tiles = len(self.nodes)
        if num_tiles % 2 != 0:
            return None
        
        # Initialize all node values to None (unplaced)
        for node in self.nodes:
            node.value = None
        
        # Track start time for timeout
        start_time = time.time()
        timed_out = [False]  # Use list to allow modification in nested functions
        
        # Pre-compute node degrees (number of neighbors) for MRV heuristic
        node_degrees = {tuple(node.p): len(node.neighbors) for node in self.nodes}
        
        def find_region(node):
            """Find all nodes in the same region as the given node (using precomputed cache)."""
            return self.node_to_region[tuple(node.p)]
        
        def check_constraints(node, domino_value, region_nodes):
            """Check if placing a domino value satisfies the region's constraints."""
            # Get all placed values in the region
            placed_values = [n.value for n in region_nodes if n.value is not None]
            all_values = placed_values + [domino_value]
            
            # Count how many nodes in the region are still empty
            empty_count = sum(1 for n in region_nodes if n.value is None)
            is_full = (empty_count == 1)  # Will be full after placing this value
            
            # Check constraints based on type
            if node.type == 'empty':
                return True
            
            if node.type == 'equals':
                if len(set(all_values)) > 1:
                    return False
            
            if node.type == 'unequal':
                if len(set(all_values)) != len(all_values):
                    return False
            
            if node.type == 'less':
                if node.target is not None and sum(all_values) >= node.target:
                    return False
            
            if node.type == 'greater':
                if node.target is not None and is_full and sum(all_values) <= node.target:
                    return False
            
            if node.type == 'sum':
                if node.target is not None:
                    s = sum(all_values)
                    if s > node.target or (is_full and s != node.target):
                        return False
            
            return True
        
        def check_domino_placement(node1, node2, domino):
            """Check if a domino can be placed at two nodes."""
            region1 = find_region(node1)
            region2 = find_region(node2)
            
            # Check first position
            if not check_constraints(node1, int(domino[0]), region1):
                return False
            
            # Check second position
            if not check_constraints(node2, int(domino[1]), region2):
                return False
            
            return True
        
        def find_next_empty():
            """Find the next node using MRV heuristic (most constrained first)."""
            best_node = None
            min_empty_neighbors = float('inf')
            
            # Quick scan for nodes with no empty neighbors (immediate fail)
            for node in self.nodes:
                if node.value is None:
                    empty_count = sum(1 for n in node.neighbors if n.value is None)
                    
                    # If node has no empty neighbors, it's a dead end - return immediately
                    if empty_count == 0:
                        return node
                    
                    # Choose node with fewest empty neighbors (most constrained)
                    if empty_count < min_empty_neighbors:
                        min_empty_neighbors = empty_count
                        best_node = node
            
            return best_node
        
        def has_dead_end():
            """Check if any empty node has no valid neighbors (dead end detection)."""
            for node in self.nodes:
                if node.value is None:
                    empty_neighbors = sum(1 for n in node.neighbors if n.value is None)
                    if empty_neighbors == 0:
                        return True
            return False
        
        def place_domino(node, remaining_dominoes):
            """Try to place dominoes with constraint propagation and pruning."""
            # Sort neighbors by degree (prefer neighbors with fewer options)
            empty_neighbors = [n for n in node.neighbors if n.value is None]
            if not empty_neighbors:
                return False  # Dead end
            
            # Sort by number of empty neighbors (prefer more constrained)
            empty_neighbors.sort(key=lambda n: sum(1 for x in n.neighbors if x.value is None))
            
            # Simple randomization - avoid expensive priority calculation
            dominoes_to_try = remaining_dominoes[:]
            random.shuffle(dominoes_to_try)
            
            for domino in dominoes_to_try:
                # Try both orientations if values are different
                orientations = [domino]
                if domino[0] != domino[1]:
                    orientations.append(domino[::-1])
                
                for current_domino in orientations:
                    # Try placing domino on sorted neighbors
                    for neighbor in empty_neighbors:
                        # Check if placement is valid
                        if check_domino_placement(node, neighbor, current_domino):
                            # Place the domino
                            node.value = int(current_domino[0])
                            neighbor.value = int(current_domino[1])
                            
                            # Forward checking: did we create a dead end?
                            if not has_dead_end():
                                # Remove domino from available dominoes
                                new_dominoes = remaining_dominoes[:]
                                new_dominoes.remove(domino)
                                
                                # Backtrack
                                result = backtrack(new_dominoes)
                                if result:
                                    return True
                            
                            # Undo placement
                            node.value = None
                            neighbor.value = None
            
            return False
        
        # Timeout check counter for efficiency
        backtrack_calls = [0]
        
        def backtrack(remaining_dominoes):
            """Backtrack to find a valid solution."""
            # Check timeout every 200 calls (more efficient)
            backtrack_calls[0] += 1
            if backtrack_calls[0] % 200 == 0:
                if time.time() - start_time > timeout:
                    timed_out[0] = True
                    return False
            
            # Find next empty node
            node = find_next_empty()
            
            # If no empty nodes, check if all dominoes are placed
            if node is None:
                return len(remaining_dominoes) == 0
            
            # Try placing a domino at this node
            return place_domino(node, remaining_dominoes)
        
        # Start backtracking with all dominoes
        success = backtrack(self.dominoes)
        
        # Return None if timed out, otherwise return success status
        if timed_out[0]:
            return None
        return success
        
        # if success:
        #     #print("✅")
        #     return True
        # else:
        #     #print("❌")
        #     return False

# ------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    date = sys.argv[1] if len(sys.argv) > 1 else '2025-10-02'
    difficulty = sys.argv[2] if len(sys.argv) > 2 else 'easy'
    with open(f'boards_json/{date}.json', 'r') as f:
        data = json.load(f)

    G = GraphMultiProcess(data, difficulty)
    print("Initial board:")
    G.visualize()
    print(f"Dominoes to place: {G.dominoes}\n")
    
    G.solve()
    
    print("\nSolved board:")
    G.visualize()
    