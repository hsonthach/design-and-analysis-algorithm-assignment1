#!/usr/bin/env python3
from math import sqrt
from random import shuffle, randint
import argparse
from copy import deepcopy

# TODO: Logs


def same_column_indexes(problem_grid, i, j, N, itself=True):
    """
    A generator function that yields indexes of the elements that are in the same column as the input indexes.

    Parameters:
        - problem_grid (list)
        - i (int): Sub-grid's index.
        - j (int): Sub-grid's element index.
        - N (int)
        - itself (bool) (optional=True): Indicates whether to yield the input indexes or not.
    """

    sub_grid_column = i % N
    cell_column = j % N

    for a in range(sub_grid_column, len(problem_grid), N):
        for b in range(cell_column, len(problem_grid), N):
            if (a, b) == (i, j) and not itself:
                continue

            yield (a, b)


def same_row_indexes(problem_grid, i, j, N, itself=True):
    """
    A generator function that yields indexes of the elements that are in the same row as the input indexes.

    Parameters:
        - problem_grid (list)
        - i (int): Sub-grid's index.
        - j (int): Sub-grid's element index.
        - N (int)
        - itself (bool) (optional=True): Indicates whether to yield the input indexes or not.
    """

    sub_grid_row = int(i / N)
    cell_row = int(j / N)

    for a in range(sub_grid_row * N, sub_grid_row * N + N):
        for b in range(cell_row * N, cell_row * N + N):
            if (a, b) == (i, j) and not itself:
                continue

            yield (a, b)


def get_cells_from_indexes(grid, indexes):
    """
    A generator function that yields the values of a list of grid indexes.

    Parameters:
        - grid (list)
        - indexes (list) : e.g. [[1, 2], [3, 10]]

    Returns (list): e.g. [3, 4, 5]
    """

    for a, b in indexes:
        yield grid[a][b]


