import unittest
from copy import copy
from tKot.common import Polygon, Box, Point, Size


class TestType(unittest.TestCase):

    def test_Polygon(self):
        pol = Polygon(4, 0, 24, 0, 24, 4, 13, 4, 13, 9, 10, 9, 10, 33, 27, 33, 27, 9, 13, 9,
                      13, 4, 24, 4, 24, 0, 33, 0, 37, 4, 37, 38, 33, 42, 4, 42, 0, 38, 0, 4)
        self.assertEqual(pol.size, Point(37, 42))
        x = pol.base
        self.assertEqual(pol.base, Point(0, 0))
        pol = pol.reshape(Point(100, 100))
        point = Point(3, 5)
        pol *= Point(2, 1)
        pol += point
        self.assertEqual(pol.base, Point(3, 5))
        print(*pol)

    def test_Box(self):
        box = Box(1, 1, 10, 10)
        self.assertEqual(str(box), "9x9+1+1")
        box2 = Box.from_size(
            size=Size(10, 10),
            base=Point(2, 2)
        )
        self.assertEqual(str(box2), "10x10+2+2")

    def test_init(self):
        self.assertEqual(Point(), Point(0, 0))
        self.assertRaises(ValueError, Point, (0, 1, 3, 4))
        point = Point(0, 0)
        self.assertEqual(point.x, 0, "compare x")
        self.assertEqual(Point(x=1, y=10), Point(1, 10), "by x, y ordinate")
        size = Size(arr=point._coords)
        self.assertEqual(str(size), "0x0")

    def test_reduce(self):
        point = Point(10, 10)
        point2 = Point(100, 100) - point
        self.assertEqual(point2, Point(90, 90))

    def test_add(self):
        point = Point(10, 10)
        point2 = Point(100, 100) + point
        self.assertEqual(point2, Point(110, 110))
        point.y += 1
        self.assertEqual(point, Point(10, 11))

    def test_unpack(self):
        point = Point(10, 10)
        x, y = point
        self.assertEqual(x, 10)
        # self.assertEqual(list(point), [10, 10])

    def test_floordiv(self):
        point = Point(10, 10)
        self.assertEqual(point // 2, Point(5, 5))

    def test_idiv(self):
        point = Point(10, 10)
        p_div = Point(2, 3)
        res = point / p_div
        self.assertEqual(point // 2, Point(5, 5))

    def test_copy(self):
        p = Point(10, 10)
        p2 = copy(p)
        print(id(p2), id(p))
