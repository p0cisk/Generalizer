from builtins import object
class MATRIX(object):
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.a = []


        i = 0
        while i<rows:
            j = 0
            tmp = []
            while j<cols:
                tmp.append(0)
                j = j+1
            self.a.append(tmp)
            i = i+1

def matrix_swap_rows(x, y, m):
    i = 0
    while i < m.cols:
        t = m.a[x][i]
        m.a[x][i] = m.a[y][i]
        m.a[y][i] = t
        i = i+1

def matrix_row_scalar(row, s, m):
    i = 0
    while i < m.cols:
        m.a[row][i] = m.a[row][i]*s
        i = i+1

def matrix_row_add_multiple(ra, rb, s, m):
    i = 0
    while i < m.cols:
        m.a[ra][i] = m.a[ra][i] + m.a[rb][i]*s

        i = i+1

def matrix_inverse(a):
    res = MATRIX(a.rows, a.rows)

    i = 0

    while i < a.rows:
        res.a[i][i] = 1
        i = i+1

    n = a.rows

    i = 0
    while i < n:
        found = 0

        j = i
        while j < n:
            if a.a[j][i] != 0:
                found = 1
                matrix_swap_rows(i, j, a)
                matrix_swap_rows(i, j, res)
                break
            j = j+1

        if not found:
            return 0
        c = 1./a.a[i][i]

        matrix_row_scalar(i, c, a)
        matrix_row_scalar(i, c, res)

        j = 0
        while j < n:
            if i == j:
                j = j+1
                continue
            c = -a.a[j][i]

            if c == 0.:
                j = j+1
                continue
            matrix_row_add_multiple(j, i, c, a)
            matrix_row_add_multiple(j, i, c, res)

            j = j+1

        i = i+1

    return res

def matrix_mult(a, b):
    res = MATRIX(a.rows, a.rows)
    i = 0
    while i < a.rows:
        j = 0
        while j < b.cols:
            res.a[i][j] = 0
            k = 0
            while k < a.cols:
                res.a[i][j] = res.a[i][j] + a.a[i][k]*b.a[k][j]

                k = k+1

            j = j+1

        i = i+1


    return res
