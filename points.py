from PyQt4.QtGui import *
from math import sqrt, acos, pi, fabs

class line_pnts(object):
    def __init__(self):
        self.x = []
        self.y = []
        self.n_points = 0

class point(object):
    def __init__(self):
        self.x = 0.
        self.y = 0.

def point_scalar(a, k, res):
    res.x = a.x * k
    res.y = a.y * k


def point_add(a, b, res):
    res.x = a.x + b.x
    res.y = a.y + b.y


def points_copy_last(points, pos):
    n = points.n_points - 1

    points.x[pos] = points.x[n]
    points.y[pos] = points.y[n]

    points.n_points = pos + 1


def point_substract(a, b, res):
    res.x = a.x - b.x
    res.y = a.y - b.y

def point_assign(points, index, res):
    res.x = points.x[index]
    res.y = points.y[index]


def point_dist(a, b):
    return sqrt((a.x-b.x)*(a.x-b.x)+(a.y-b.y)*(a.y-b.y))

def point_distance(p1, p2, p):
    try:
        #return fabs( (p2.x-p1.x)*(p1.y-p.y)-(p1.x-p.x)*(p2.y-p1.y) ) / sqrt((p2.x-p1.x)*(p2.x-p1.x) + (p2.y-p1.y)*(p2.y-p1.y))
        return fabs( (p2.x-p1.x)*(p1.y-p.y)-(p1.x-p.x)*(p2.y-p1.y) ) / point_dist(p1, p2)
    except:
        return 0


#calc angle g
#A_______B
# \g)
#  \
#   \
#    C
def point_angle(p, p1, p2):
    pp1 = point()
    pp2 = point()

    pp1.x = p1.x - p.x
    pp1.y = p1.y - p.y

    pp2.x = p2.x - p.x
    pp2.y = p2.y - p.y

    pp1_len = point_dist(p, p1)
    pp2_len = point_dist(p, p2)

    return ((acos((pp1.x*pp2.x+pp1.y*pp2.y)/(pp1_len*pp2_len)))*180)/pi

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