def solve(problem_grid, population_size=10, selection_rate=0.5, max_generations_count=1000, mutation_rate=0.05):
    """
    Solves a Sudoku puzzle using genetic algorithm.
    Assumes that the parameters are all valid.

    Parameters:
        - problem_grid (list): An N*N sudoku grid. See the paper ("encoding" section) to understand it's format.
        - population_size (int): The initial population size. (max number of candidates)
        - selection_rate (int) ???
        - max_generations_count (int) ???
        - mutation_rate (int) ???

    Raises:
            - Exception: The puzzle is not solvable.
    """

    # square root of the problem grid's size
    # e.g: problem_grid = 3 (size of box), -> N = 81
    N = int(sqrt(len(problem_grid)))

    def empty_grid(elem_generator=None):
        """
        Returns an empty Sudoku grid. ??? for what ?

        Parameters:
            - elem_generator (function) (optional=None): Is is used to generate initial values of the grid's elements.
              If it's not given, all grid's elements will be "None".
        """

        return [
            [
                (None if elem_generator is None else elem_generator(i, j))
                for j in range(len(problem_grid))
            ] for i in range(len(problem_grid))
        ]

    def deep_copy_grid(grid):
        """
        Returns a deep copy of the grid argument.

        Parameters:
            - grid (list)
        """

        return empty_grid(lambda i, j: grid[i][j])

    # this is done to avoid changes in the input argument
    problem_grid = deep_copy_grid(problem_grid)

    def same_box_indexes(i, j, grid, itself=True):
        """
        A generator function that yields indexes of the elements that are in the same box as the input indexes.

        Parameters:
            - i (int): Sub-grid's index.
            - j (int): Sub-grid's element index.
            - itself (bool) (optional=True): Indicates whether to yield the input indexes or not.
        """

        for k in range(len(grid)):
            if k == j and not itself:
                continue

            yield (i, k)

    def fill_predetermined_cells():
        """
        Fills some predetermined cells of the Sudoku grid (filling all safe cells) using a pencil marking method.
        Minimize the complexity of the problem

        Raises:
            - Exception: The puzzle is not solvable.
        """

        # Initialize [[1->9][1->9]...]
        track_grid = empty_grid(
            lambda *args: [val for val in range(1, len(problem_grid) + 1)])

        def pencil_mark(i, j):
            """
            Marks the value of grid[i][j] element in it's row, column and sub-grid.

            Parameters:
                - i (int): Sub-grid's index.
                - j (int): Sub-grid's element index.

            Returns: The more completed version of the grid.
            """

            # remove from same sub-grid cells
            for a, b in same_box_indexes(i, j, problem_grid, itself=False):
                try:
                    track_grid[a][b].remove(problem_grid[i][j])
                except (ValueError, AttributeError) as e:
                    pass

            # remove from same row cells
            for a, b in same_row_indexes(problem_grid, i, j, N, itself=False):
                try:
                    track_grid[a][b].remove(problem_grid[i][j])
                except (ValueError, AttributeError) as e:
                    pass

            # remove from same column cells
            for a, b in same_column_indexes(problem_grid, i, j, N, itself=False):
                try:
                    track_grid[a][b].remove(problem_grid[i][j])
                except (ValueError, AttributeError) as e:
                    pass

        # Get all possible number at any position in grid
        for i in range(len(problem_grid)):
            for j in range(len(problem_grid)):
                if problem_grid[i][j] is not None:
                    pencil_mark(i, j)

        while True:
            anything_changed = False
            '''
            Lookup the whole track_grid to see if there is
            any safe move, if there is we continue make
            track_grid more likely to have another safe move
            by continue pencil mark the found safe move.
            '''
            for i in range(len(problem_grid)):
                for j in range(len(problem_grid)):
                    if track_grid[i][j] is None:
                        continue

                    # No mark mean can't solve
                    if len(track_grid[i][j]) == 0:
                        raise Exception('The puzzle is not solvable.')
                    # Only 1 mark means safe to add to problem_grid
                    elif len(track_grid[i][j]) == 1:
                        problem_grid[i][j] = track_grid[i][j][0]
                        # continue to make track_grid more likely to have another 1 mark
                        pencil_mark(i, j)

                        # None to make sure we won't visit it twice
                        track_grid[i][j] = None

                        anything_changed = True

            if not anything_changed:
                break

        return problem_grid

    def generate_initial_survivals():
        """
        Generates an initial population of size "population_size". ???

        Returns (list): An array of candidate grids.
        """

        candidates = []
        for k in range(population_size):
            candidate = empty_grid()
            for i in range(len(problem_grid)):
                """
                    randomize the digits, then swap the fixed elements back
                    into their correct places
                """
                shuffled_sub_grid = [n for n in range(
                    1, len(problem_grid) + 1)]  # ???
                shuffle(shuffled_sub_grid)  # ???
                for j in range(len(problem_grid)):
                    if problem_grid[i][j] is not None:
                        candidate[i][j] = problem_grid[i][j]

                        shuffled_sub_grid.remove(problem_grid[i][j])

                for j in range(len(problem_grid)):
                    if candidate[i][j] is None:
                        candidate[i][j] = shuffled_sub_grid.pop()

            candidates.append(candidate)
        # The return candidates won't be the right solution (have many duplicate row)
        return candidates

    def fitness(grid):
        """
        Calculates the fitness function for a grid.

        Parameters:
            - grid (list)

        Returns (int): The value of the fitness function for the input grid.
        """

        row_duplicates_count = 0

        # calculate rows duplicates
        for a, b in same_column_indexes(grid, 0, 0, N):
            row = list(get_cells_from_indexes(
                grid, same_row_indexes(grid, a, b, N)))

            row_duplicates_count += len(row) - len(set(row))

        return row_duplicates_count

    def selection(candidates):
        """
        Returns the best portion ("selection_rate") of candidates based on their fitness function values (lower ones).

        Parameters:
            - candidates (list)

        Returns (list)
        """
        """
        The entire population of solution strings is ranked by the fitness function, and a
        certain percentage is selected for survival and reproduction. The best solutions are selected
        probabilistically, so that even lower-ranked solutions have a small but finite chance of
        reproducing. ???

        Retturn: All candidates and best fitness
        """
        # TODO: Probabilistically selection.

        index_fitness = []
        for i in range(len(candidates)-1):
            index_fitness.append(tuple([i, fitness(candidates[i])]))
        # ( index , fitnesss number)
        # sort base on fitness number
        index_fitness.sort(key=lambda elem: elem[1])

        selected_part = index_fitness[0: int(
            len(index_fitness) * selection_rate)]

        # Survival indexs  (ranged from good -> bad)
        indexes = [e[0] for e in selected_part]
        # Survivals (ranged from good -> bad) , and its best finess
        return [candidates[i] for i in indexes], selected_part[0][1]

    # Start GA
    fill_predetermined_cells()

    survivals = generate_initial_survivals()  # candidates
    best_fitness = None

    for i in range(max_generations_count):
        # Survivals (sorted) and its best finess
        survivals, best_fitness = selection(survivals)
        print("Best fitness, generation, number of survivals")
        print(best_fitness, i, len(survivals))
        if best_fitness == 0:
            break

        shuffle(survivals)  # Shuffle new survivals
        old_survivals = deepcopy(survivals)
        new_survivals = deepcopy(survivals)

        '''
        Make candidate randomly swap subgrid(column and row)
        '''
        for candidate in new_survivals[0:int(len(new_survivals) * mutation_rate)]:
            random_sub_grid = randint(0, 8)
            possible_swaps = []
            for grid_element_index in range(len(problem_grid)):
                if problem_grid[random_sub_grid][grid_element_index] is None:
                    possible_swaps.append(grid_element_index)
            if len(possible_swaps) > 1:
                shuffle(possible_swaps)
                first_index = possible_swaps.pop()
                second_index = possible_swaps.pop()
                tmp = candidate[random_sub_grid][first_index]
                candidate[random_sub_grid][first_index] = candidate[random_sub_grid][second_index]
                candidate[random_sub_grid][second_index] = tmp
        # Replace old survivals with new combined survivals
        survivals = new_survivals

        # survivals.extend(fitness_survivals)
        survivals = new_survivals + old_survivals

    return survivals[0], best_fitness


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file", help="Input file that contains Sudoku's problem.")
    parser.add_argument("-o", "--output-file", help="Output file to store problem's solution.",
                        type=str, default=None)
    parser.add_argument("-p", "--population-size", type=int, default=10000)
    parser.add_argument("-s", "--selection-rate", type=float, default=0.5)
    parser.add_argument("-m", "--max-generations-count",
                        type=int, default=1000)
    parser.add_argument("-u", "--mutation-rate", type=float, default=0.05)
    parser.add_argument("-q", "--quiet", action="store_true")
    args = parser.parse_args()

    try:
        with open(args.file, "r") as input_file:
            file_content = input_file.read()
            file_lines = file_content.split('\n')
            problem_grid = [[] for i in range(len(file_lines))]
            sqrt_n = int(sqrt(len(file_lines)))
            for j in range(len(file_lines)):
                line_values = [(int(value) if value != '-' else None)
                               for value in file_lines[j].split(' ')]
                for i in range(len(line_values)):
                    problem_grid[
                        int(i / sqrt_n) +
                        int(j / sqrt_n) * sqrt_n
                    ].append(line_values[i])
          # try:
            solution, best_fitness = solve(
                problem_grid,
                population_size=args.population_size,
                selection_rate=args.selection_rate,
                max_generations_count=args.max_generations_count,
                mutation_rate=args.mutation_rate
            )
            output_str = "Best fitness value: " + \
                str(best_fitness) + '\n\n'
            for a, b in same_column_indexes(solution, 0, 0, sqrt_n):
                row = list(get_cells_from_indexes(
                    solution, same_row_indexes(solution, a, b, sqrt_n)))

                output_str += " ".join([str(elem) for elem in row]) + '\n'
            output_str = output_str

            if args.output_file:
                with open(args.output_file, "w") as output_file:
                    output_file.write(output_str)

            if not args.quiet:
                print(output_str[:-1])

            # except:
            #     exit('Input problem is not solvable.')
    except FileNotFoundError:
        exit("Input file not found.")
