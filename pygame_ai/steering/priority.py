# -*- coding: utf-8 -*-
""" Priority Steering Behaviors

This module implements a class that holds a list of
:py:class:`~.kinematic.KinematicSteeringBehavior`\ s and applies them in order,
keeping only the first one that produces an output greater than a certain
treshold. This means that some behaviors which are considered more important
(like :py:class:`~.kinematic.ObstacleAvoidance` and 
:py:class:`~.kinematic.CollisionAvoidance`) but are not always neccesary 
to reach the character's goal can be ignored when they don't produce a 
meaningful output, it also means that when they do produce a meaningful 
output they will be the only ones in action.

This is a very simple form of decision making that involves only steering
algorithms, and therefore it is classified as a steering behavior.

Derives from :py:class:`~.kinematic.KinematicSteeringBehavior`.


Example
--------

This is how you would normally create your own :py:class:`~PrioritySteering`\ ,
in this case we are making a behavior that will most of the time **Pursue**
a target, but will prioritize **Avoiding Obstacles** when that behavior
returns a steering greater than the treshold.

.. code-block:: python

    mybehavior = PrioritySteering(
        behaviors = [
            kinematic.ObstacleAvoidance(character, obstacles),
            kinematic.Pursue(character, target),
        ],
    )

"""

from . import kinematic
from . import blended
from . import path


class PrioritySteering(kinematic.KinematicSteeringBehavior):
    
    def __init__(self, behaviors, epsilon = 0.1):
        self.behaviors = behaviors
        self.epsilon = epsilon
        
    def __repr__(self):
        return 'PrioritySteering '+super(PrioritySteering, self).__repr__()
        
    def draw_indicators(self, screen, offset = (lambda pos: pos)):
        for behavior in self.behaviors:
            behavior.draw_indicators(screen, offset)
    
    def get_steering(self):
        
        for behavior in self.behaviors:
            # Get behavior's steering
            steering = behavior.get_steering()
            
            # If any of it's components surpases the treshold, return it
            if steering.linear.length() > self.epsilon or abs(steering.angular) > self.epsilon:
                return steering
                
        # If we get here, no output surpased the treshold
        # Return the last group's steering as small as it is
        return steering
        
class OscilateHorizontally(PrioritySteering):
    
    def __init__(self, character, target, solid_entities, width = 160, height = 80, start_x = 0):
        
        def mypath(self, i):
            x, y = self.center()
            a = [(x - width//2, y - height), (x, y - height), (x + width//2, y - height)]
            return a[i]
        
        hpath = path.MirroredPath(mypath, domain_end = 2)
        hpath.center = lambda: target.position
        hpath.x = start_x
        behaviors = [
            kinematic.CollisionAvoidance(character, solid_entities),
            kinematic.FollowPath(character, hpath),
        ]
        super(OscilateHorizontally, self).__init__(behaviors, epsilon = 10)

