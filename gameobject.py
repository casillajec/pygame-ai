# -*- coding: utf-8 -*-
""" General-Purpose Game Object

    This module implements the GameObject class, core of this AI engine,
    along with other useful classes, methods and constants
"""
import pygame
from pygame_ai.utils import list_utils

null_surface = pygame.Surface((0, 0))
""" (:pgsurf:`Surface`) : Empty Surface with size 0 """

class GameObject(pygame.sprite.Sprite):
    """ General-Purpose Game Object.
    
    Derives from :pgsprite:`Sprite`.
    
    Holds values relevant to any non-static entity in the game.
    
    Parameters
    ----------
    
    img_surf: :pgsurf:`Surface`
        It is asigned to self.image, defaults to :const:`null_surface`
    pos: list_like(int, int), optional
        Initial Position, it is assigned to self.rect.center
    max_speed: int, optional
        Maximum linear speed
    max_accel: int, optional
        Maximum linear acceleration
    max_rotation: int, optional
        Maximum angular speed
    max_angular_accel: int, optional
        Maximum angular acceleration
    
    
    This class exposes the following public properties and methods
    
    Attributes
    ----------
    
    image: :pgsurf:`Surface`
        Surface to be blited to screen
    rect: :pgrect:`Rect`
        Derived from image, it's center is the GameObejct's position
    position: :pgmath:`Vector2`
        Current position
    velocity: :pgmath:`Vector2`
        Current velocity
    max_speed: int
        Maximum linear speed
    max_accel: int
        Maximum linear acceleration
    orientation: int
        Current orientation in degrees
    rotation: int
        Current angular velocity
    max_rotation: int
        Maximum angular speed
    max_angular_accel: int
        Maximum angular acceleration
    """
    def __init__(self, img_surf = null_surface, pos = (0, 0), max_speed = 30, max_accel = 20, max_rotation = 60, max_angular_accel = 50):
        """
        Constructor
        """
        super(GameObject, self).__init__()
        self.original_image = img_surf
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.velocity = pygame.Vector2(0, 0)
        self.max_speed = max_speed
        self.max_accel = max_accel
        self.orientation = 0
        self.rotation = 0
        self.max_rotation = max_rotation
        self.max_angular_accel = max_angular_accel
    
    @property
    def position(self):
        return pygame.Vector2(self.rect.center)
    
    @position.setter
    def position(self, pos):
        self.rect.center = pos

    def steer(self, steering, tick):
        """ Updates GameObject's velocity and rotation
        
        Parameters
        ----------
        steering: :py:class:`.kinematic.SteeringOutput` or :py:class:.`static.SteeringOutput`
            The steering request to update velocity and rotation
        tick: int
            Time passed since the last loop
        """
        self.velocity += steering.linear * tick
        self.rotation += steering.angular * tick
        
        if self.velocity.length() > self.max_speed:
            self.velocity.normalize_ip()
            self.velocity *= self.max_speed
            
    def steer_x(self, steering, tick):
        """ Updates GameObject's velocity along the x axis
        
        Parameters
        ----------
        steering: :py:class:`.kinematic.SteeringOutput` or :py:class:.`static.SteeringOutput`
            The steering request to update velocity and rotation
        tick: int
            Time passed since the last loop
        """
        steering_x = steering.copy()
        steering_x.linear[1] = 0
        steering_x.angular = 0
        
        self.velocity += steering_x.linear * tick
        
        if self.velocity[0] > self.max_speed:
            self.velocity[0] = self.max_speed
        #self.steer(steering_x, tick)
        
    def steer_y(self, steering, tick):
        """ Updates GameObject's velocity along the y axis
        
        Parameters
        ----------
        steering: :py:class:`.kinematic.SteeringOutput` or :py:class:.`static.SteeringOutput`
            The steering request to update velocity and rotation
        tick: int
            Time passed since the last loop
        """
        steering_y = steering.copy()
        steering_y.linear[0] = 0
        steering_y.angular = 0
        
        self.velocity += steering_y.linear * tick
        
        if self.velocity[1] > self.max_speed:
            self.velocity[1] = self.max_speed
        
        #self.steer(steering_y, tick)
        
    def steer_angular(self, steering, tick):
        """ Updates GameObject's rotation
        
        Parameters
        ----------
        steering: :py:class:`.kinematic.SteeringOutput` or :py:class:.`static.SteeringOutput`
            The steering request to update velocity and rotation
        tick: int
            Time passed since the last loop
        """
        steering_angular = steering.copy()
        steering_angular.linear[0], steering_angular.linear[1] = 0, 0
        self.steer(steering_angular)
        
    def get_lines(self):
        """ Reruns what it returns, can you guess what it is? """
        left = [self.rect.topleft, self.rect.bottomleft]
        top = [self.rect.topleft, self.rect.topright]
        right = [self.rect.topright, self.rect.bottomright]
        bottom = [self.rect.bottomright, self.rect.bottomleft]
        
        return [left, top, right, bottom]
        

class DummyGameObject(GameObject):
    """ A Dummy with :py:class:`GameObject` properties
    
    Derives from :py:class:`GameObject`.
    
    Used for quick instantiation when creating :py:class:`GameObject` s
    that will only be used as palceholders and are not meant to appear
    on screen.
    
    Parameters
    ----------
    
    position: list_like(int, int)
        Current position
    """
    def __init__(self, position = (0, 0)):
        """ Constructor
        """
        super(DummyGameObject, self).__init__(pos = position, max_speed = 0, max_accel = 0, max_rotation = 0, max_angular_accel = 0)
