Welcome to Pygame AI's Documentation!
=====================================

Pygame AI is a package that aims at implementing a bunch of common
algorithms and techniques often used in Videogame AI. It is still a work
in progress.

Installation
------------

The package is available at PyPI, you can simply do:

    pip install pygame-ai
    
Usage
-----

After installing it you only need to import like:

    import pygame_ai
    
or

    import pygame_ai as pai
    
Core
----

All of this library's implementations work using this implementation
of :py:class:`~.GameObject`.
    
You can see how the library works by downloading our :ref:`example_game`, or
you can visit the :ref:`guide` to see how to implement a simple game
using the library's core functions.

So far these are the major techniquest that have been implemented:

Steering Behaviors
------------------
    
Basic movement behaviors that make in-game characters move in a
pseudo-intelligent way. You will mainly be using 
:py:class:`~.BlendedSteering` and :py:class:`~.PrioritySteering`, 
but feel free to use any of the behaviors found in 
:py:mod:`~steering.kinematic` and :py:mod:`~steering.static` modules.

    * :py:class:`~.StaticSteeringBehavior`
    * :py:class:`~.KinematicSteeringBehavior`
    * :py:class:`~.BlendedSteering`
    * :py:class:`~.PrioritySteering`

Table of Contents
=================

.. toctree::
    :maxdepth: 1
    
    gameobject
    static
    kinematic
    blended
    priority
    path
    example_game
    guide

Indices and tables
==================

    * :ref:`genindex`
    * :ref:`search`

