from abc import ABC, abstractmethod
from typing import Self
import numpy as np
from numpy.typing import NDArray


class Coords(ABC):
    _coords: NDArray[np.float16]

    @abstractmethod
    def __init__(self, *coords: int | float, arr: np.ndarray = None):
        """init"""

    def __mul__(self, other: int | float):
        if isinstance(other, (int, float)):
            return self.__class__(arr=self._coords * other)
        else:
            raise TypeError(F"for multiplicate of {self.__class__.__name__}")

    def __truediv__(self, other: int | float):
        if isinstance(other, (int, float)):
            return self.__class__(arr=self._coords / other)
        else:
            raise TypeError(F"for truediv of {self.__class__.__name__}")

    def __floordiv__(self, other: int | float):
        if isinstance(other, (int, float)):
            return self.__class__(arr=self._coords / other)
        else:
            raise TypeError(F"for truediv of {self.__class__.__name__}")

    def __iter__(self):
        return iter(self._coords.astype(
            dtype=np.int16
        ).flatten(
        ).tolist())

    def __eq__(self, other: Self):
        return np.equal(self._coords, other._coords).all()


class Point(Coords):
    def __init__(self, *coords: int | float, arr: np.ndarray = None, x: int | float = None, y: int | float = None):
        if arr is not None:
            self._coords = arr
        else:
            if x is not None or y is not None:
                coords = (
                    x if isinstance(x, (int, float)) else 0,
                    y if isinstance(y, (int, float)) else 0
                )
            elif len(coords) == 0:
                coords = (0, 0)
            elif len(coords) != 2:
                raise ValueError(F"{self.__class__.__name__} got not one pair values")
            self._coords = np.array(coords, dtype=np.float16).reshape(1, 2)

    @property
    def x(self) -> float:
        return float(self._coords[0][0])

    @property
    def y(self) -> float:
        return float(self._coords[0][1])

    @x.setter
    def x(self, value: int | float):
        self._coords[0][0] = value

    @y.setter
    def y(self, value: int | float):
        self._coords[0][1] = value

    def __add__(self, other: Self):
        return self.__class__(arr=self._coords + other._coords)

    def __sub__(self, other: Self):
        return self.__class__(arr=self._coords - other._coords)

    def __mul__(self, other: int | float | Self):
        if isinstance(other, Point):
            return self.__class__(arr=self._coords * other._coords)
        else:
            return super().__mul__(other)

    def __truediv__(self, other: int | float | Self):
        if isinstance(other, Point):
            return self.__class__(arr=self._coords / other._coords)
        else:
            return super().__truediv__(other)

    def __floordiv__(self, other: int | float | Self):
        if isinstance(other, Point):
            return self.__class__(arr=self._coords // other._coords)
        else:
            return super().__floordiv__(other)

    def __str__(self):
        return F"{int(self.x)}+{int(self.y)}"

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise StopIteration


class Size(Point):
    def __str__(self):
        return F"{int(self.x)}x{int(self.y)}"


class Polygon(Coords):
    def __init__(self, *coords: int | float, arr: np.ndarray = None):
        if arr is not None:
            self._coords = arr
        elif len(coords) < 2:
            raise ValueError(F"{self.__class__.__name__} got not pair values")
        else:
            self._coords = np.array(coords, dtype=np.float16).reshape(len(coords) // 2, 2)

    def __add__(self, other: Point):
        return self.__class__(arr=self._coords + other._coords)

    def __sub__(self, other: Point):
        return self.__class__(arr=self._coords - other._coords)

    def __mul__(self, other: int | float | Point):
        if isinstance(other, Point):
            return self.__class__(arr=self._coords * other._coords)
        else:
            return super().__mul__(other)

    def __truediv__(self, other: int | float | Point):
        if isinstance(other, Point):
            return self.__class__(arr=self._coords / other._coords)
        else:
            return super().__truediv__(other)

    def __floordiv__(self, other: int | float | Point):
        if isinstance(other, Point):
            return self.__class__(arr=self._coords // other._coords)
        else:
            return super().__floordiv__(other)

    @property
    def size(self) -> Size:
        """area occupied by polygon"""
        return Size(arr=(self._coords.max(axis=0) - self._coords.min(axis=0)).reshape(1, 2))

    @property
    def base(self) -> Point:
        """upper left point"""
        return Point(arr=self._coords.min(axis=0).reshape(1, 2))

    def move_to(self, p: Point) -> Self:
        """move base to Point<x, y>"""
        return self + (p - self.base)

    def reshape(self, shape: Point) -> Self:
        return self * (shape / self.size)


class Box(Polygon):
    def validate(self):
        if len(self._coords) != 2:
            raise ValueError(F"got pair[{len(self._coords)}], expected 2")

    @classmethod
    def from_size(cls, size: Size, base: Point = Point(0, 0)) -> Self:
        return cls(arr=np.concatenate((base._coords, (base + size)._coords)))

    def __str__(self):
        return F"{self.size}+{self.base}"
