from itertools import chain

assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# Add additional diagonal requirement for 2 diagonal units
diag_units = [ [p[0]+p[1] for p in list(zip(rows, cols))] , [p[0]+p[1] for p in list(zip(rows, reversed(cols)))] ]

unitlist = row_units + column_units + square_units + diag_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def _naked_twins_helper(values):
    # Find 2 boxes in the same unit that
    # has the same 2 possible values
    # Eliminate these 2 values from all other peers in the unit
    solution = values.copy()

    for unit in unitlist:
        # Is there any pair of boxes with the same 2 possible values in this unit?
        # Could be more than 1 pair
        # Potential pair
        pot_pair = [box for box in unit if len(solution[box]) == 2]
        # Naked Pair, all pairs must be mutually exclusive
        naked_pair = []

        pot_pair2 = pot_pair.copy()
        for box1 in pot_pair:
            pot_pair2.remove(box1)
            for box2 in pot_pair2:
                if solution[box1] == solution[box2]:
                    naked_pair.append((box1, box2))

        solved_box = [box for box in unit if len(solution[box]) == 1]
        # Peers to eliminate from
        peers_to_eliminate = list(set(unit) - set(chain(*naked_pair)) - set(solved_box))

        # Eliminate from all peers
        for pair in naked_pair:
            value_to_eliminate = set(solution[pair[0]])
            for peer in peers_to_eliminate:
                new_value = set(solution[peer]).difference(value_to_eliminate) 
                new_value = list(new_value)
                new_value.sort() # Set new value to the right format
                solution = assign_value(solution, peer, ''.join(new_value))
    return solution

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = _naked_twins_helper(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return None
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def reduce_puzzle(values):
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return None
    return values

def search(values):
    # Using depth-first search
    #Recurrence relation base case
    values = reduce_puzzle(values)

    if values is None:
        return False
    if all(len(values[box]) == 1 for box in values.keys()):
        return values # solved
    
    # Choose the box that has smallest number of possibilities
    # to perform DFS
    min_length, min_box = min((len(values[box]), box) for box in values.keys() if len(values[box]) > 1)

    for node in values[min_box]:
        new_values = values.copy()
        new_values = assign_value(new_values, min_box, node)
        new_values = search(new_values)
        if new_values:
            return new_values

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    board = grid_values(grid)
    solution = search(board)

    return solution

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
