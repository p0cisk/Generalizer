from points import *
import math


def vertex_reduction(points, eps):
#http://softsurfer.com/Archive/algorithm_0205/algorithm_0205.htm#Vertex Reduction
    start = 0
    i = 0
    count = 1
    n = 0
    p1 = point()
    p2 = point()
    res = line_pnts()

    n = points.n_points

    if n <= 2: return n

    i = 0
    dst = 0

    res.x.append(points.x[0])
    res.y.append(points.y[0])

    while i < n-1:

        j = i+1
        point_assign(points, i, p1)
        point_assign(points, j, p2)

        dst = point_dist(p1, p2)
        #print dst

        while dst <= eps:
            j = j + 1
            if j > n-1: break
            point_assign(points, j, p2)
            dst = point_dist(p1, p2)
        #point_assign(points, j+1, p2)
        res.x.append(p2.x)
        res.y.append(p2.y)
        i = j

    #res.x.append(points.x[n-1])
    #res.y.append(points.y[n-1])
    res.n_points = len(res.x)

    points.x = []
    points.y = []
    points.x.extend(res.x)
    points.y.extend(res.y)
    points.n_points = len(points.x)

    return points.n_points


"""

>>> line = [(0,0),(1,0),(2,0),(2,1),(2,2),(1,2),(0,2),(0,1),(0,0)]
>>> douglas_pecker(line, 1.0)
[(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]

>>> line = [(0,0),(0.5,0.5),(1,0),(1.25,-0.25),(1.5,.5)]
>>> douglas_pecker(line, 0.25)
[(0, 0), (0.5, 0.5), (1.25, -0.25), (1.5, 0.5)]

"""

def douglas_pecker(pts, tolerance):
    anchor  = 0
    floater = len(pts) - 1
    stack   = []
    keep    = set()

    stack.append((anchor, floater))
    while stack:
        anchor, floater = stack.pop()

        # initialize line segment
        if pts[floater] != pts[anchor]:
            anchorX = float(pts[floater][0] - pts[anchor][0])
            anchorY = float(pts[floater][1] - pts[anchor][1])
            seg_len = math.sqrt(anchorX ** 2 + anchorY ** 2)
            # get the unit vector
            anchorX /= seg_len
            anchorY /= seg_len
        else:
            anchorX = anchorY = seg_len = 0.0

        # inner loop:
        max_dist = 0.0
        farthest = anchor + 1
        for i in range(anchor + 1, floater):
            dist_to_seg = 0.0
            # compare to anchor
            vecX = float(pts[i][0] - pts[anchor][0])
            vecY = float(pts[i][1] - pts[anchor][1])
            seg_len = math.sqrt( vecX ** 2 + vecY ** 2 )
            # dot product:
            proj = vecX * anchorX + vecY * anchorY
            if proj < 0.0:
                dist_to_seg = seg_len
            else:
                # compare to floater
                vecX = float(pts[i][0] - pts[floater][0])
                vecY = float(pts[i][1] - pts[floater][1])
                seg_len = math.sqrt( vecX ** 2 + vecY ** 2 )
                # dot product:
                proj = vecX * (-anchorX) + vecY * (-anchorY)
                if proj < 0.0:
                    dist_to_seg = seg_len
                else:  # calculate perpendicular distance to line (pythagorean theorem):
                    dist_to_seg = math.sqrt(abs(seg_len ** 2 - proj ** 2))
                if max_dist < dist_to_seg:
                    max_dist = dist_to_seg
                    farthest = i

        if max_dist <= tolerance: # use line segment
            keep.add(anchor)
            keep.add(floater)
        else:
            stack.append((anchor, farthest))
            stack.append((farthest, floater))

    keep = list(keep)
    keep.sort()
    return [pts[i] for i in keep]

def lang(points, eps, look_ahead):
    i = 0
    j = look_ahead
    n = points.n_points
    if j > n-1: j = n-1
    p1 = point()
    p2 = point()
    p = point()
    res = line_pnts()

    point_assign(points, i, p1)
    point_assign(points, j, p2)
    point_add_new(points, 0, res)
    end = False
    while not end:
        dists = []
        between = True

        for m in range(i+1, j):
            point_assign(points, m, p)
            dists.append(point_distance(p1, p2, p))

        for dist in dists:
            if dist > eps:
                between = False
                break

        if not between:
            j = j - 1
            point_assign(points, j, p2)
        else:
            point_add_new(points, j, res)
            i = j
            if i == n-1:
                end = True
            j = j + look_ahead
            if j > n-1: j = n-1
            point_assign(points, i, p1)
            point_assign(points, j, p2)

    points.x = []
    points.y = []
    points.x.extend(res.x)
    points.y.extend(res.y)
    points.n_points = len(points.x)


def point_distance(p1, p2, p):
    try:
        return math.fabs( (p2.x-p1.x)*(p1.y-p.y)-(p1.x-p.x)*(p2.y-p1.y) ) / math.sqrt((p2.x-p1.x)*(p2.x-p1.x) + (p2.y-p1.y)*(p2.y-p1.y))
    except:
        return 0

"""
#l = [[0,0], [1,1], [1,2], [2,3], [3,3], [4,2], [5,3], [4,5], [4,7], [6,9], [9,10]]
l = [(487532,653736), (487532,653736), (487608,653726), (487646,653736)]
p = Vect_new_line_struct(l)
lang(p, 50, 8)
print l
print 'X;Y'
for i in range(len(p.x)):
    print p.x[i], ';', p.y[i]"""