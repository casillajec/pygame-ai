# -*- coding: utf-8 -*-
""" Iterator that describes a Path

This module implements an iterator :py:class:`~.path.Path` to be used the 
descriptions of the points that form a particular path. There are also 
the following classes with specialised paths:

    * :py:class:`~.path.CyclicPath`
    * :py:class:`~.path.MirroredPath`
    
Aswell as the following pre-implemented useful paths:

    * :py:class:`~.path.PathCircumference`
    * :py:class:`~.path.PathParabola`

"""
import math

class Path(object):
    """ Iterator that describes a **Path**
    
    Provides a flexible interface to describe dynamic paths as an iterator,
    it uses a **Path Function** in the form of f(x) = y to describe
    the path.
    
    Parameters
    ----------
    path_func: function number -> number
        The function that describes the path
    domain_start: int
        Start point for the function domain, defaults to 0
    domain_end: int
        End point for the function domain
    increment: int
        Step to generate every point on the path
        
        
    Example
    -------
    The way this class is meant to be used is by sub-classing it and creating
    your own class with your own properties, this is a slightly useluess
    implementation of :py:class:`~.path.CircumferencePath` that only
    traverses the path once.
    
    .. code-block:: python
    
        class OnceCircumferencePath(Path):
        
            def __init__(self, center, radius):
                self.center = center
                self.radius = radius
    
                def circumference_path(self, x):
                    angle = math.radians(x)
                    center = self.center
                    x = center[0] + math.cos(angle)*self.radius
                    y = center[1] + math.sin(angle)*self.radius
                    return x, y
                    
                super(OnceCircumferencePath, self).__init__(parabola_path, domain_start = 0, domain_end = 360, increment = 15)
        
        >>> mypath = OnceCircumferencePath(center = (50, 50), radius = 50)
        >>> next(mypath)
        (100.0, 50.0)
        >>> next(mypath)
        (98.29629131445341, 62.940952255126035)
        >>> next(mypath)
        (93.30127018922194, 75.0)
    
    
    A good tip is to use lambda functions in order to have dynamically
    updated paths, this allows to have attributes like 'center' update
    with the position of something in the game, which will alter
    the points the path will produce
    
    .. code-block:: python
    
        class OnceCircumferencePath(Path):
        
            def __init__(self, center, radius):
                self.center = center
                self.radius = radius
    
                def circumference_path(self, x):
                    angle = math.radians(x)
                    # Notice that we are now calling the attribute 'center' as a function
                    center = self.center()
                    x = center[0] + math.cos(angle)*self.radius
                    y = center[1] + math.sin(angle)*self.radius
                    return x, y
                    
                super(OnceCircumferencePath, self).__init__(parabola_path, domain_start = 0, domain_end = 360, increment = 15)
        
        >>> character = SomeGameObjectWithARect()
        # The 'center' parameter is now defined as a lambda functions that gets the position of a character
        >>> mypath = OnceCircumferencePath(center = (lambda: character.rect.center), radius = 50)
    """
    
    def __init__(self, path_func, domain_end, domain_start = 0, increment = 1):
        self.path_func = path_func
        self.increment = increment
        self.x = -increment + domain_start
        self.domain_start = domain_start
        self.domain_end = domain_end
        self.current = None
        
    def __iter__(self):
        return self
        
    def __next__(self):
        if self.x < self.domain_end:
            self.x += self.increment
            self.current = lambda: self.path_func(self, self.x)
            return self.current()
        else:
            raise StopIteration
            
    def __repr__(self):
        return 'Function Path'
        
    def reset(self):
        """ Returns the iterator to it's initial point """
        self.x = self.domain_start
        
    def as_list(self):
        """ Returns the path as a list of points
        
        This ignores the infinity of :py:class:`~.path.CyclicPath`
        and :py:class:`~.path.MirroredPath` and returns a finite list.
        Nevertheless, you should keep in mind that if for your own
        sub-classes this methods does not return the expected results,
        it's probabbly the method's fault (my faul) and you should
        implement your own since this is used for drawing indicators.
        
        Returns
        -------
            list(tuple(float, float))
        """
        path_list = []
        
        for x in range(self.domain_start, self.domain_end+1, self.increment):
            path_list.append(self.path_func(self, x))
            
        return path_list
        
        
