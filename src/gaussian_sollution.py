import sympy as sp
import numpy as np


# ======================================================================
# gaussian elimination algorithm

# form augmented matrix
def matrix_representation(system, sym):
    # extract equation coefficients and constant
    a, b = sp.linear_eq_to_matrix(system, sym)

    # insert right hand size values into coefficients matrix
    return np.asarray(a.col_insert(len(sym), b), dtype=np.float32)


# write rows in row echelon form
def upper_triangular(m):
    # move all zeros to bottom of matrix
    m = np.concatenate((m[np.any(m != 0, axis=1)], m[np.all(m == 0, axis=1)]), axis=0)

    # iterate over matrix rows
    for i in range(0, m.shape[0]):

        # initialize row-swap iterator
        j = 1

        # select pivot value
        pivot = m[i][i]

        # find next non-zero leading coefficient
        while pivot == 0 and i + j < m.shape[0]:
            # perform row swap operation
            m[[i, i + j]] = m[[i + j, i]]

            # increment row-swap iterator
            j += 1

            # get new pivot
            pivot = m[i][i]

        # if pivot is zero, remaining rows are all zeros
        if pivot == 0:
            # return upper triangular matrix
            return m

        # extract row
        row = m[i]

        # get 1 along the diagonal
        m[i] = row / pivot

        # iterate over remaining rows
        for j in range(i + 1, m.shape[0]):
            # subtract current row from remaining rows
            m[j] = m[j] - m[i] * m[j][i]

    # return upper triangular matrix
    return m


def back_substitution(m, sym):
    # symbolic variable index
    for i, row in reversed(list(enumerate(m))):
        # create symbolic equation
        eqn = -m[i][-1]
        for j in range(len(sym)):
            eqn += sym[j] * row[j]

        # solve symbolic expression and store variable
        sym[i] = sp.solve(eqn, sym[i])[0]

    # return list of evaluated variables
    return sym


def validate_solution(system, solutions, tolerance=1e-6):
    # iterate over each equation
    for eqn in system:
        # assert equation is solved
        assert eqn.subs(solutions) < tolerance


# solve system using numpy built in functions
def lineal_solve(system, sym):
    # convert list of equations to matrix form
    m, c = sp.linear_eq_to_matrix(system, sym)

    # form augmented matrix - convert sympy matrices to numpy arrays and concatenate
    m, c = np.asarray(m, dtype=np.float32), np.asarray(c, dtype=np.float32)

    # solve system of equations
    return np.linalg.solve(m, c)


def final_res(formula):

    final_str = ''

    # symbolic variables
    x1, x2, x3 = sp.symbols('x1 x2 x3')
    symbolic_vars = [x1, x2, x3]

    # define system of equations
    equations = list(eval(formula))

    # display equations
    final_str += str([eqn for eqn in equations])

    # obtain augmented matrix representation
    augmented_matrix = matrix_representation(system=equations, sym=symbolic_vars)
    final_str += str('\naugmented matrix:\n' + str(augmented_matrix))

    # generate upper triangular matrix form
    upper_triangular_matrix = upper_triangular(augmented_matrix)
    final_str += str('\nupper triangular matrix:\n' + str(upper_triangular_matrix))

    # remove zero rows
    back_sub_matrix = upper_triangular_matrix[np.any(upper_triangular_matrix != 0, axis=1)]

    # assert that number of rows in matrix equals number of unknown variables
    if back_sub_matrix.shape[0] != len(symbolic_vars):
        final_str += 'dependent system. infinite number of solutions.'
    elif not np.any(back_sub_matrix[-1][:len(symbolic_vars)]) or \
            (back_sub_matrix[0][0] == back_sub_matrix[1][0] == back_sub_matrix[2][0] == 0) or \
            (back_sub_matrix[0][1] == back_sub_matrix[1][1] == back_sub_matrix[2][1] == 0) or \
            (back_sub_matrix[0][2] == back_sub_matrix[1][2] == back_sub_matrix[2][2] == 0):
        final_str += '\n\ninconsistent system. no solution.'
    else:
        # back substitute to solve for variables
        numeric_solution = back_substitution(back_sub_matrix, symbolic_vars)
        final_str += f'\n\nsolutions:\n{numeric_solution}'

    return final_str
