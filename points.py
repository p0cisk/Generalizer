from builtins import object
from PyQt5.QtGui import *
from math import sqrt, acos, pi, fabs

class line_pnts(object):
    def __init__(self, cpSource = None):
        if cpSource == None:
            self.x = []
            self.y = []
            self.n_points = 0
        else:
            self.x = list(cpSource.x)
            self.y = list(cpSource.y)
            self.n_points = len(self.x)

    def add_point(self, p):
        self.x.append(p.x)
        self.y.append(p.y)
        self.n_points = len(self.x)

    def add_point_xy(self, x, y):
        self.x.append(x)
        self.y.append(y)
        self.n_points = len(self.x)

    def add_points(self, pts):
        self.x.extend(pts.x)
        self.y.extend(pts.y)
        self.n_points = len(self.x)

    def repleace_point(self, index, p):
        self.x[index] = p.x
        self.y[index] = p.y

    def repleace_all_pts(self, pts):
        self.x = pts.x[:]
        self.y = pts.y[:]
        self.n_points = len(self.x)


    def insert_point(self, index, p):
        self.x.insert(index, p.x)
        self.y.insert(index, p.y)
        self.n_points = len(self.x)


class point(object):
    def __init__(self):
        self.x = 0.
        self.y = 0.


def point_scalar(a, k, res):
    res.x = a.x * k
    res.y = a.y * k


def points_add(a, b, res):
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
    #distance between two points
    return sqrt((a.x-b.x)*(a.x-b.x)+(a.y-b.y)*(a.y-b.y))

def point_distance(p1, p2, p):
    #Perpendicular distance from point to line
    try:
        #return fabs( (p2.x-p1.x)*(p1.y-p.y)-(p1.x-p.x)*(p2.y-p1.y) ) / sqrt((p2.x-p1.x)*(p2.x-p1.x) + (p2.y-p1.y)*(p2.y-p1.y))
        return fabs( (p2.x-p1.x)*(p1.y-p.y)-(p1.x-p.x)*(p2.y-p1.y) ) / point_dist(p1, p2)
    except:
        return 0

def point_dist2(a):
    return a.x*a.x + a.y*a.y

def point_dot(a, b):
    return a.x*b.x+a.y*b.y


#calc angle g
#p_______p1
# \g)
#  \
#   \
#    p2
def point_angle(p, p1, p2):
    pp1 = point()
    pp2 = point()

    pp1.x = p1.x - p.x
    pp1.y = p1.y - p.y

    pp2.x = p2.x - p.x
    pp2.y = p2.y - p.y

    pp1_len = point_dist(p, p1)
    pp2_len = point_dist(p, p2)

    if pp1_len == 0 or pp2_len == 0: return 0

    return ((acos((pp1.x*pp2.x+pp1.y*pp2.y)/(pp1_len*pp2_len)))*180)/pi

    #def point_add_new(points, index, res):
    #res.add_point_xy(points.x[index], points.y[index])
    #res.x.append(points.x[index])
    #res.y.append(points.y[index])

    #res.n_points = len(res.x)


def Vect_new_line_struct(l):
    res = line_pnts()

    for i in l:
        res.x.append(i[0])
        res.y.append(i[1])
    res.n_points = len(l)

    return res

def compare_points(a, b):
    return (a.x == b.x) and (a.y == b.y)

"""
p = point()
p.x = 9
p.y = 10

p1 = point()
p1.x = 4
p1.y = 7

p2 = point()
p2.x = 5
p2.y = 3

pts = line_pnts()
pts.add_point(p)
pts.add_point(p1)

tmp = line_pnts(pts)
pts.add_point(p2)

print tmp.n_points, pts.n_points"""
