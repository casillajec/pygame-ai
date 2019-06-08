# -*- coding: utf-8 -*-
""" Kinematic movement

This module implements a series of classes and methods that emulate
the behavior of objects moving in a 2D space in a kinematic way
(involving acceleration)

Notes
-----
    This might need a slightly better explaination
"""

import math
import random

import pygame
import pygame.gfxdraw

from pygame_ai import colors
from pygame_ai.utils import math_utils
from pygame_ai.utils.list_utils import remove_if_exists
from pygame_ai.gameobject import DummyGameObject

class SteeringOutput(object):
    """ Container for Steering data
    
    This class is used as a container for the  output of the 
    :py:class:`KinematicSteeringBehavior` algorithms.
    
    These objects can be added, multiplied, and compared to eachother. Each
    of these operations will be executed element-wise
        
    Parameters
    ----------
    linear : :pgmath:`Vector2`, optional
        Linear acceleration, defaults to (0, 0)
    angular : int, optional
        Angular acceleration, defaults to 0
        
    Attributes
    ----------
    linear : :pgmath:`Vector2`
        Linear acceleration
    angular : int
        Angular acceleration
    """
    
    def __init__(self, linear = None, angular = None):
        if linear is None:
            linear = pygame.Vector2(0, 0)
        self.linear = linear
        
        if angular is None:
            angular = 0
        self.angular = angular
        
    def update(self, gameobject, tick):
        """ Update a :py:class:`~gameobject.GameObject`'s velocity and rotation
        
        This method should be called once per loop, it updates the given 
        :py:class:`~gameobject.GameObject`'s velocity and rotation based 
        on this :py:class:`SteeringOutput`'s acceleration request
        
        Parameters
        ----------
        gameobject : :py:class:`~gameobject.GameObject`
            The Game Objectthat will be updated
        tick : int
            Time transcurred since last loop
        """
        gameobject.velocity += self.linear * tick
        gameobject.rotation += self.angular * tick
        
        if gameobject.velocity.length() > gameobject.max_speed:
            gameobject.velocity.normalize_ip()
            gameobject.velocity *= gameobject.max_speed
            
    def copy(self):
        selfcopy = SteeringOutput()
        selfcopy.linear = pygame.Vector2(self.linear[0], self.linear[1])
        selfcopy.angular = self.angular
        
        return selfcopy
        
    def reset(self):
        self.linear[0], self.linear[1] = 0, 0
        self.angular = 0
            
    def __repr__(self):
        return 'linear: {} angular: {}'.format(self.linear, self.angular)
        
    def __eq__(self, other):
        return self.linear == other.linear and self.angular == other.angular
     
    # These might need to be modified
    def __mul__(self, number):
        new_steering = SteeringOutput()
        new_steering.linear = pygame.Vector2(self.linear[0], self.linear[1]) * number
        new_steering.angular = self.angular * number
        return new_steering
        
    def __rmul__(self, number):
        return self.__mul__(number)
        
    def __add__(self, other):
        new_steering = SteeringOutput()
        new_steering.linear += self.linear + other.linear
        new_steering.angular += self.angular + other.angular
        return new_steering
        
    def __neg__(self):
        new_steering = SteeringOutput()
        new_steering.linear = -self.linear
        new_steering.angular = -self.angular
        return new_steering

null_steering = SteeringOutput(linear = pygame.Vector2(0, 0), angular = 0)
""":py:class:`SteeringOutput` : Constant with 0 linear acceleration and 0 angular acceleration """

def negative_steering(linear, angular):
    """ Returns a steering request opposite to the linear and 
        angular accelerations provided.
        
        Parameters
        ----------
        linear : :pgmath:`Vector2`
            Linear acceleration
        angular : int
            Angular acceleration
            
            
        Returns
        -------
        :py:class:`SteeringOutput`
    """
    
    neg_steering = SteeringOutput()
    neg_steering.linear = -linear
    neg_steering.angular = -angular
    
    return neg_steering


