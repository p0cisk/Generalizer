from __future__ import print_function
from __future__ import absolute_import
from builtins import range
from qgis.PyQt.QtWidgets import *
from .points import *
from .matrix import *

GRASS_EPSILON = 1.0e-15


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
        points_add(last, ppoint, npoint)
        points.repleace_point(next, npoint)

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
        points_add(p, tmp, p)
        i = i + 1

    i = half
    while i+half < n:
        point_assign(points, i, s)
        point_scalar(s, 1. - slide, s)
        point_scalar(p, sc*slide, tmp)
        points_add(tmp, s, res[i])
        if i+half+1 < n:
            point_assign(points, i-half, tmp)
            point_substract(p, tmp, p)
            point_assign(points, i+half+1, tmp)
            points_add(p, tmp, p)
        i = i + 1

    i = half
    while i+half < n:
        points.repleace_point(i, res[i])

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
        points_add(s, tmp, res[i])
        i = i + 1

    i = half
    while i+half < n:
        points.repleace_point(i, res[i])

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
    res = line_pnts()

    n = points.n_points

    if n < 3: return n

    d1 = 1./(1+weight)
    d2 = float(weight)/(1+weight)

    point_assign(points, 0, p0)
    point_assign(points, n-1, pn)

    tmp = line_pnts(points)

    for i in range(level):
        cut_edges(tmp, res, d1, d2)

        res.n_points = len(res.x)
        tmp = line_pnts(res)

        res = line_pnts()


    tmp.insert_point(0, p0)
    tmp.add_point(pn)

    points.repleace_all_pts(tmp)

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

        res.add_point(m1)
        res.add_point(m2)


def hermite(points, threshold, a):
    i = 1
    p1 = point()
    p2 = point()
    t1 = point()
    t2 = point()
    h1p1 = point()
    h2p2 = point()
    h3t1 = point()
    h4t2 = point()
    tmp1 = point()
    tmp2 = point()
    tmp = point()

    res = line_pnts()


    point_assign(points, 1, p1)
    point_assign(points, 0, p2)
    t1 = getEdgeTangent(p1, p2)
    points.insert_point(0, t1)

    point_assign(points, -2, p1)
    point_assign(points, -1, p2)
    t2 = getEdgeTangent(p1, p2)
    points.insert_point(points.n_points, t1)

    n = points.n_points

    if n < 3:
        return n

    h1 = lambda s: (2*(s**3))-(3*(s**2))+1
    h2 = lambda s: 3*(s**2)-2*(s**3)
    h3 = lambda s: (s**3)-(2*(s**2))+s
    h4 = lambda s: (s**3)-(s**2)
    ht = lambda s: (1+2*s)*(1-s)**2

    while i < n-2:
        point_assign(points, i, p1)
        point_assign(points, i+1, p2)

        dist = point_dist(p1, p2)
        #t = 0.
        if dist == 0 or dist<threshold:
            i = i+1
            res.add_point(p1)
            res.add_point(p2)
            continue
        else:
            t = float(threshold)/dist
        s = 0.

        t1 = getTangent(points, a, i)
        t2 = getTangent(points, a, i+1)

        while s < 1:
            point_scalar(p1, h1(s), h1p1)
            point_scalar(p2, h2(s), h2p2)
            point_scalar(t1, h3(s), h3t1)
            point_scalar(t2, h4(s), h4t2)

            points_add(h1p1, h2p2, tmp1)
            points_add(h3t1, h4t2, tmp2)
            points_add(tmp1, tmp2, tmp)

            res.add_point(tmp)

            s = s+t

        i = i + 1

    res.add_point(p2)

    points.repleace_all_pts(res)

    return points.n_points

def getEdgeTangent(p1, p2):
    p = point()

    p.x = (p2.x-p1.x)+p2.x
    p.y = (p2.y-p1.y)+p2.y

    return p

def getTangent(points, a, i):
    p1 = point()
    p2 = point()
    p = point()

    point_assign(points, i-1, p1)
    point_assign(points, i+1, p2)

    point_substract(p2, p1, p)
    point_scalar(p, a, p)

    return p

def snakes(points, alpha, beta):
    n = points.n_points

    if n < 3: return n

    plus = 4

    g = MATRIX(n+2*plus, n+2*plus)
    xcoord = MATRIX(n+2*plus, 1)
    ycoord = MATRIX(n+2*plus, 1)
    xout = MATRIX(n+2*plus, 1)
    yout = MATRIX(n+2*plus, 1)

    x0 = points.x[0]
    y0 = points.y[0]

    i = 0
    while i<n:
        xcoord.a[i+plus][0] = points.x[i]-x0
        ycoord.a[i+plus][0] = points.y[i]-y0
        i = i+1

    i = 0
    while i<plus:
        xcoord.a[i][0] = 0
        ycoord.a[i][0] = 0
        i = i+1

    i = n+plus
    while i<n+2*plus:
        xcoord.a[i][0] = points.x[n-1]-x0
        ycoord.a[i][0] = points.y[n-1]-y0
        i = i+1

    a = 2. * alpha + 6. * beta
    b = -alpha - 4. * beta
    c = beta

    val = [c, b, a, b, c]

    i = 0
    while i < n+2*plus:
        j = 0
        while j < n+2*plus:
            index = j-i+2
            if index >= 0 and index <=4:
                g.a[i][j] = val[index]
            else:
                g.a[i][j] = 0
            j = j +1

        i = i+1

    i = 0
    while i < g.rows:
        g.a[i][i]= g.a[i][i] + 1.
        i = i+1

    # fix_print_with_import
    print(2)
    ginv = matrix_inverse(g)
    # fix_print_with_import
    # fix_print_with_import
    print(3)

    xout = matrix_mult(ginv, xcoord)
    yout = matrix_mult(ginv, ycoord)

    # fix_print_with_import
    # fix_print_with_import
    print(4)

    i = 1
    while i < n-1:
        points.x[i] = xout.a[i+plus][0] + x0
        points.y[i] = yout.a[i+plus][0] + y0

        i = i+1

    points.n_points = len(points.x)
    return points.n_points

"""
l = [[0,0], [1,1], [1,2], [2,3], [3,3], [4,2], [5,3], [4,5], [4,7], [6,9], [9,10]]
p = Vect_new_line_struct(l)
pi = hermite(p, 1, 0.3)
print l
print 'X;Y'
for i in range(len(p.x)):
    print p.x[i], ';', p.y[i]"""
