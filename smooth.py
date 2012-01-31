from PyQt4.QtGui import *
from points import *

GRASS_EPSILON = 1.0e-15


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


def boyle(points, look_ahead):
    ppoint = point()
    npoint = point()
    last = point()
    next = 1
    i = 0
    p = 0
    c1 = 0.
    c2 = 0.

    n = points.n_points

    if look_ahead < 2 or look_ahead > n: return n

    point_assign(points, 0, last)

    c1 = 1. / float(look_ahead-1)
    c2 = 1. - c1

    while i < n-2:
        p = i + look_ahead
        if p >= n: p = n - 1
        point_assign(points, p, ppoint)
        point_scalar(ppoint, c1, ppoint)
        point_scalar(last, c2, last)
        point_add(last, ppoint, npoint)
        points.x[next] = npoint.x
        points.y[next] = npoint.y

        next = next + 1
        i = i + 1

        last = npoint

    points_copy_last(points, next)

    return points.n_points

def sliding_averaging(points, slide, look_ahead):
    n = 0
    half = 0
    i = 1
    sc = 0.
    p = point()
    tmp = point()
    s = point()

    n = points.n_points
    res = []
    for w in range(n):
        res.append(point())

    half = look_ahead / 2

    if look_ahead % 2 == 0:
        return n

    if look_ahead >= n or look_ahead == 1:
        return 0

    sc = 1. / float(look_ahead)

    point_assign(points, 0, p)
    while i < look_ahead:
        point_assign(points, i, tmp)
        point_add(p, tmp, p)
        i = i + 1

    i = half
    while i+half < n:
        point_assign(points, i, s)
        point_scalar(s, 1. - slide, s)
        point_scalar(p, sc*slide, tmp)
        point_add(tmp, s, res[i])
        if i+half+1 < n:
            point_assign(points, i-half, tmp)
            point_substract(p, tmp, p)
            point_assign(points, i+half+1, tmp)
            point_add(p, tmp, p)
        i = i + 1

    i = half
    while i+half < n:
        points.x[i] = res[i].x
        points.y[i] = res[i].y
        i = i + 1

    return points.n_points

def distance_weighting(points, slide, look_ahead):
    p = point()
    c = point()
    s = point()
    tmp = point()

    n = 0
    i = 0
    half = 0
    j = 0

    dists = 0.
    d = 0.

    n = points.n_points

    res = []
    for w in range(n):
        res.append(point())

    if look_ahead % 2 == 0:
        return n

    point_assign(points, 0, res[0])

    half = look_ahead / 2

    i = half
    while i+half < n:
        point_assign(points, i, c)
        s.x = 0.
        s.y = 0.
        dists = 0.

        j = i-half
        while j <= i+half:
            if j == i:
                j = j + 1
                continue

            point_assign(points, j, p)
            d = point_dist(p, c)

            if d < GRASS_EPSILON:

                j = j + 1
                continue

            d = 1. / d
            dists = dists + d
            point_scalar(p, d, tmp)
            s.x = s.x + tmp.x
            s.y = s.y + tmp.y
            j = j + 1

        if dists == 0:
            point_scalar(s, slide, tmp)
        else:
            point_scalar(s, slide/dists, tmp)
        point_scalar(c, 1.-slide, s)
        point_add(s, tmp, res[i])
        i = i + 1

    i = half
    while i+half < n:
        points.x[i] = res[i].x
        points.y[i] = res[i].y

        i = i + 1

    return points.n_points


def chaiken(points, level, weight):
    n = 0
    i = 0
    j = 0
    p0 = point()
    pn = point()
    p1 = point()
    p2 = point()
    m1 = point()
    m2 = point()
    tmp = line_pnts()
    res = line_pnts()

    n = points.n_points

    if n < 3: return n

    d1 = 1./(1+weight)
    d2 = float(weight)/(1+weight)

    #thresh = thresh * thresh

    point_assign(points, 0, p0)
    point_assign(points, n-1, pn)
    #res.x.append(p0.x)
    #res.y.append(p0.y)

    tmp.x.extend(points.x)
    tmp.y.extend(points.y)
    tmp.n_points = len(tmp.x)

    for i in range(level):
        """
        for j in range(tmp.n_points):
            if j == n-1: break
            point_assign(tmp, j, p1)
            point_assign(tmp, j+1, p2)
            #print 'y1: ' + str(p1.y)
            #print 'y2: ' + str(p2.y)

            point_calc_new(p1, p2, d1, m1)
            point_calc_new(p1, p2, d2, m2)

            #print 'y1:', m1.y
            #print 'y2:', m2.y

            res.x.extend([m1.x, m2.x])
            res.y.extend([m1.y, m2.y])"""
        cut_edges(tmp, res, d1, d2)

        res.n_points = len(res.x)
        tmp.x = []
        tmp.y = []
        tmp.n_points = 0

        tmp.x.extend(res.x)
        #print res.x
        tmp.y.extend(res.y)
        tmp.n_points = len(tmp.x)

        res.x = []
        res.y = []
        res.n_points = 0



    #points2.x.append(pn.x)
    #points2.y.append(pn.y)
    #points2.n_points = len(points2.x)
    tmp.x.insert(0, p0.x)
    tmp.x.append(pn.x)

    tmp.y.insert(0, p0.y)
    tmp.y.append(pn.y)

    points.x = []
    points.y = []
    points.x.extend(tmp.x)
    points.y.extend(tmp.y)
    points.n_points = len(points.x)


    return points.n_points


def point_calc_new(p1, p2, d, m):
    m.x = (p1.x+d*(p2.x-p1.x))
    m.y = (p1.y+d*(p2.y-p1.y))


def cut_edges(points, res, d1, d2):
    p1 = point()
    p2 = point()
    m1 = point()
    m2 = point()

    for i in range(points.n_points):
        if i == points.n_points-1: break
        point_assign(points, i, p1)
        point_assign(points, i+1, p2)

        point_calc_new(p1, p2, d1, m1)
        point_calc_new(p1, p2, d2, m2)

        res.x.extend([m1.x, m2.x])
        res.y.extend([m1.y, m2.y])


"""
l = [[0,0], [1,1], [1,2], [2,3], [3,3], [4,2], [5,3], [4,5], [4,7], [6,9], [9,10]]
p = Vect_new_line_struct(l)
pi = chaiken(p, 2, 3)
print l
print 'X;Y'
for i in range(len(pi.x)):
    print pi.x[i], ';', pi.y[i] """