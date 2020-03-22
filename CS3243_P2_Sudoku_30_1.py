import sys
import copy
from collections import deque

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

# Variable ordering heuristics: Most constrained variable + Most constraining variable
# Value ordering heuristics: Least constraining value
# Inference mechanisms: Arc consistency

class Sudoku(object):
    def __init__(self, puzzle):
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.var_domain, self.var_constraints, self.var_unassigned = self.csp(puzzle)

    def csp(self, puzzle):
        var_domain = {}
        var_constraints = {}
        var_unassigned = 0

        for r in xrange(9):
            for c in xrange(9):
                var_domain[(r, c)] = None
                var_constraints[(r, c)] = set()

                if puzzle[r][c] == 0:
                   var_unassigned += 1

        possible_domain = set([1, 2, 3, 4, 5, 6, 7, 8, 9])

        for var in var_domain:
            row, column = var[0], var[1]
            assigned_val = set()            
            puzzle_val = puzzle[row][column]

            for c in xrange(9):
                val = puzzle[row][c]
                var_constraints[var].add((row, c))

                if val != 0 and puzzle_val == 0:
                    assigned_val.add(val)

            for r in xrange(9):
                val = puzzle[r][column]
                var_constraints[var].add((r, column))

                if val != 0 and puzzle_val == 0:
                    assigned_val.add(val)

            subgrid_r = (row / 3) * 3
            subgrid_c = (column / 3) * 3

            for r in xrange(subgrid_r, subgrid_r + 3):
                for c in xrange(subgrid_c, subgrid_c + 3):
                    val = puzzle[r][c]
                    var_constraints[var].add((r, c))

                    if val != 0 and puzzle_val == 0:
                        assigned_val.add(val)

            var_constraints[var].remove(var)

            if puzzle_val == 0:
                var_domain[var] = possible_domain - assigned_val
            else:
                var_domain[var] = puzzle_val

        return var_domain, var_constraints, var_unassigned

    def is_complete(self, var_unassigned):
        return var_unassigned == 0

    def is_consistent(self, var, val, var_domain, var_constraints):
        return all(var_domain[constraint] != val for constraint in var_constraints[var])

    def select_unassigned_var(self, var_domain, var_constraints):
        most_constrained_var = set()
        fewest_legal_val = 9

        for var in var_domain:
            domain = var_domain[var]

            if isinstance(domain, set):
                legal_val = len(domain)

                if legal_val < fewest_legal_val:
                    most_constrained_var = set()
                    fewest_legal_val = legal_val

                if legal_val == fewest_legal_val:
                    most_constrained_var.add(var)

        most_constraining_var = None
        most_constraints = 0

        for var in most_constrained_var:
            num_constraints = 0

            for constraint in var_constraints[var]:
                if isinstance(var_domain[constraint], set):
                    num_constraints += 1

            if num_constraints >= most_constraints:
                most_constraining_var = var
                most_constraints = num_constraints

        # last var in most_constrained_var with largest num_constraints
        # may not be only var with that num_constraints
        return most_constraining_var
                
    def order_domain_val(self, var, var_domain, var_constraints):
        val_order = []

        for val in var_domain[var]:
            num_affected = 0

            for constraint in var_constraints[var]:
                if isinstance(var_domain[constraint], set):
                    if val in var_domain[constraint]:
                        num_affected += 1

            val_order.append((val, num_affected))

        val_order.sort(key = lambda c: c[1])

        return [v[0] for v in val_order]

    def revise(self, var_domain, x_i, x_j):
        revised = False
        domain_i = var_domain[x_i]
        delete = set()

        for val_x in domain_i:
            domain_j = var_domain[x_j]

            if isinstance(domain_j, set):
                if not any(val_y != val_x for val_y in domain_j):
                    delete.add(val_x)
                    revised = True
            else:
                if not domain_j != val_x:
                    delete.add(val_x)
                    revised = True

        var_domain[x_i] = domain_i - delete

        return revised

    def inference(self, var, var_domain, var_constraints):
        # queue of arcs (x_i, x_j) for all x_i which are unassigned. x_j is var.
        queue = deque()

        for constraint in var_constraints[var]:
            if isinstance(var_domain[constraint], set):
                queue.append((constraint, var))

        while queue:
            x_i, x_j = queue.popleft()

            if self.revise(var_domain, x_i, x_j):
                if len(var_domain[x_i]) == 0:
                    return False

                for x_k in var_constraints[x_i] - set([x_j]):
                    if isinstance(var_domain[x_k], set):
                        queue.append((x_k, x_i))

        return True

    def backtrack(self, var_domain, var_constraints, var_unassigned):

        if self.is_complete(var_unassigned):
            return var_domain

        var = self.select_unassigned_var(var_domain, var_constraints)

        for val in self.order_domain_val(var, var_domain, var_constraints):
            var_domain_prev = var_domain.copy()
            var_unassigned_prev = var_unassigned

            if self.is_consistent(var, val, var_domain, var_constraints):
                var_domain[var] = val
                var_unassigned -= 1
                inferences = self.inference(var, var_domain, var_constraints)

                if inferences != False:
                    result = self.backtrack(var_domain, var_constraints, var_unassigned)

                    if result != False:
                        return result

            var_domain = var_domain_prev
            var_unassigned = var_unassigned_prev

        return False

    def solve(self):
        complete_assignment = self.backtrack(self.var_domain, self.var_constraints, self.var_unassigned)

        for var in complete_assignment:
            r, c = var[0], var[1]
            self.puzzle[r][c] = complete_assignment[var]

        return self.puzzle

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
