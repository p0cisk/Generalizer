from PyQt4.QtGui import *
from math import sqrt

class line_pnts(object):
    def __init__(self):
        self.x = []
        self.y = []
        self.n_points = 0

class point(object):
    def __init__(self):
        self.x = 0.
        self.y = 0.


def point_assign(points, index, res):
    res.x = points.x[index]
    res.y = points.y[index]


def point_dist(a, b):
    return sqrt((a.x-b.x)*(a.x-b.x)+(a.y-b.y)*(a.y-b.y))

def point_add_new(points, index, res):
    res.x.append(points.x[index])
    res.y.append(points.y[index])

    res.n_points = len(res.x)


def Vect_new_line_struct(l):
    res = line_pnts()

    for i in l:
        res.x.append(i[0])
        res.y.append(i[1])
    res.n_points = len(l)

    return res