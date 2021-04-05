from copy import deepcopy
grid = [
    [0, 1, 0, 0, 0, 0],  # x
    [0, 1, 0, 0, 0, 0],  # |  # 0 are free path whereas 1's are obstacles
    [0, 1, 0, 0, 0, 0],  # |
    [0, 1, 0, 0, 1, 0],  # |
    [0, 0, 0, 0, 1, 0],  # ---------------> y
]  # initial map (every node max branching factor (number of possible move) = 4)

"""
heuristic = [[9, 8, 7, 6, 5, 4],
             [8, 7, 6, 5, 4, 3],
             [7, 6, 5, 4, 3, 2],
             [6, 5, 4, 3, 2, 1],
             [5, 4, 3, 2, 1, 0]]"""

init = [0, 0]
goal = [len(grid) - 1, len(grid[0]) - 1]
cost = 1

# initilize the heuristic : heuristic[0:][0:] = 0
heuristic = [[0 for row in range(len(grid[0]))] for col in range(len(grid))]

# Create heuristic grid
for i in range(len(grid)):
    for j in range(len(grid[0])):
        heuristic[i][j] = abs(i - goal[0]) + abs(j - goal[1])
        if grid[i][j] == 1:
            heuristic[i][j] = 99  # added extra penalty in the heuristic map


# the actions we can take
# go up 0  # go left 1 # go down 2 # go right 3
delta = [[-1, 0], [0, -1], [1, 0], [0, 1]]


# def convertDeltaToMove(action):
#     options = {
#         0: 'up',
#         1: 'left',
#         2: 'down',
#         3: 'right',
#     }
#     convertedAction = deepcopy(action)

#     for i in range(len(action)):
#         for j in range(len(action[i])):
#             convertedAction[i][j] = options[action[i][j]]
#     return convertedAction


# function to search the path
def search(grid, init, goal, cost, heuristic):

    closed = [
        [0 for col in range(len(grid[0]))] for row in range(len(grid))
    ]  # the reference grid to note the extended node
    closed[init[0]][init[1]] = 1  # note the init as extended
    action = [
        [0 for col in range(len(grid[0]))] for row in range(len(grid))
    ]  # the action grid

    x = init[0]
    y = init[1]
    g = 0  # total cost to reach to the goal (accumulate path)
    f = g + heuristic[init[0]][init[0]]  # cost of accumulate + heuristic
    # the queue: contain the informed cost (f) to the goal, accumulate cost (g), x ,y
    cell = [[f, g, x, y]]

    found = False  # flag that is set when search is complete
    resign = False  # flag set if we can't find expand

    # Note that because the cost to move is the same no matter what the move is
    # So there is no need to keep extending other paths when we've got the goal (although f(x)<f(goal), g(x) always >=g(goal))
    while not found and not resign:
        if len(cell) == 0:  # Have extended & check all possible paths and no goal found
            return "FAIL"
        else:
            # Extend the sortest path to extend(using f as benchmark)
            cell.sort()
            cell.reverse()
            next = cell.pop()
            g = next[1]
            x = next[2]
            y = next[3]

            if x == goal[0] and y == goal[1]:  # Check if it is the goal
                found = True
            else:
                # to try out different valid actions (4 actions)
                for i in range(len(delta)):
                    x2 = x + delta[i][0]  # the suggesting move
                    y2 = y + delta[i][1]
                    # Check if the move is inside the map
                    if x2 >= 0 and x2 < len(grid) and y2 >= 0 and y2 < len(grid[0]):
                        # Check if the node is not extended yet and not an obstacle
                        if closed[x2][y2] == 0 and grid[x2][y2] == 0:
                            g2 = g + cost
                            f2 = g2 + heuristic[x2][y2]

                            # extend the "next"
                            cell.append([f2, g2, x2, y2])

                            # set closed = 1 to note that x2,y2 is already extended
                            closed[x2][y2] = 1

                            # note how to move to x2,y2
                            # delta[action[x2][y2]] is the shortest path to move from x,y -> x2,y2
                            action[x2][y2] = i

    #  A list of node to move from init -> goal
    invpath = []
    x = goal[0]
    y = goal[1]
    invpath.append([x, y])
    while x != init[0] or y != init[1]:
        # Move backward from the goal to start
        # No need to check if x2,y2 is inside the map cause we already check it when adding action
        x2 = x - delta[action[x][y]][0]
        y2 = y - delta[action[x][y]][1]

        x = x2
        y = y2

        invpath.append([x, y])

    path = deepcopy(invpath)
    path.reverse()
    print("ACTION MAP")
    for i in range(len(action)):
        print(action[i])

    return path


a = search(grid, init, goal, cost, heuristic)
for i in range(len(a)):
    print(a[i])
