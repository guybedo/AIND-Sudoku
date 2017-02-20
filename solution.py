from _collections import defaultdict
assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]


def dot(A, B):
    "Dot product of elements in A and elements in B."
    return [a + b for a, b in zip(A, B)]


boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
diag_units = [dot(rows, cols), dot(rows, reversed(cols))]
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


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
    return {
        k: v if v != '.' else '123456789'
        for k, v in zip(cross(rows, cols), grid)}


def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF':
            print(line)
    print


def difference(value1, value2):
    """remove the values of value2 from value1
    Args:
        value1(str): a set of values represented as a string
        value2(str): a set of values represented as a string
    Returns:
        a string representing the difference between the 2 sets
    """
    diff = set(list(value1)).difference(set(list(value2)))
    return ''.join(sorted(diff))


def update_other_unit_members(values, box, new_value):
    """
    for a specified box and a new value assigned to this box, update the other boxes
    in the same units by removing the new value
    Args:
        values: A sudoku in dictionary form.
        box: a box
        new_value: the new value assigned to the box
    """
    for unit in units[box]:
        for other_box in unit:
            if other_box == box:
                continue
            values[other_box] = difference(values[other_box], new_value)


def solved_boxes(values, unit):
    """
    returns the list of boxes already solved in the specified unit
    Args:
        values: A sudoku in dictionary form.
        unit: a unit
    """
    return [
        box
        for box in unit
        if len(values[box]) == 1]


def non_solved_boxes(values, unit):
    """
    returns the list of boxes not already solved in the specified unit
    Args:
        values: A sudoku in dictionary form.
        unit: a unit
    """
    return [
        box
        for box in unit
        if len(values[box]) > 1]


def assigned_values(values, unit):
    """
    returns the list of values already assigned in the specified unit
    Args:
        values: A sudoku in dictionary form.
        unit: a unit
    """
    return [
        values[box]
        for box in solved_boxes(values, unit)]


def non_assigned_values(values, unit):
    """
    returns the list of values not already assigned in the specified unit
    Args:
        values: A sudoku in dictionary form.
        unit: a unit
    """
    return list(
        set([str(i) for i in range(1, 10)])
        .difference(
            set(assigned_values(values, unit))))


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    values = dict(values)
    for unit in unitlist:
        unit_values = defaultdict(list)
        for box in unit:
            unit_values[values[box]].append(box)
        twins = [
            box
            for e in filter(
                lambda e: len(e[0]) == 2 and len(e[1]) == 2,
                unit_values.items())
            for box in e[1]]
        if len(twins) > 0:
            twin_value = values[twins[0]]
            for box in set(unit).difference(set(twins)):
                values[box] = difference(values[box], twin_value)
    return values


def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    values = dict(values)
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit, '')
    return values


def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    values = dict(values)
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def single_possibility(values):
    """
    Go through all the boxes, whenever there is a box for which there is only one common value possible across all the box's units,
    assign the value to this box, and then remove the value from other boxes in the box's units
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    values = dict(values)
    non_solved_boxes = [box for box, value in values.items() if len(value) > 1]
    for box in non_solved_boxes:
        box_units = units[box]
        box_units_non_assigned = [
            non_assigned_values(values, box_unit)
            for box_unit in box_units]
        intersection = set(box_units_non_assigned[0])
        for non_assigned in box_units_non_assigned[1:]:
            intersection = intersection.intersection(set(non_assigned))
        if len(intersection) == 1:
            values[box] = list(intersection)[0]
            for unit in box_units:
                for other_box in unit:
                    if other_box != box:
                        values[other_box] = difference(values[other_box], values[box])
    return values


def only_square(values):
    """
    Go through all the units, whenever there is a unit with 2 unsolved boxes, each box having 2 possible values,
    inspect the 2 boxes and check the assigned values in their respective units to try to reduce the space of
    possible values
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    values = dict(values)
    for unit in unitlist:
        non_solved = {
            box: values[box]
            for box in non_solved_boxes(values, unit)}
        if len(non_solved) != 2 or sum(len(value) for value in non_solved.values()) != 4:
            continue
        for box in non_solved:
            already_assigned = [
                value
                for unit in units[box]
                for value in assigned_values(values, unit)]
            values[box] = difference(
                values[box],
                already_assigned)
            if len(values[box]) == 1:
                update_other_unit_members(values, box, values[box])
                break
    return values


# defines the default strategies to be used
default_strategies = [eliminate, only_choice, naked_twins, single_possibility, only_square]


def reduce_puzzle(values, strategies=None):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input:
        values: A sudoku in dictionary form.
        strategies: list of strategies to be used, if None default_strategies will be used
    Output: The resulting sudoku in dictionary form.
    """
    strategies = strategies or default_strategies
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        for strategy in strategies:
            values = strategy(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values, strategies=None):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.
    Input:
        values: A sudoku in dictionary form.
        strategies: list of strategies to be used, if None default_strategies will be used
    Output: The resulting sudoku in dictionary form.
    """
    unsolved_values = len([box for box in values.keys() if len(values[box]) > 1])
    if unsolved_values == 0:
        return values
    values = reduce_puzzle(values, strategies)
    if not values:
        return False

    min_value = '123456789'
    min_box = None
    for box, value in values.items():
        if len(value) > 1 and len(value) <= len(min_value):
            min_value = value
            min_box = box
    if not min_box:
        return values

    for value in min_value:
        new_values = dict(values)
        new_values[min_box] = value
        result = search(new_values, strategies)
        if result:
            return result
    return False


def solve(grid, strategies=None):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        strategies: list of strategies to be used, if None default_strategies will be used
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid), strategies)

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
