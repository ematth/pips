# Pips Solver

Implementation of the Pips game from NYT Games, including board structure, available dominoes, and checks for available solutions.

Currently the board and dominoes can be set up and printed out. Future plans include:

- [] Color-coding solution dominoes, (as opposed to just printing the locations of numbers)

- Generating puzzles from scratch
    - [] From a set of dominoes
    - [] From a starting board shape (w/ or w/o contraints)

- [] Potential GPU optimization? (i.e. can we get to <5 seconds/puzzle?)

- [x] 100% solve rate on NYTGames puzzles, <20 seconds/puzzle.

- [x] Reimplementing as a graph structure

- ~~[x] Potentially refining the `.pips` file format?~~

- [x] Webscrape daily NYT pips puzzles for daily testing

- [x] Iteratively placing dominoes to fill the given board
- [x] Recursively placing dominoes to solve the board, *given tile constraints.*
- [x] Validating whether or not a board is *solveable* with given dominoes:
    - Are all dominoes placeable?
    - Are any tiles empty once all dominoes are placed?
    - Do all dominoes meet tile constraints, (i.e. the board has a solution) ?


## Code Files

- `pips.py`: (9/18/2025) handles all logic for solution solving. The high-level method is a standard backtracking problem, where domino orientations and placements are backtracked to determine a solution that uses every domino. The low-level method uses Breadth-First Search (BFS) to find all neighboring tiles whose constraint affects the domino currently being placed. This file can be called with `python pips.py boards/board#.pips` to return the solution of a given board.

- `pips2.py`: (10/18/2025) a new graph-based implementation for solving Pips puzzles. This code converts JSON files directly into graphs with nodes and edges, which saves on memory.
For reference, `pips.py` relies on puzzles being left-aligned in order to reduce the number of additional tiles needed to represent certain tiles being positioned farther to the right.

- `pips3.py`: (10/18/2025) almost identical to `pips2.py` in functionality, but uses the `multiprocessing` package to run multiple randomly-seeded search attempts on a puzzle. 
This addition is overkill on easy and medium puzzles, but due to hard puzzles being significantly larger and more complex, running multiple attempts in parallel speeds up the overall solve time.
This change is what allows for hard puzzles to maintain a <15 second/puzzle solve time.

- `all.py`: Solves all boards in the `boards_json` directory and returns each solution.

- `nytgames.py`: imports the easy, medium, and hard boards from NYTGames as a specified date. The farthest date to check is 2025-07-05 according to comments online.

- `fetch_games.sh`: performs the import script for all dates in a specified range.


## ~~Puzzle File Format (.pips)~~

> the .pips puzzle format is now OUTDATED since I now convert the puzzles directly to graph representation from JSON.

Boards and dominoes are stored under `boards/board#.pips`, where the first row of the .pips file contains the list of dominoes, and remaining rows describe the board. Every two elements of the header represent a single domino, despite not being grouped that way.

For the boards, there is some vocab to describe the state of each tile:

- An empty element `''` -> a non-tile where a domino cannot be placed.
These are used to left-align rows of the board, if necessary.
- `-` -> Empty region: no conditions apply, dots in it can be any number.
- `=` -> dots in this region must all be the same number.
- `!` -> dots in this region must all be different numbers.
- `#` -> dots must sum to this number.
- `>#` -> dots must sum to more than this number.
- `<#` -> dots must sum to less than this number.
- Any of these patterns except for `''` and `-` can be suffixed by a capital letter 'A' through 'Z', representing a unique region. For example, the row `[=A, =A, =B, =B]` is two separate regions with the `=` constraint. 

Other details:
- Rows can have varying sizes, (small rows are not formatted with extra `''` tiles to right-align with the largest row on the board.)
- A simple check that `num_tiles == num_dominoes * 2` is done in case the board is not solveable. This is **not** a complete board validation, as certain shapes of tiles are not solveable with two-wide dominoes.
- For each row of the .pips file, the last element does **not** have an end comma because this unintentionally extends the length of the row by one. 