class KinematicSteeringBehavior(object):
    """ Template KinematicSteeringBehavior class
    
    This class is a template to supply base methods for KinematicSteeringBehaviors.
    This class is meant to be subclassed since the methods here are just placeholders
    """
    
    def __repr__(self):
        """ If not overriden, returns class name """
        return type(self).__name__
    
    def draw_indicators(self, screen, offset = (lambda pos: pos)):
        """ Draws appropiate indicators for each :py:class:`KinematicSteeringBehavior`
        
        Parameters
        ----------
        screen: :pgsurf:`Surface`
            Surface in which to draw indicators, normally this would be the screen Surface
        offset: function, optional
            Function that applies an offset to the object's position
            
            This is meant to be used together with scrolling cameras,
            leave empty if your game doesn't implement one,it defaults 
            to a linear function f(pos) -> pos
        """
        pass

    def get_steering(self):
        """ Returns a steering request
        
        Returns
        -------
        :py:class:`SteeringOutput`
            Requested steering
        """
        return null_steering.copy()


class Seek(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Seek** a target
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    target: :py:class:`~gameobject.GameObject`
        Target to **Seek**
    """
    
    def __init__(self, character, target):
        self.character = character
        self.target = target
        self.steering = SteeringOutput()
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        start = offset(self.character.position)
        end = start + self.steering.linear
        pygame.draw.line(screen, colors.GREEN, start, end)
        
    def get_steering(self):
        # Get direction to the target
        self.steering.linear = self.target.position - self.character.position
        
        # Velocity is along this direction at full speed
        if(math_utils.is_not_null(self.steering.linear)):
            self.steering.linear.normalize_ip()
            self.steering.linear *= self.character.max_accel
        
        self.steering.angular = 0
        return self.steering
  
        
class Flee(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Flee** from a target
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    target: :py:class:`~gameobject.GameObject`
        Target to **Flee** from
    """
    
    def __init__(self, character, target):
        self.character = character
        self.target = target
        self.steering = SteeringOutput()
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        start = offset(self.character.position)
        end = start + self.steering.linear
        pygame.draw.line(screen, colors.GREEN, start, end)
        
    def get_steering(self):
        # Get direction to the target
        self.steering.linear = self.character.position - self.target.position
        
        # Velocity is along this direction at full speed
        if(math_utils.is_not_null(self.steering.linear)):
            self.steering.linear.normalize_ip()
            self.steering.linear *= self.character.max_accel
        
        return self.steering
        
class Arrive(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Arrive** at a target
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    target: :py:class:`~gameobject.GameObject`
        Target to **Arrive** at
    target_radius: int, optional
        Distance from the center of the target at which the character will stop
    slow_radius: int, optional
        Distance from the center of the target at which the character will start to slow down
    time_to_target: float, optional
        Estimated time, in seconds, to **Arrive** at the target
    """
    
    def __init__(self, character, target, target_radius = None, slow_radius = None, time_to_target = 0.2):
        # Complete unprovided values
        if target_radius is None:
            target_radius = int(math.sqrt((target.rect.height/2)**2 + (target.rect.width/2)**2)*2)
            
        if slow_radius is None:
            slow_radius = target_radius * 5
            
        self.character = character
        self.target = target
        self.time_to_target = time_to_target
        self.target_radius = target_radius
        self.slow_radius = slow_radius
        self.steering = SteeringOutput()
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        start = offset(self.character.position)
        end = start + self.steering.linear
        pygame.draw.line(screen, colors.GREEN, start, end)
        x, y = offset(self.target.position)
        pygame.gfxdraw.aacircle(screen, int(x), int(y), self.target_radius, (255, 0, 0))
        pygame.gfxdraw.aacircle(screen, int(x), int(y), self.slow_radius, (0, 0, 255))
        
    def get_steering(self):
        # Direction to target
        direction = self.target.position - self.character.position
        distance = direction.length()
            
        # If we are outside slow radius, go at max_speed
        if distance > self.slow_radius:
            target_speed = self.character.max_speed
        
        # If we are within target radius, make speed 0
        elif distance <= self.target_radius:
            self.steering = null_steering.copy()
            return self.steering
            
        # Determine 'slow' speed based on distance
        else:
            target_speed = self.character.max_speed*distance/self.slow_radius
        
        # Target velocity combines target_speed and direction
        target_velocity = direction
        if math_utils.is_not_null(target_velocity):
            target_velocity.normalize_ip()
            target_velocity *= target_speed
        
        # Finally, acceleration tries to get to target_velocity
        self.steering.linear = target_velocity - self.character.velocity
        self.steering.linear /= self.time_to_target
        
        # Clip acceleration
        if self.steering.linear.length() > self.character.max_accel:
            self.steering.linear.normalize_ip()
            self.steering.linear *= self.character.max_accel
        
        return self.steering
        
class Align(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Align** with the target's orientation
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    target: :py:class:`~gameobject.GameObject`
        Target to **Align** with it's orientation at
    target_radius: int, optional
        Distance, in degrees, from the target orientation at which the character will stop rotation
    slow_radius: int, optional
        Distance, in degrees, from the target orientation at which the character will start to slow rotation
    time_to_target: float, optional
        Estimated time, in seconds, to Align with the target's orientation
    """
    
    def __init__(self, character, target, target_radius = 1, slow_radius = 20, time_to_target = 0.1):
        self.character = character
        self.target = target
        self.time_to_target = time_to_target
        self.target_radius = target_radius
        self.slow_radius = slow_radius
        self.steering = SteeringOutput()
        
    def draw_indicators(self, screen, offset = (lambda pos: pos)):
        start = offset(self.character.position)
        factor = math_utils.get_bound_radius(self.character.rect) + 10
        end = start + math_utils.orientation_asvector(self.character.orientation + self.steering.angular)*factor
        pygame.draw.line(screen, colors.BLUE, start, end)
        
    def get_steering(self):
        # Get naive direction to target orientation
        rotation = self.target.orientation - self.character.orientation
        
        # Map result to (-pi, pi)
        rotation = math_utils.map_to_range(rotation)
        rotation_size = abs(rotation)
        
        # If we're there, return no steering
        if rotation_size < self.target_radius:
            target_rotation = 0
            
        # If outside slow_radius, use max_rotation
        elif rotation_size > self.slow_radius:
            target_rotation = self.character.max_rotation
            target_rotation *= rotation / rotation_size
        
        # Otherwise calculate appropiate target rotation    
        else:
            target_rotation = self.character.max_rotation * rotation_size / self.slow_radius
            target_rotation *= rotation / rotation_size
        
        # Calculate aprropiate angular accel to reach this rotation
        self.steering.angular = target_rotation - self.character.rotation / self.time_to_target
        
        # Clip if it's too large
        angular_accel = abs(self.steering.angular)
        if angular_accel > self.character.max_angular_accel:
            self.steering.angular /= angular_accel
            self.steering.angular *= self.character.max_angular_accel
        
        return self.steering
        
class VelocityMatch(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character match the velocity of the target
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    target: :py:class:`~gameobject.GameObject`
        Target to match it's velocity
    time_to_target: float, optional
        Estimated time, in seconds, to reach the target's velocity
    """
    
    def __init__(self, character, target, time_to_target = 0.1):
        self.character = character
        self.target = target
        self.time_to_target = time_to_target
        self.steering = SteeringOutput()
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        start = offset(self.character.position)
        end = start + self.steering.linear
        pygame.draw.line(screen, colors.GREEN, start, end)
        
    def get_steering(self):
        # Acceleration tries to get to the target velocity
        self.steering.linear = self.target.velocity - self.character.velocity
        self.steering.linear /= self.time_to_target
        
        # Clip acceleration if it's too large
        if self.steering.linear.length() > self.character.max_accel:
            self.steering.linear.normalize_ip()
            self.steering.linear *= self.character.max_accel
        
        return self.steering
        
class Pursue(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Purse** the target
     
    This behavior tries to predict the target's future position based on
    the direction it is currently moving, and then :py:class:`Seek` s that
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    target: :py:class:`~gameobject.GameObject`
        Target to **Pursue**
    max_prediction_time: float, optional
        Maximum time, in seconds, to look ahead while predicting future position
    """
    
    def __init__(self, character, target, max_prediction_time = 0.2):
        self.character = character
        self.target = target
        self.max_prediction_time = max_prediction_time
        self.seek = Seek(self.character, DummyGameObject())
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        self.seek.draw_indicators(screen, offset)
        
    def get_steering(self):
        # Calculate target to delegate to Seek
        # Calculate distance to target
        direction = self.target.position - self.character.position
        distance = direction.length()
        
        # Calculate current speed
        speed = self.character.velocity.length()
        
        # Check if speed is too small to give reasonable prediction
        if speed <= distance/self.max_prediction_time:
            prediction_time = self.max_prediction_time
        else:
            prediction_time = distance/speed
            
        # Update target coordinates
        self.seek.target.position = self.target.position
        self.seek.target.position += self.target.velocity * prediction_time
        
        return self.seek.get_steering()
        
class Evade(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Evade** the target
     
    This behavior tries to predict the target's future position based on
    the direction it is currently moving, and then :py:class:`Flee` s from that
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    target: :py:class:`~gameobject.GameObject`
        Target to **Evade**
    max_prediction_time: float, optional
        Maximum time, in seconds, to look ahead while predicting future position
    """
    
    def __init__(self, character, target, max_prediction_time = 0.2):
        self.character = character
        self.target = target
        self.max_prediction_time = max_prediction_time
        self.flee = Flee(self.character, DummyGameObject())
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        self.flee.draw_indicators(screen, offset)
        
    def get_steering(self):
        # Calculate target to delegate to Seek
        # Calculate distance to target
        direction = self.target.position - self.character.position
        distance = direction.length()
        
        # Calculate current speed
        speed = self.character.velocity.length()
        
        # Check if speed is too small to give reasonable prediction
        if speed <= distance/self.max_prediction_time:
            prediction_time = self.max_prediction_time
        else:
            prediction_time = distance/speed
            
        # Update target coordinates
        self.flee.target.position = self.target.position
        self.flee.target.position += self.target.velocity * prediction_time
        
        return self.flee.get_steering()
        
class Face(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Face** the target
     
    This behavior creates a :py:class:`~gameobject.DummyGameObject` that 
    is looking in the direction of the target and then :py:class:`Align` s
    with that dummy's orientation
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    target: :py:class:`~gameobject.GameObject`
        Target to **Face**
    target_radius: int, optional
        Distance, in degrees, from the target orientation at which the character will stop rotation
    slow_radius: int, optional
        Distance, in degrees, from the target orientation at which the character will start to slow rotation
    time_to_target: float, optional
        Estimated time, in seconds, to **Face** the target
    """
    def __init__(self, character, target, target_radius = 1, slow_radius = 10, time_to_target = 0.1):
        self.character = character
        self.target = target
        self.align = Align(self.character, DummyGameObject(), target_radius, slow_radius, time_to_target)
        
    def draw_indicators(self, screen, offset = (lambda pos: pos)):
        self.align.draw_indicators(screen, offset)
        
    def get_steering(self):
        # Calculate target to delegate to Align
        # Calculate direction to target
        direction = self.target.position - self.character.position
        
        # If distance is 0, set dummy target to original target position
        if direction.length() == 0:
            self.align.target.orientation = self.target.orientation
        # Otherwise calculate orientation based in target direction
        else:
            self.align.target.orientation = math_utils.get_angle_from_vector(direction)
        
        return self.align.get_steering()
        
class LookWhereYoureGoing(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Look Where He's Going**
     
    This behavior makes the character face in the direction it's moving
    by creating  a :py:class:`~gameobject.DummyGameObject` that 
    is looking in the direction of the character's velocity and then
    it :py:class:`Align` s with that.
    
    This behavior is meant to be used in combination with other behaviors,
    see :py:class:`steering.blended.BlendedSteering` .
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    target_radius: int, optional
        Distance, in degrees, from the target orientation at which the character will stop rotation
    slow_radius: int, optional
        Distance, in degrees, from the target orientation at which the character will start to slow rotation
    time_to_target: float, optional
        Estimated time, in seconds, to **LookWhereYoureGoing**
    """
    
    def __init__(self, character, target_radius = 1, slow_radius = 20, time_to_target = 0.1):
        self.character = character
        self.align = Align(self.character, DummyGameObject(), target_radius, slow_radius, time_to_target)
        
    def get_steering(self):
        # If no velocity, return null steering
        if self.character.velocity.length() == 0:
            return null_steering.copy()
            
        # Calculate target orientation based on character velocity
        self.align.target.orientation = math_utils.get_angle_from_vector(self.character.velocity)
            
        return self.align.get_steering()
    
class Wander(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Wander**
     
    This behavior makes the character move with it's maximum speed in a 
    random direction that feels smooth, meaning that it does not rotate
    too abruptly. This generates a target in front of the character and 
    :py:class:`Seek` s it while applying `:py:class:`LookWhereYoureGoing`,
    you can use the :py:meth:`KinematicSteeringBehavior.draw_indicators()`
    to see how the target is generated. This Behavior also uses 
    :py:class:`LookWhereYoureGoing`.
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    wander_offset: int, optional
        Distance in front of the character to generate target to :py:class:`Seek`
    wander_radius: int, optional
        Radius of the circumference in front of the character in which the target will generated
    wander_rate: int, optional
        Angles, in degrees, that the target is allowed to move along the circumference
    align_target_radius: int, optional
        Distance, in degrees, from the target orientation at which the character will stop rotation
    slow_radius: int, optional
        Distance, in degrees, from the target orientation at which the character will start to slow rotation
    align_time: float, optional
        Estimated time, in seconds, to **LookWhereYoureGoing**
    """
    def __init__(self, character, wander_offset = 50, wander_radius = 15, wander_rate = 20):
                 #align_target_radius = 1, align_slow_radius = 10, align_time = 0.2,
                 #draw = True):
                     
        self.character = character
        self.wander_offset = wander_offset
        self.wander_radius = wander_radius
        self.wander_rate = wander_rate
        self.wander_orientation = self.character.orientation
        self.seek = Seek(self.character, DummyGameObject())
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        x, y = offset(self.seek.target.position)
        pygame.gfxdraw.filled_circle(screen, int(x), int(y), 2, (255, 0, 0))
        x, y = offset(self.character.position + (math_utils.orientation_asvector(self.character.orientation) * self.wander_offset))
        pygame.gfxdraw.aacircle(screen, int(x), int(y), self.wander_radius, (0, 255, 0))
        
    def get_steering(self):
        # Calculate target to delegate to seek
        # Update wander orientation
        self.wander_orientation += math_utils.random_binomial() * self.wander_rate
        # Calculate combined target_orientation
        target_orientation = self.wander_orientation + self.character.orientation
        
        # Calculate center of wander circle
        target_position = self.character.position + (math_utils.orientation_asvector(self.character.orientation) * self.wander_offset)
        
        # Calculate target location
        target_position += math_utils.orientation_asvector(target_orientation) * self.wander_radius
        
        # Delegate to seek
        self.seek.target.position = target_position
        return self.seek.get_steering()


class FollowPath(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Follow a Path**
     
    This behavior makes the character follow a particular
    :py:class:`~.path.Path`. It will do so until the character
    has traversed all points in it.
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    path: :py:class:`steering.path.Path`
        Path that will be Followed
    """
    
    def __init__(self, character, path):
        self.character = character
        self.path = path
        self.seek = Seek(self.character, DummyGameObject())
        self.seek.target.position = next(self.path)
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        self.seek.draw_indicators(screen, offset)
        
        for point in self.path.as_list():
            x, y = offset(point)
            pygame.gfxdraw.filled_circle(screen, int(x), int(y), 2, (0, 0, 255))
        x, y = offset(self.seek.target.position)
        pygame.gfxdraw.filled_circle(screen, int(x), int(y), 3, (255, 0, 0))
                
    def __repr__(self):
        return 'FollowPath ' + str(self.path)
        
    def get_steering(self):
        # Calculate to delegate to seek
        self.seek.target.position = self.path.current()
        distance = (self.character.position - self.seek.target.position).length()
        if distance < 50:   # THIS MIGHT NEED SOME REVISIOn
            try:
                self.seek.target.position = next(self.path)
            except StopIteration:
                return null_steering.copy()
        
        # Delegate to Seek
        return self.seek.get_steering()


class Separation(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Separate** itself from a list of targets
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    targets: list(:py:class:`~gameobject.GameObject`)
        Targets to stay separated from
    treshold : int, optional
        Distance from any of the targets at which the character will start separate from them
    """
    
    def __init__(self, character, targets, treshold = None):
        # Complete unprovided values
        if treshold is None:
            treshold = int(math.sqrt((character.rect.height/2)**2 + (character.rect.width/2)**2)*3)
        
        self.character = character
        self.targets = targets
        self.treshold = treshold
        self.steering = SteeringOutput()
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        start = offset(self.character.position)
        end = start + self.steering.linear
        pygame.draw.line(screen, colors.GREEN, start, end)
        
        x, y = offset(self.character.position)
        pygame.gfxdraw.aacircle(screen, int(x), int(y), self.treshold, (255, 0, 0))
        
    def get_steering(self):
        
        for target in self.targets:
            self.steering = SteeringOutput()
            
            # Check if target is close
            direction = self.character.position - target.position
            distance = direction.length()
            
            # Make sure there's a direction
            if distance == 0:
                direction[1] = -1
            
            if distance < self.treshold:
                # Calculate strength of repulsion
                strength = self.character.max_accel * (self.treshold - distance) / self.treshold
                # Add the acceleration
                direction.normalize_ip()
                self.steering.linear += strength * direction
                
        return self.steering
        

class CollisionAvoidance(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Avoid Collision** with a list of targets
    
    This behavior looks at the velocities of the character and the targets
    to determine if they will collide in the next few loops, and if they will,
    it accelerates away from the collision point
    
    This behavior is meant to be used in combination with other behaviors,
    see :py:class:`steering.blended.BlendedSteering` .
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    targets: list(:py:class:`~gameobject.GameObject`)
        Targets to avoid collision with
    radius : int, optional
        Distance at which the future positions of the character and any
        target are are considered as *colliding*
    """
    
    def __init__(self, character, targets, radius = None):
        # Complete unprovided values
        if radius is None:
            radius = int(math_utils.get_bound_radius(character.rect)*2)
            
        self.character = character
        self.targets = targets
        self.radius = radius
        self.steering = SteeringOutput()
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        start = offset(self.character.position)
        end = start + self.steering.linear
        pygame.draw.line(screen, colors.GREEN, start, end)
        
        x, y = offset(self.character.position + self.character.velocity)
        pygame.gfxdraw.aacircle(screen, int(x), int(y), self.radius, (255, 0, 0))
        
        for target in self.targets:
            x, y = offset(target.position + target.velocity)
            pygame.gfxdraw.aacircle(screen, int(x), int(y), self.radius, (255, 0, 0))
        
    def get_steering(self):
        # Calculate future character pos
        char_future_pos = self.character.position + self.character.velocity
        closest_target = None
        
        # See if any target comes close enough
        min_distance = float('inf')
        for target in self.targets:
            target_future_pos = target.position + target.velocity
            relative_pos = char_future_pos - target_future_pos
            distance = relative_pos.length()
            
            if distance > self.radius:
                continue
                
            if distance < min_distance:
                closest_target = target
                closest_relative_pos = relative_pos
                min_distance = distance
        
        # If no target is close enough, return no sterring
        if closest_target is None:
            self.steering = null_steering.copy()
            return self.steering
        
        # Otherwise, calculate avoidance path
        if math_utils.is_not_null(closest_relative_pos):
            closest_relative_pos.normalize_ip()
        self.steering.linear = closest_relative_pos * self.character.max_accel
        
        return self.steering
        

class ObstacleAvoidance(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Avoid Obstacles**
    
    This behavior looks ahead in the current direction the character is 
    moving to see if it will collide with any obstacle, and if it does, 
    creates a target *away* from the collision point and :py:class:`Seek` s that.
    
    The difference between this and :py:class:`CollisionAvoidance` is that
    the **Obstacles** are considered to be a rectangular shape of a any size,
    while the targets are normally almost-square-sized.
    
    This behavior is meant to be used in combination with other behaviors,
    see :py:class:`steering.blended.BlendedSteering` .
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    obstacles: list(:py:class:`~gameobject.GameObject`)
        Obstacles to avoid collision with
    avoid_distance: int, optional
        Distance from the collision point at which the target that 
        the algorithm uses to avoid collision will be generated
    lookahead: int, optional
        Distance to *look ahead* in the direction of the player's velocity
    """
    
    def __init__(self, character, obstacles, avoid_distance = None, lookahead = None):
        # Complete unprovided values
        if lookahead is None:
            lookahead = int(math_utils.get_bound_radius(character.rect)*4)
            
        if avoid_distance is None:
            avoid_distance = int(math_utils.get_bound_radius(character.rect)*3)
            
        self.character = character
        self.obstacles = obstacles
        self.avoid_distance = avoid_distance
        self.lookahead = lookahead
        self.seek = Seek(self.character, DummyGameObject())
        
        # For indicator drawing
        self.closest_intersection = None
        
    def draw_indicators(self, screen, offset = lambda pos: pos):
        # Velocity
        self.seek.draw_indicators(screen, offset)
        
        # Ray vector
        start = offset(self.character.position)
        if math_utils.is_not_null(self.character.velocity):
            end = start + self.character.velocity.normalize() * self.lookahead
        else:
            end = start + self.character.velocity * self.lookahead
        pygame.draw.line(screen, colors.YELLOW, start, end)
        
        # Intersection point
        if self.closest_intersection:
            x, y = offset(self.closest_intersection)
            pygame.gfxdraw.filled_circle(screen, int(x), int(y), 2, colors.RED)
        
            # Seek target
            x, y = offset(self.seek.target.position)
            pygame.gfxdraw.filled_circle(screen, int(x), int(y), 2, colors.BLUE)
        
    def get_steering(self):
        # Cast ray vector
        ray_vector = pygame.Vector2(self.character.velocity)
        if math_utils.is_not_null(ray_vector):
            ray_vector.normalize_ip()
        ray_vector *= self.lookahead
        closest_intersection = None
        
        # Look for the closest collision
        closest_distance = float('inf')
        closest_intersection = None
        closest_intersection_line = None
        for obstacle in self.obstacles:
            for line in obstacle.get_lines():
                ray_line = [self.character.position, self.character.position + ray_vector]
                intersection = math_utils.lines_intersect(ray_line, line)
                if intersection is not None:
                    distance = (intersection - self.character.position).length()
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_intersection = intersection
                        closest_intersection_line = line
        
        self.closest_intersection = closest_intersection
        # If there was no collision return null steering
        if closest_intersection is None:
            return null_steering.copy()
        
        # Otherwise, calculate target to delegate to Seek
        # Get RHS and LHS perpendicular points and see which is closer 
        # to the player
        p1, p2 = math_utils.get_perpendicular(closest_intersection_line)
        p1.normalize_ip()
        p2.normalize_ip()
        p1 = closest_intersection + p1*self.avoid_distance
        p2 = closest_intersection + p2*self.avoid_distance
        dis1 = (p1 - self.character.position).length()
        dis2 = (p2 - self.character.position).length()
        closest = p1 if dis1 < dis2 else p2
        
        # Delegate to seek
        self.seek.target.position = closest
        return self.seek.get_steering()
                

class NullSteering(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that makes the character **Stay Still** """
    
    def get_steering(self):
        return null_steering.copy()
        
class Stationary(KinematicSteeringBehavior):
    
    def __init__(self, character):
        self.character = character
        self.steering = SteeringOutput()
    
    def get_steering(self):
        self.steering.linear = -self.character.velocity
        
        if math_utils.is_not_null(self.steering.linear):
            self.steering.linear.normalize_ip()
            self.steering.linear *= self.character.max_accel
            
        return self.steering

        
class Drag(KinematicSteeringBehavior):
    """ :py:class:`KinematicSteeringBehavior` that applies a **Drag** to the character
    
    This behavior should be applied to every :py:class:`~gameobject.GameObject`
    in every loop (unless it's meant to be permanently stationary). It
    applies an acceleration contrary to it's current linear and angular
    velocity.
    
    Parameters
    ----------
    strenght: float, optional
        The strength of the drag to apply, should be a number in the
        range (0, 1], any number outside of that range will have 
        unexpected behavior.
    """
    
    def __init__(self, linear_strength = 10, angular_strength = 1):
        self.linear_strength = linear_strength
        self.angular_strength = angular_strength
        self.steering = SteeringOutput()
        
    def get_steering(self, character):
        """ Returns steering with a character's drag
        
        Parameters
        ----------
        character: :py:class:`~gameobject.GameObject`
        """
        
        if math_utils.is_not_null(character.velocity):
            linear_direction = -character.velocity
            linear_direction.normalize_ip()    
            self.steering.linear = linear_direction * self.linear_strength
        else:
            self.steering.linear = pygame.Vector2(0, 0)
        
        if character.rotation == 0:
            self.steering.angular = 0
        else:
            angular_direction = -character.rotation / abs(character.rotation)
            self.steering.angular = angular_direction*self.angular_strength
        
        return self.steering
