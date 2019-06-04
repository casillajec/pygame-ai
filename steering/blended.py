# -*- coding: utf-8 -*-
""" Blended Steering Behaviors

This module implements a class that Blends a list of
:py:class:`~.KinematicSteeringBehavior` s and provides
a weighted sum of their outputs as a steering request.

This is the bread and butter of **Steering Behaviors** since it easily 
combines different behaviors that allow for semi-complex AI behaviors.

Derives from :py:class:`~.kinematic.KinematicSteeringBehavior`.

Example
--------

This is how you would normally create your own :py:class:`~BlendedSteering` ,
in this case we are making a more complex version of :py:class:`~steering.kinematic.Arrive`
where the character looks where it's going and also tries to avoid any
obstacle in the way.

.. code-block:: python

    flocking_behavior = BlendedSteering(
        character = character
        behaviors = [
            BehaviorAndWeight(kinematic.Arrive(character, target), weight = 1),
            BehaviorAndWeight(kinematic.LookWhereYoureGoing(character), weight = 1),
            BehaviorAndWeight(kinematic.ObstacleAvoidance(character, obstacles), weight = 2),
        ]
    )
    
    
This module also includes a couple of pre-implemented :py:class:`BlendedSteering`.
    
    
.. todo:: Make BehaviorAndWeight prettier, maybe use named tuples?

"""

from . import kinematic
from . import path
from pygame_ai.gameobject import DummyGameObject

class BehaviorAndWeight(object):
    """ Container for Behavior and Weight values
    
    Parameters
    ----------
    behavior: :py:class:`~.KinematicSteeringBehavior`
    weight: int
    """
    
    def __init__(self, behavior, weight):
        self.behavior = behavior
        self.weight = weight

class BlendedSteering(kinematic.KinematicSteeringBehavior):
    """ Base Blended Steering
    
    This class provides methods neccesary to combine the list of steering
    behaviors and produce a single :py:class:`~.kinematic.SteeringOutput`.
    
    Derives from :py:class:`~.KinematicSteeringBehavior`, currently 
    :py:class:`BlendedSteering` with :py:class:`~.StaticSteeringBehavior`
    is not supported.
    
    Parameters
    ----------
    character: :py:class:`~gameobject.GameObject`
        Character with this behavior
    behaviors: list(:py:class:`~.BehaviorAndWeight`)
        List of behaviors that compose this :py:class:`~.BlendedSteering`
    """
    
    def __init__(self, character, behaviors):
        self.character = character
        self.behaviors = behaviors
        
    def __repr__(self):
        return 'BlendedSteering '+super(BlendedSteering, self).__repr__()
        
    def draw_indicators(self, screen, offset = (lambda pos: pos)):
        """ Draws appropiate indicators for this :py:class:`BlendedSteering`
        
        Draws the indicators of all :py:class:`~.KinematicSteeringBehavior`
        that compose this :py:class:`~.BlendedSteering`.
        
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
        for behavior in self.behaviors:
            behavior.behavior.draw_indicators(screen, offset)
        
    def get_steering(self):
        """ Returns the combined steering request of this :py:class:`~BlendedSteering`
        
        Returns
        -------
        :py:class:`SteeringOutput`
            Requested steering
        """
        # Output steering for accumulating
        steering = kinematic.SteeringOutput()
        
        # Accumulate all accelerations
        for behavior in self.behaviors:
            steering += behavior.behavior.get_steering() * behavior.weight
            
        # Crop the results and return
        steering_lin_accel = steering.linear.length()
        if steering_lin_accel > self.character.max_accel:
            steering.linear /= steering_lin_accel
            steering.linear *= self.character.max_accel
        
        steering_angular_accel = steering.angular
        if steering_angular_accel > self.character.max_angular_accel:
            steering.angular /= steering_angular_accel
            steering.angular *= self.character.max_angular_accel
            
        return steering
        
class Flocking(BlendedSteering):
    """ :py:class:`~.BlendedSteering` that makes the character move in a flock-like way
    
    This behavior is meant to be used with several characters, they will all
    try to **Arive** at the same target location while **Looking Where They're Going**
    and keeping **Separated** from eachother.
    
    Parameters
    ----------
    character: :py:class:`~.GameObject`
    swarm: iterable(:pgsprite:`Sprite`)
        Rest of the entities that conform the Flock
    target: :py:class:`~.GameObject`
    """
    
    def __init__(self, character, swarm, target):
        behaviors = [
            BehaviorAndWeight(kinematic.Separation(character, swarm), 3),
            BehaviorAndWeight(kinematic.Arrive(character, target), 1),
            BehaviorAndWeight(kinematic.LookWhereYoureGoing(character), 1),
        ]
        super(Flocking, self).__init__(character, behaviors)
        
class Wander(BlendedSteering):
    """ :py:class:`~.BlendedSteering` that makes the character **Wander** around.
    
    This behaviors is a more complex version of :py:class:`~.kinematic.Wander`
    that also tries to **Avoid Obstacles**.
    
    Parameters
    ----------
    character: :py:class:`~.GameObject`
    obstacles: iterable(:pgsprite:`Sprite`)
        Solid obstacles
    """
    
    def __init__(self, character, obstacles):
        behaviors = [
            # Wander
            BehaviorAndWeight(
                kinematic.Wander(character),
                weight = 1),
            # ObstacleAvoidance
            BehaviorAndWeight(
                kinematic.ObstacleAvoidance(character, obstacles),
                weight = 4),
            # LookWhereYoureGoing
            BehaviorAndWeight(
                kinematic.LookWhereYoureGoing(character),
                weight = 2),
        ]
        super(Wander, self).__init__(character, behaviors)
        
class Arrive(BlendedSteering):
    """ :py:class:`~.BlendedSteering` that makes the character **Arrive** at a target
    
    This is behavior is a more complex version of :py:class:`~.kinematic.Arrive`
    that also **Looks Where it's Going** and tries to **Avoid Obstacles**.
    
    Parameters
    ----------
    character: :py:class:`~.GameObject`
    target: :py:class:`~.GameObject`
    obstacles: iterable(:pgsprite:`Sprite`)
        Solid obstacles
    """
    
    def __init__(self, character, target, obstacles, target_radius = None, slow_radius = None):
        behaviors = [
            # Arrive
            BehaviorAndWeight(
                kinematic.Arrive(character, target, target_radius, slow_radius),
                weight = 1),
            # ObstacleAvoidance    
            BehaviorAndWeight(
                kinematic.ObstacleAvoidance(character, obstacles),
                weight = 2),
            # LookWhereYoureGoing
            BehaviorAndWeight(
                kinematic.LookWhereYoureGoing(character),
                weight = 1),
        ]
        super(Arrive, self).__init__(character, behaviors)
        
class Surround(BlendedSteering):
    """ :py:class:`~.BlendedSteering` that makes the character **Surround** a target
    
    This behavior uses :py:class:`~.FollowPath` and :py:class:`~.Face`
    to make the character revolve around the target while looking at it.
    
    Parameters
    ----------
    character: :py:class:`~.GameObject`
    target: :py:class:`~.GameObject`
    radius: int
        The radius of the circle the character will surround the target with
    """
    def __init__(self, character, target, radius):
        circumpath = path.PathCircumference(lambda: target.position, radius)
        behaviors = [
            BehaviorAndWeight(
                kinematic.FollowPath(character, circumpath),
                weight = 2),
            BehaviorAndWeight(
                kinematic.Face(character, target),
                weight = 1),
        ]
        super(Surround, self).__init__(character, behaviors)
