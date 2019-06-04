import math
import random
import pygame

def is_not_null(vector2):
    """ Returns true if the vector is null, returns false otherwise 
    
    :param vector2: Vector2
    :type vector2" pygame.Vector2
    
    :returns: TTrue if the vector is null, False otherwise 
    :rtype: bool
    """
    return (vector2[0] != 0 or vector2[1] != 0)

def get_angle_from_vector(vector2):
    """ Returns the angle from X+ axis to the given vector """
    return math.atan2(-vector2[1], vector2[0]) * (180/math.pi)
    
def orientation_asvector(orientation):
    """ Returns a vector representation of the given orientation in degrees """
    return pygame.Vector2(math.cos(math.radians(orientation)), -math.sin(math.radians(orientation)))
    
def map_to_range(orientation):
    """ Maps the angle orientation in degrees to range [-180, 180) """
    return orientation - 360*math.floor((orientation + 180) * (1/360))
    
def random_binomial():
    """ Returns a random value in the range [-1, 1] """
    return random.random() - random.random()
    
def vec2_to_int(vector2):
    return pygame.Vector2(int(vector2[0]), int(vector2[1]))
    
def lines_intersect(line1, line2):
    """ Returns intersection point between line1 and line2, or None if they dont intersect """
    (x1, y1), (x2, y2) = line1
    (x3, y3), (x4, y4) = line2
    
    # Compute coeficients for line1
    # where a1 x + b1 y + c1 = 0
    a1 = y2 - y1
    b1 = x1 - x2
    c1 = x2 * y1 - x1 * y2
    
    # Compute r3 and r4
    r3 = a1 * x3 + b1 * y3 + c1
    r4 = a1 * x4 + b1 * y4 + c1
    
    # If r3 and r4 have same signs, lines don't intersect
    #if r3 != 0 and r4 != 0 and r3*r4 > 0:
    if  r3*r4 >= 0:
        return None
        
    # Compute coeficients for line2
    # where a2 x + b2 y + c2 = 0
    a2 = y4 - y3
    b2 = x3 - x4
    c2 = x4 * y3 - x3 * y4
    
    # Compute r1 and r2
    r1 = a2 * x1 + b2 * y1 + c2
    r2 = a2 * x2 + b2 * y2 + c2
    
    # If r1 and r2 have same signs, lines don't intersect
    if  r1*r2 >= 0:
        return None
    
    # Line segments definitely intersect
    # Compute intersection point
    denom = a1 * b2 - a2 * b1
    if denom == 0:
        return None # Colinear???? What should I do in this case? Maybe return x1, y1
        
    offset = abs(denom)//2
    
    num = b1 * c2 - b2 * c1
    x = (num - offset if num < 0 else num + offset) // denom
    
    num = a2 * c1 - a1 * c2
    y = (num - offset if num < 0 else num + offset) // denom
    
    return pygame.Vector2(x, y)
    
def get_perpendicular(line):
    """ Returns line perpendicular to line """
    (x1, y1), (x2, y2) = line
    x = x2 - x1
    y = y2 - y1
    
    return pygame.Vector2(-y, x), pygame.Vector2(y, -x)
    
def get_bound_radius(rect):
    """ Returns the radius of a circle that bounds the given rect """
    return math.sqrt((rect.height/2)**2 + (rect.width/2)**2)
    
     
