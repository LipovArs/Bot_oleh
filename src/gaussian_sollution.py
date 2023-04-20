import sympy as sp
import numpy as np


# ======================================================================
# gaussian elimination algorithm


# form augmented matrix
def matrix_representation(system, syms):
    # extract equation coefficients and constant
    a, b = sp.linear_eq_to_matrix(system, syms)

    # insert right hand size values into coefficients matrix
    return np.asarray(a.col_insert(len(syms), b), dtype=np.float32)


# write rows in row echelon form
def upper_triangular(M):
    # move all zeros to buttom of matrix
    M = np.concatenate((M[np.any(M != 0, axis=1)], M[np.all(M == 0, axis=1)]), axis=0)

    # iterate over matrix rows
    for i in range(0, M.shape[0]):

        # initialize row-swap iterator
        j = 1

        # select pivot value
        pivot = M[i][i]

        # find next non-zero leading coefficient
        while pivot == 0 and i + j < M.shape[0]:
            # perform row swap operation
            M[[i, i + j]] = M[[i + j, i]]

            # incrememnt row-swap iterator
            j += 1

            # get new pivot
            pivot = M[i][i]

        # if pivot is zero, remaining rows are all zeros
        if pivot == 0:
            # return upper triangular matrix
            return M

        # extract row
        row = M[i]

        # get 1 along the diagonal
        M[i] = row / pivot

        # iterate over remaining rows
        for j in range(i + 1, M.shape[0]):
            # subtract current row from remaining rows
            M[j] = M[j] - M[i] * M[j][i]

    # return upper triangular matrix
    return M


def backsubstitution(M, syms):
    # symbolic variable index
    for i, row in reversed(list(enumerate(M))):
        # create symbolic equation
        eqn = -M[i][-1]
        for j in range(len(syms)):
            eqn += syms[j] * row[j]

        # solve symbolic expression and store variable
        syms[i] = sp.solve(eqn, syms[i])[0]

    # return list of evaluated variables
    return syms


def validate_solution(system, solutions, tolerance=1e-6):
    # iterate over each equation
    for eqn in system:
        # assert equation is solved
        assert eqn.subs(solutions) < tolerance


# solve system using numpy built in functions
def linalg_solve(system, syms):
    # convert list of equations to matrix form
    M, c = sp.linear_eq_to_matrix(system, syms)

    # form augmented matrix - convert sympy matrices to numpy arrays and concatenate
    M, c = np.asarray(M, dtype=np.float32), np.asarray(c, dtype=np.float32)

    # solve system of equations
    return np.linalg.solve(M, c)


def final_res(formula):

    final_str = ''

    # symbolic variables
    x1, x2, x3 = sp.symbols('x1 x2 x3')
    symbolic_vars = [x1, x2, x3]

    # define system of equations
    equations = list(eval(formula))

    # display equations
    final_str = str([eqn for eqn in equations])

    # obtain augmented matrix representation
    augmented_matrix = matrix_representation(system=equations, syms=symbolic_vars)
    final_str += str('\naugmented matrix:\n' + str(augmented_matrix))

    # generate upper triangular matrix form
    upper_triangular_matrix = upper_triangular(augmented_matrix)
    final_str += str('\nupper triangular matrix:\n' + str(upper_triangular_matrix))

    # remove zero rows
    backsub_matrix = upper_triangular_matrix[np.any(upper_triangular_matrix != 0, axis=1)]

    # initialise numerical solution
    numeric_solution = np.array([0., 0., 0.])

    # assert that number of rows in matrix equals number of unknown variables
    if backsub_matrix.shape[0] != len(symbolic_vars):
        final_str += ('dependent system. infinite number of solutions')
    elif not np.any(backsub_matrix[-1][:len(symbolic_vars)]):
        final_str += ('inconsistent system. no solution..')
    else:
        # backsubstitute to solve for variables
        numeric_solution = backsubstitution(backsub_matrix, symbolic_vars)
        final_str += (f'\nsolutions:\n{numeric_solution}')

    return final_str