class CyclicPath(Path):
    """Iterator that implements Cyclic Paths
    
    This is a sub-class of :py:class:`~.Path` that returns to the path's
    starting point once it reaches the end, this produces an infinite
    iterator.
    
    Uses the same parameters as :py:class:`~.Path`.
    """
    
    def __init__(self, path_func, domain_end, domain_start = 0, increment = 1):
        super(CyclicPath, self).__init__(path_func, domain_end, domain_start, increment)
        
    def __next__(self):
        if self.x >= self.domain_end:
            self.reset()
        
        return super(CyclicPath, self).__next__()
        
        
class MirroredPath(Path):
    """ Iterator that implements Mirrored Paths
    
    This is a sub-class of :py:class:`~.Path` that **Mirrors** the 
    path produced by the given function, this produces an infinite
    iterator that backtracks on the traversed path once it reaches
    it's domain_end, and does the same after it reaches domain_start.
    
    Uses the same parameters as :py:class:`~.Path`.
    """
    
    def __init__(self, path_func, domain_end, domain_start = 0, increment = 1):
        super(MirroredPath, self).__init__(path_func, domain_end, domain_start, increment)
        
    def __repr__(self):
        return 'Mirrored ' + super(MirroredPath, self).__repr__()
        
    def __next__(self):
        self.x += self.increment
        if self.x > self.domain_end or self.x < self.domain_start:
            self.increment = -self.increment
            self.x += self.increment
        
        self.current = lambda: self.path_func(self, self.x)
        return self.current()
        
    def as_list(self):
        path_list = []
        
        if self.increment > 0:
            f_range = range(self.domain_start, self.domain_end+1, self.increment)
        else:
            f_range = range(self.domain_end, self.domain_start-1, self.increment)
            
        for x in f_range:
                path_list.append(self.path_func(self, x))
            
        return path_list
            
    
class PathCircumference(CyclicPath):
    """ Circumference-like :py:class:`~.CyclicPath`
    
    Parameters
    ----------
    center: tuple(int, int) or function -> tuple(int, int)
    radius: int
    """
    
    def __init__(self, center, radius, start = 0):
        
        if not callable(center):
            callable_center = lambda : center
        else:
            callable_center = center
        self.center = callable_center
        self.radius = radius
        
        self.start = start
        
        def circumference_path(self, t):
            angle = math.radians(t)
            center = self.center()
            x = center[0] + math.cos(angle)*self.radius
            y = center[1] + math.sin(angle)*self.radius
            return x, y
            
        super(PathCircumference, self).__init__(circumference_path, domain_start = self.start, domain_end = self.start + 360, increment = 15)
        
    def __repr__(self):
        return 'PathCircumference'
        
class PathParabola(MirroredPath):
    """ Parabola-like :py:class:`~.MirroredPath`
    
    Parameters
    ----------
    origin: tuple(int, int) or function -> tuple(int, int)
        Lowest point of the parabola
    width: int
    height: int
    """
    
    def __init__(self, origin, width = 400, height = 100):
        if not callable(origin):
            callable_origin = lambda: origin
        else:
            callable_origin = origin
        self.origin = callable_origin
        self.domain_range = int(math.sqrt(height))
        self.amplitude = width/(2*self.domain_range)
        
        def parabola_path(self, t):
            origin = self.origin()
            x = origin[0] + t*self.amplitude
            y = origin[1] - t**2
            return x, y
            
        super(PathParabola, self).__init__(parabola_path, domain_start = -self.domain_range, domain_end = self.domain_range, increment = 2)
        
    def __repr__(self):
        return 'PathParbola'
