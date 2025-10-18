import json, sys

"""
Attempt to construct and solve boards from the provided JSON files.
This is the format used by the NYT Games API, and going from this format directly to a graph structure will make the solving process easier.
"""

class Graph:

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
        self.construct_nodes(data, difficulty)
        self.construct_edges()
        self.dominoes = data[difficulty]['dominoes']

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
                    row_str += " .   "
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

    def solve(self):
        """Solve the puzzle by placing dominoes on the graph."""
        num_tiles = len(self.nodes)
        if num_tiles % 2 != 0:
            print("Invalid game: number of nodes is not even")
            return None
        
        # Create a dictionary to quickly find nodes by position
        pos_to_node = {tuple(node.p): node for node in self.nodes}
        
        # Initialize all node values to None (unplaced)
        for node in self.nodes:
            node.value = None
        
        def find_region(node):
            """Find all nodes in the same region as the given node."""
            if node.type == 'empty':
                return [node]
            
            visited = set([tuple(node.p)])
            queue = [node]
            region = [node]
            
            head = 0
            while head < len(queue):
                current = queue[head]
                head += 1
                
                for neighbor in current.neighbors:
                    pos_tuple = tuple(neighbor.p)
                    if pos_tuple not in visited:
                        # Nodes are in the same region if they have the same type and target
                        if neighbor.type == current.type and neighbor.target == current.target:
                            visited.add(pos_tuple)
                            queue.append(neighbor)
                            region.append(neighbor)
            
            return region
        
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
            """Find the next node without a value assigned."""
            for node in self.nodes:
                if node.value is None:
                    return node
            return None
        
        def place_domino(node, remaining_dominoes):
            """Try to place dominoes starting from the given node."""
            for domino in remaining_dominoes:
                # Try both orientations if values are different
                orientations = [domino]
                if domino[0] != domino[1]:
                    orientations.append(domino[::-1])
                
                for current_domino in orientations:
                    # Try placing domino on each neighbor
                    for neighbor in node.neighbors:
                        if neighbor.value is None:  # Neighbor is empty
                            # Check if placement is valid
                            if check_domino_placement(node, neighbor, current_domino):
                                # Place the domino
                                node.value = int(current_domino[0])
                                neighbor.value = int(current_domino[1])
                                
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
        
        def backtrack(remaining_dominoes):
            """Backtrack to find a valid solution."""
            # Find next empty node
            node = find_next_empty()
            
            # If no empty nodes, check if all dominoes are placed
            if node is None:
                return len(remaining_dominoes) == 0
            
            # Try placing a domino at this node
            return place_domino(node, remaining_dominoes)
        
        # Start backtracking with all dominoes
        success = backtrack(self.dominoes)
        
        if success:
            print("✅")
            return True
        else:
            print("❌")
            return False

# ------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    date = sys.argv[1] if len(sys.argv) > 1 else '2025-10-02'
    difficulty = sys.argv[2] if len(sys.argv) > 2 else 'easy'
    with open(f'boards_json/{date}.json', 'r') as f:
        data = json.load(f)

    G = Graph(data, difficulty)
    print("Initial board:")
    G.visualize()
    print(f"Dominoes to place: {G.dominoes}\n")
    
    G.solve()
    
    print("\nSolved board:")
    G.visualize()
    