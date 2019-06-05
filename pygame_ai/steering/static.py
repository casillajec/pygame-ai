# -*- coding: utf-8 -*-
""" Static movement

This module implements a series of classes and methods that emulate
the behavior of objects moving in a 2D space in a static way
(not involving acceleration)

Notes
-----
    This might need a slightly better explaination
"""
import random

import pygame

from pygame_ai.utils import math_utils

class SteeringOutput(object):
    """ Container for Steering data
    
    This class is used as a container for the  output of the 
    :py:class:`~StaticSteeringBehavior` algorithms.
        
    Parameters
    ----------
    velocity : :pgmath:`Vector2`, optional
        Linear velocity, defaults to (0, 0)
    rotation : int, optional
        Angular velocity, defaults to 0
        
    Attributes
    ----------
    velocity : :pgmath:`Vector2`
        Linear velocity
    rotation : int
        Angular velocity
    """
    
    def __init__(self, velocity = None, rotation = None):
        if velocity is None:
            velocity = pygame.Vector2(0, 0)
        self.velocity = velocity
        if rotation is None:
            rotation = 0
        self.rotation = rotation
        
    def update(self, gameobject, tick):
        """ Update a :py:class:`~gameobject.GameObject`'s velocity and rotation
        
        This method should be called once per loop, it updates the given 
        :py:class:`gameobject.GameObject`'s velocity and rotation based 
        on this :py:class:`~SteeringOutput`'s acceleration request
        
        Parameters
        ----------
        gameobject : :py:class:`~gameobject.GameObject`
            The :py:class:`GameObject` that will be updated
        tick : int
            Time transcurred since last loop
        """
        gameobject.velocity += self.linear * tick
        gameobject.rotation += self.rotation * tick
        
        if gameobject.velocity.length() > gameobject.max_speed:
            gameobject.velocity.normalize_ip()
            gameobject.velocity *= gameobject.max_speed
        
null_steering = SteeringOutput(velocity = pygame.Vector2(0, 0), rotation = 0)
""":py:class:`SteeringOutput` : Constant with 0 linear velocity and 0 angular velocity """

class StaticSteeringBehavior(object):
    """ Template StaticSteeringBehavior class
    
    This class is a template to supply base methods for StaticSteeringBehaviors.
    This class is meant to be subclassed since the methods here are just placeholders
    """
    
    def __repr__(self):
        """ If not overriden, returns class name """
        return type(self).__name__
    
    def draw_indicators(self, screen, offset = (lambda pos: pos)):
        """ Draws appropiate indicators for each :py:class:`~StaticSteeringBehavior`
        
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
        return null_steering

class Seek(StaticSteeringBehavior):
    """ :py:class:`~StaticSteeringBehavior` that makes the character **Seek** a target
    
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
        
    def get_steering(self):
        # Create structure for output
        steering = SteeringOutput()
        
        # Get direction to the target
        steering.velocity = self.target.position - self.character.position
        # Velocity is along this direction at full speed
        if(steering.velocity[0] != 0 or steering.velocity[1] != 0):
            steering.velocity.normalize_ip()
            steering.velocity *= self.character.max_speed
        # Face in the direction of velocity
        if(math_utils.is_not_null(steering.velocity)):
            self.character.orientation = math_utils.get_angle_from_vector(steering.velocity)
        
        # Return the steering
        steering.rotation = 0
        return steering
        
class Flee(StaticSteeringBehavior):
    """ :py:class:`~StaticSteeringBehavior` that makes the character **Flee** from a target
    
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
        
    def get_steering(self):
        
        # Create structure for output
        steering = SteeringOutput()
        
        # Get direction to the target
        steering.velocity = self.character.position - self.target.position
        # Velocity is along this direction at full speed
        if(steering.velocity[0] != 0 or steering.velocity[1] != 0):
            steering.velocity.normalize_ip()
            steering.velocity *= self.character.max_speed
        # Face in the direction of velocity
        if(math_utils.is_not_null(steering.velocity)):
            self.character.orientation = math_utils.get_angle_from_vector(steering.velocity)
        
        # Return the steering
        steering.rotation = 0
        return steering
        
class Arrive(StaticSteeringBehavior):
    """ :py:class:`~StaticSteeringBehavior` that makes the character **Arrive** at a target
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    target: :py:class:`~gameobject.GameObject`
        Target to **Arrive** at
    radius: int, optional
        Distance from the center of the target at which the character will stop
    time_to_arrive: float, optional
        Estimated time, in seconds, to **Arrive** at the target
    """
    
    def __init__(self, character, target, radius = None, time_to_arrive = 0.25):
        # Complete unprovided values
        if radius is None:
            radius = int(math.sqrt((target.rect.height/2)**2 + (target.rect.width/2)**2)*1.5)
        self.character = character
        self.target = target
        self.radius = radius
        self.time_to_arrive = time_to_arrive
        
    def get_steering(self):
        # Create structure for output
        steering = SteeringOutput()
        
        # Get direction to the target
        steering.velocity = self.target.position - self.character.position
        # Check if we're within radius
        if steering.velocity.length() < self.radius:
            return null_steering
            
        # Clip to get there in time_to_arrive
        steering.velocity /= self.time_to_arrive
        
        # If it is too fast, clip it to character's speed
        if steering.velocity.length() > self.character.max_speed:
            steering.velocity.normalize_ip()
            steering.velocity *= self.character.max_speed
            
        # Face in the direction of velocity
        if(math_utils.is_not_null(steering.velocity)):
            self.character.orientation = math_utils.get_angle_from_vector(steering.velocity)
        
        # Return the steering
        steering.rotation = 0
        
        return steering
        
class Wander(StaticSteeringBehavior):
    """ :py:class:`~StaticSteeringBehavior` that makes the character **Wander**
     
    This behavior makes the character move with it's maximum speed in a 
    particular direction for a random period of time, after that the
    character's orientation is changed randomly using the character's
    :py:attr:`~gameobject.GameObject.max_rotation`.
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    """
    
    def __init__(self, character):
        self.character = character
        self.counter = 0
        self.max_timer = random.randint(7, 13)
        
    def get_steering(self):
        # Output steering
        steering = SteeringOutput()
        steering.rotation = 0
        
        # Get velocity from orientation
        steering.velocity = math_utils.orientation_asvector(self.character.orientation)
        steering.velocity *= self.character.max_speed
        
        # Change orientation randomly after random amount of iterations
        if(self.counter > self.max_timer):
            steering.rotation = (random.random() - random.random())*self.character.max_rotation
            self.counter = 0
            self.max_timer = random.randint(7, 13)
        self.counter += 1
        
        return steering
        
        
        
