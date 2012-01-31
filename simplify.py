from PyQt4.QtGui import *
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

    res.add_point_xy(points.x[0], points.y[0])

    while i < n-1:

        j = i+1
        point_assign(points, i, p1)
        point_assign(points, j, p2)

        dst = point_dist(p1, p2)

        while dst <= eps:
            j = j + 1
            if j > n-1: break
            point_assign(points, j, p2)
            dst = point_dist(p1, p2)
        res.add_point(p2)

        i = j


    points.repleace_all_pts(res)

    return points.n_points



def douglas_peucker(pts, tolerance):
    anchor  = 0
    floater = len(pts) - 1
    stack   = []
    keep    = set()

    if len(pts) < 3: return pts

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
    res.add_point_xy(points.x[0], points.y[0])
    #point_add_new(points, 0, res) #use point_add insted of this function

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
            res.add_point_xy(points.x[j], points.y[j])
            #point_add_new(points, j, res) #use point_add insted of this function
            i = j
            if i == n-1:
                end = True
            j = j + look_ahead
            if j > n-1: j = n-1
            point_assign(points, i, p1)
            point_assign(points, j, p2)

    points.repleace_all_pts(res)

    return points.n_points


def jenks(points, threshold, angle_thresh):
    n = points.n_points
    i = 1
    p = point()
    p1 = point()
    p2 = point()
    res = line_pnts()

    res.add_point_xy(points.x[0], points.y[0])
    #point_add_new(points, 0, res) #use point_add insted of this function

    point_assign(points, 0, p1)
    while i < n-1:
        point_assign(points, i, p)
        point_assign(points, i+1, p2)

        dist = point_distance(p1, p2, p)
        #angle = point_angle(p1, p, p2)
        #print i, angle
        if dist >= threshold:# and angle >= angle_thresh:
            i = i + 1
            res.add_point_xy(points.x[i-1], points.y[i-1])
            point_assign(points, i-1, p1)
        else:
            while dist < threshold:# or angle < angle_thresh:
                i = i+1
                if i == n-1: break
                point_assign(points, i, p)
                point_assign(points, i+1, p2)
                dist = point_distance(p1, p2, p)
                #angle = point_angle(p1, p, p2)

    res.add_point_xy(points.x[n-1], points.y[n-1])

    points.repleace_all_pts(res)

    return points.n_points


def reumann_witkam(points, thresh):
    x0 = point()
    x1 = point()
    x2 = point()
    sub = point()
    diff = point()
    res = line_pnts()
    same = True

    n = points.n_points

    if n<3: return n

    thresh = thresh**2

    seg1 = 0
    seg2 = 1
    count = 1

    point_assign(points, 0, x1)
    res.add_point(x1)
    i = 1
    while same:
        point_assign(points, i, x2)
        same = compare_points(x1, x2)
        i = i+1
        if i == n: return n
    point_substract(x2, x1, sub)
    subd = point_dist2(sub)

    i = 2
    while i < n:
        point_assign(points, i, x0)
        point_substract(x1, x0, diff)
        diffd = point_dist2(diff)
        sp = point_dot(diff, sub)
        if subd == 0: dist = 0
        else: dist = (diffd * subd - sp*sp) / subd

        if dist > thresh:
            point_assign(points, i-1, x1)
            same = True
            j = i
            while same:
                point_assign(points, j, x2)
                same = compare_points(x2, x1)
                j = j+1
            point_substract(x2, x1, sub)
            subd = point_dist2(sub)

            res.add_point(x0)

            count = count + 1

        i = i+1

    res.add_point_xy(points.x[n-1], points.y[n-1])


    points.repleace_all_pts(res)

    return points.n_points



"""
l = [[0,0], [1,1], [1,2], [2,3], [3,3], [4,2], [5,3], [4,5], [4,7], [6,9], [9,10]]
#l = [[9,10], [6,9], [4,7], [4,5], [5,3], [4,2], [3,3], [2,3], [1,2], [1,1], [0,0]]
#l = [(487532,653736), (487532,653736), (487608,653726), (487646,653736)]
p = Vect_new_line_struct(l)
reumann_witkam(p, 1)
print l
print 'X,Y'
for i in range(len(p.x)):
    print p.x[i], ',', p.y[i]"""