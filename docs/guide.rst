.. _guide:

Pygame AI Guide
===============

This guide is meant to explain the basic concepts you need to know to 
integrate this library into your game, it is not meant to explain how to
create games with PyGame, although it does include a very basic game 
structure that you can use as a template.

Contents
--------
    
    * :ref:`GameStructure`
    * :ref:`GameObjects`
    * :ref:`Steering`
    * :ref:`SteeringAsAnAI`
    * :ref:`VerySimpleGame`
    * :ref:`Drag`
    * :ref:`OtherBehaviors`
    * :ref:`Gravity`
    * :ref:`MoreComplexStuff`


.. _GameStructure:

Game Structure
--------------

This is the basic game structure that I'll be working with in this guide,
it contains the basic things that any PyGame game should have.

.. code-block:: python
    
    import sys

    import pygame
    from pygame.locals import *
    import pygame_ai as pai

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # Custom classes and definitions
    # ...   
        
    def main():
        
        # Create screen
        screen_width, screen_height = 800, 600
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('PyGame AI Guide')
        
        # Create white background
        background = pygame.Surface((screen_width, screen_height)).convert()
        background.fill((255, 255, 255))
        
        # Initialize clock
        clock = pygame.time.Clock()
        
        # Variables that you will use in your game loop
        # ...
        
        # Game loop
        while True:
            
            # Get loop time, convert milliseconds to seconds
            tick = clock.tick(60)/1000
            
            # Handle input
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(2)
            
            # Erease previous frame by bliting background
            screen.blit(background, background.get_rect())
            
            # Update the entities in your game
            # ...
            
            # Blit all your entities
            # . . .
            
            # Update display
            pygame.display.update()
            
    if __name__ == '__main__':
        pygame.init()
        main()
        pygame.quit()
        
With this in place we can move on.

.. _GameObjects:

Game Objects
------------

I used the word *entities* before, by that I mean all the moving things
in your game, like the player, enemies, NPCs, you name it. The way these
entities will be better represented (and the only way they should be, 
unless you really know what you're doing) in a game that uses this libray is
by using the :py:class:`~.GameObject` class, it contains all the 
neccesary properties and methods the library uses to do all it's calculations.

The way you create your own entities is by subclassing :py:class:`~.GameObject`
like this:

.. code-block:: python

    class Player(pai.gameobject.GameObject):
    
        def __init__(self, pos = (0, 0)):
            # First we create the image by filling a surface with blue color
            img = pygame.Surface( (10, 15) ).convert()
            img.fill(BLUE)
            # Call GameObejct init with appropiate values
            super(Player, self).__init__(
                img_surf = img,
                pos = pos,
                max_speed = 15,
                max_accel = 40,
                max_rotation = 40,
                max_angular_accel = 30
            )
            
Note that the first thing I do is create a :pgsurf:`Surface`, this is the
image that will be displayed in the game, in this case it is a blue rectangle.
Also note that we hand picked most of the parameters for the :py:class:`~.GameObject`,
this is unfortunately still done trough trial and error, the values that I
used work sort of smoothly but they can be improved.

Now, that is not enough to call it done, we still need to implement a way for
this entity to move, this is usually done trough an **update** function, in fact,
every :py:class:`~.GameObject` has one, but it doesn't do anything.

This is an example Player with it's update function:

.. code-block:: python

    class Player(pai.gameobject.GameObject):
    
        def __init__(self, pos = (0, 0)):
            # First we create the image by filling a surface with blue color
            img = pygame.Surface( (10, 15) ).convert()
            img.fill(BLUE)
            # Call GameObejct init with appropiate values
            super(Player, self).__init__(
                img_surf = img,
                pos = pos,
                max_speed = 15,
                max_accel = 40,
                max_rotation = 40,
                max_angular_accel = 30
            )
            
        def update(self, steering, tick):
            self.steer(steering, tick)
            self.rect.move_ip(self.velocity)
            
Esentially what it does is to **accelerate** the entity in the direction
and strength dictated by the **steering** parameter, and then move the
entity's rect with the direction and stregth of the entity's **velocity**.

.. _Steering:

Steering
--------

*Steering Algorithms* are the core of movement in this library, the
:py:class:`~.kinematic.SteeringOutput` is the way these algorithms comunicate how
an object should **accelerate** in order to achieve it's goal.

In the previous example we saw that the player does not produce it's 
own steering, that is because normally the player is controled by
user input, we'll see later how we can create and modify our own 
:py:class:`SteeringOutput` to move the player, for now let's
move  on and actually implement something useful with this library.

.. _SteeringAsAnAI:

Steering as an AI
-----------------

You can have NPCs whose behavior is only composed by a :py:class:`~.KinematicSteeringBehavior`,
this would be a very simple but often useful AI design, this is how you can
implement an NPC whose only AI behavior is a :py:class:`~.KinematicSteeringBehavior`:

.. code-block:: python

    class CircleNPC(pai.gameobject.GameObject):
    
        def __init__(self, pos = (0, 0)):
            # First create the circle image with alpha channel to have transparency
            img = pygame.Surface( (10, 10) ).convert_alpha()
            img.fill( (255, 255, 255, 0) )
            # Draw the circle
            pygame.draw.circle(img, RED, (5, 5), 5)
            # Call GameObejct init with appropiate values
            super(CircleNPC, self).__init__(
                img_surf = img,
                pos = pos,
                max_speed = 25,
                max_accel = 40,
                max_rotation = 40,
                max_angular_accel = 30
            )
            # Create a placeholder for the AI
            self.ai = pai.steering.kinematic.NullSteering()
            
        def update(self, tick):
            steering = self.ai.get_steering()
            self.steer(steering, tick)
            self.rect.move_ip(self.velocity)
            
The main differences between this and the **Player** entity are that:

    1) The image is a circle
    2) The update actually generates it's own steering
    
The way that point (2) is achieved is by calling the :py:class:`~.KinematicSteeringBehavior`'s
:py:meth:`~.KinematicSteeringBehavior.get_steering` method, this returns
the behaviors' :py:class:`~.kinematic.SteeringOutput`, it is then applied to the
:py:class:`~.GameObject` with the :py:meth:`~.GameObject.steer` method.
This is not the only steering method that exists, we will see more about these
methods later.

.. _VerySimpleGame:

Very Simple Game
----------------

With all we have learned so far we can make a very simple game that consists
only of one input-controlled player and one NPC that chases the player.

First we need to see how to make the player input-controlled, for that
we need to create an artificial :py:class:`~.kinematic.SteeringOutput`
that we can modify, lets add that:

.. code-block:: python

    # . . .
    
    # Variables that you will use in your game loop
    # Create player steering
    player_steering = pai.steering.kinematic.SteeringOutput()

    # Game loop
    while True:
        
        # Get loop time, convert milliseconds to seconds
        tick = clock.tick(60)/1000
        
        # Restart player steering
        player_steering.reset()
        
        # Handle input
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(2)
                
        # . . .
        
With that we simply created an empty :py:class:`~.kinematic.SteeringOutput`
that gets :py:meth:`~.kinematic.SteeringOutput.reset` every frame, this
is to guarantee that it will not grow infinitely.

Then we need to catch user input and modify the steering accordingly,
this piece of code is horrible but I'll use it to avoid complicating
the guide with things that do not relate to the library.

.. code-block:: python
    
    # . . .
    
    # Handle input
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(2)
    
    keys = pygame.key.get_pressed()
    if keys[K_w]:
        player_steering.linear[1] -= player.max_accel
    if keys[K_a]:
        player_steering.linear[0] -= player.max_accel
    if keys[K_s]:
        player_steering.linear[1] += player.max_accel
    if keys[K_d]:
        player_steering.linear[0] += player.max_accel
        
    # . . .
            

Now it is time to actually apply this to the player using the **update**
method that we wrote, for that we first need to instantiate the **Player** class that we 
created. We will also need to instantiate the **CircleNPC** class and do the same with it:

.. code-block:: python
    
    # . . .
    
    # Variables that you will use in your game loop
    # Create player steering
    player_steering = pai.steering.kinematic.SteeringOutput()
    
    # Instantiate game objects
    player = Player(pos = (screen_width//2, screen_height//2))
    circle = CircleNPC(pos = (screen_width//4, screen_height//2))
    
    # Set the NPC AI
    circle.ai = pai.steering.kinematic.Arrive(circle, player)
    
    # Game loop
    while True:
    
        # . . .
        
        # Erease previous frame by bliting background
        screen.blit(background, background.get_rect())
        
        # Update player and NPCs
        player.update(player_steering, tick)
        circle.update(tick)
        
        # Blit all your entities
        screen.blit(player.image, player.rect)
        screen.blit(circle.image, circle.rect)
        
        pygame.display.update()

Apart from instantiating the **CircleNPC** we changed it's ai property to be
:py:class:`~.kinematic.Arrive`, this will make the NPC arrive near the
player and then stop accelerating, We also added the code neccesary to 
blit our entity's images to the screen.
 
If you were to run this code now, it should run propperly, you should 
see the player in the center of the screen and the NPC chasing the player,
the problem is, if you try to move the player, well... it won't stop moving.
That is because when we :py:meth:`~.GameObject.steer` the player it's 
velocity increases, and since we are moving it's position
based on it's velocity, it will never stop moving (unless you steer it correctly 
to negate it's current velocity). The NPC will also never stop beside
the player as it should.

.. _Drag:

Drag
----

To avoid this behavior we need to apply some sort of **Drag** to our
entities, luckily, I've implemented a :py:class:`~.KinematicSteeringBehavior`
that does just that, enter :py:class:`~.Drag`.

The only thing particular to this behavior is that you will not normally
create an individual instance for every entity, instead you should create
one for every *surface* or *environemnt* your entity is in. This is because
an entity will have less drag trying to run in plain land than trying to 
run with it's body half-submerged in water.

For this example we are using only one instance of :py:class:`~.Drag` and
applying it to all entities, but you can get creative.

.. code-block:: python

    # . . .
    
    # Create drag
    drag = pai.steering.kinematic.Drag(15)
    
    # Game loop
    while True:
    
        # . . .
        
        # Erease previous frame by bliting background
        screen.blit(background, background.get_rect())
        
        # Update player and NPCs
        player.update(player_steering, tick)
        circle.update(tick)
        
        # Apply drag
        player.steer(drag.get_steering(player), tick)
        circle.steer(drag.get_steering(circle), tick)
        
        # Blit all your entities
        screen.blit(player.image, player.rect)
        screen.blit(circle.image, circle.rect)
        
        pygame.display.update()
        
Now you will be able to run the code and it should behave as expected.
Note that you can totally add the drag instructions in your entity's
**update** function to make the code less cluttered, I just added it 
there to avoid having to pass it as an argument or putting it
inside the class.

That was a very basic game, and you should be able to use most of the library's 
movement behaviors only with that, the only thing that is a little different
is the :py:class:`~.Path` class used by the :py:class:`~.FollowPath` behavior.

.. _Paths:

Paths
-----

You can create very light-weight paths using the :py:class:`~.Path` class,
the only "problem" is that the paths are defined as mathematic functions,
for people unfamiliar with that it can be quiet spooky, and I would recommend them
to use the pre-implemented paths. Otherwise it is very easy to define paths
with this class, let's define a very simple cosine-wave-shaped path and 
make an NPC follow it:

.. code-block:: python
    
    import math
    
    # . . .
    
    class PathCosine(pai.steering.path.Path):
    
        def __init__(self, start, height, length):
            self.start = start
            self.height = height
            self.length = length
            
            def cosine_path(self, x):
                y = self.start[1] + math.cos(x) * self.height
                return x, y
            
            super(PathCosine, self).__init__(
                path_func = cosine_path,
                domain_start = int(self.start[0]),
                domain_end = int(self.start[0] + length),
                increment = 30
            )
            
And that is it, the :py:class:`~.Path` class handles everything, you just
need to specify the function, it's domain and a discrete increment (for each
point to be generated).

Now we need to put it into the game, let's create another NPC instance
and assign :py:class:`~.FollowPath` with our **PathCosine** to it's
ai behavior.

.. code-block:: python

    # . . .

    # Instantiate game objects
    player = Player(pos = (screen_width//2, screen_height//2))
    circle = CircleNPC(pos = (screen_width//4, screen_height//2))
    circle2 = CircleNPC(pos = (screen_width//5, screen_height//2))
    
    # Set the NPC AI
    circle.ai = pai.steering.kinematic.Arrive(circle, player)
    path_cosine = PathCosine(
        start = circle2.position,
        height = 200,
        length = 500
    )
    circle2.ai = pai.steering.kinematic.FollowPath(circle2, path_cosine)
    
    # . . .
    
Remember to also update, blit and apply drag to circle2.

.. code-block:: python

    # . . .
    
    # Update player and NPCs
    player.update(player_steering, tick)
    circle.update(tick)
    circle2.update(tick)
    
    # Apply drag
    player.steer(drag.get_steering(player), tick)
    circle.steer(drag.get_steering(circle), tick)
    circle2.steer(drag.get_steering(circle2), tick)
    
    # Blit all your entities
    screen.blit(player.image, player.rect)
    screen.blit(circle.image, circle.rect)
    screen.blit(circle2.image, circle2.rect)
    
    # . . .
    
Now you should see an NPC that follows a cosine-wave like path, it will only
go trough it once, you can use :py:meth:`~.Path.reset()` to make the path
reset at any point, or you can take a look into :py:class:`~.CyclicPath`
and :py:class:`~.MirroredPath` for special Path implementations.

.. _OtherBehaviors:

Other Behaviors
---------------

Finally, this library also implements a couple different kinds of 
:py:class:`KinematicSteeringBehavior`s which are :py:class:`BlendedSteering`
and :py:class:`PrioritySteering`. These allow you to combine different
basic behaviors to create more complicated ones, take a look at the
pre-implemented behaviors to see what is possible by using those.

.. _Gravity:

Gravity
-------

Many games include gravity as a core feature (so core that most people
won't consider it a feature), there are a couple of things we need to
consider when adding gravity into our game, but here I'll show a very
basic NPC that has gravity applied.

First, if we are going to have falling entities, we need to make sure 
they dont fall off-screen. for that we can add a very simple check to make
sure nothing moves under the screen:

.. code-block:: python

    # . . .
    
    # Entities afected by gravity
    gravity_entities = []
    
    # . . .
    
    # Game loop
    while True:
        
        # . . .
        
        # Update player and NPCs
        player.update(player_steering, tick)
        circle.update(tick)
        circle2.update(tick)
        
        # Check if our gravity-affected entities are falling off-screen
        for gentity in gravity_entities:
            if gentity.rect.bottom > screen_height:
                gentity.rect.bottom = screen_height
        
        # . . .
        
Now we need to actually implement an entity that is affected by gravity,
let's make that an NPC:

.. code-block:: python

    class GravityCircleNPC(pai.gameobject.GameObject):
    
        def __init__(self, pos = (0, 0)):
            # First create the circle image with alpha channel to have transparency
            img = pygame.Surface( (10, 10) ).convert_alpha()
            img.fill( (255, 255, 255, 0) )
            # Draw the circle
            pygame.draw.circle(img, RED, (5, 5), 5)
            # Call GameObejct init with appropiate values
            super(GravityCircleNPC, self).__init__(
                img_surf = img,
                pos = pos,
                max_speed = 10,
                max_accel = 40,
                max_rotation = 40,
                max_angular_accel = 30
            )
            # Create a placeholder for the AI
            self.ai = pai.steering.kinematic.NullSteering()
            
        def update(self, tick):
            # Gravity steering
            gravity = pai.steering.kinematic.SteeringOutput()
            gravity.linear[1] = 300 # This value is arbitrary, it just works
            
            # Steer only along x axis
            steering = self.ai.get_steering()
            self.steer_x(steering, tick)
            
            # Get total velocity considering gravity
            velocity = self.velocity + gravity.linear * tick
            
            # Move with that velocity
            self.rect.move_ip(velocity)
            
The only difference between this and the regular **CircleNPC** is in the
**update** function, in this one we create a :py:class:`~.kinematic.SteeringOutput`
to act as the **gravity**, we then only consider the AI steering along the x axis,
finally we get a total **velocity** composed of the NPC velocity
plus the velocity induced by gravity. This way we separate the velocity
produced by the actual NPC from the one produced by any external force
(in this case gravity).

Now we only need to instantiate this NPC and do all neccesary actions to 
have it function like the rest of the entities (add it to the
gravity entities list, assign it an AI behavior, update, blit and apply drag).

.. code-block:: python

    # . . .
    
    # Instantiate game objects
    player = Player(pos = (screen_width//2, screen_height//2))
    circle = CircleNPC(pos = (screen_width//4, screen_height//2))
    circle2 = CircleNPC(pos = (screen_width//5, screen_height//2))
    circle3 = GravityCircleNPC(pos = (screen_width//6, screen_height//2))
    
    # Remember to add it to our gravity_entitites list for collision
    gravity_entities.append(circle3)
    
    # Set the NPC AI
    circle.ai = pai.steering.kinematic.Arrive(circle, player)
    path_cosine = PathCosine(
        start = circle2.position,
        height = 200,
        length = 500
    )
    circle2.ai = pai.steering.kinematic.FollowPath(circle2, path_cosine)
    circle3.ai = pai.steering.kinematic.Seek(circle3, player)
    
    # . . .
    
    # Game loop
    while True:
    
        # . . .
        
        # Update player and NPCs
        player.update(player_steering, tick)
        circle.update(tick)
        circle2.update(tick)
        circle3.update(tick)
        
        # Check if our gravity-affected entities are falling off-screen
        for gentity in gravity_entities:
            if gentity.rect.bottom > screen_height:
                gentity.rect.bottom = screen_height
        
        # Apply drag
        player.steer(drag.get_steering(player), tick)
        circle.steer(drag.get_steering(circle), tick)
        circle2.steer(drag.get_steering(circle2), tick)
        circle3.steer(drag.get_steering(circle3), tick)
        
        # Blit all your entities
        screen.blit(player.image, player.rect)
        screen.blit(circle.image, circle.rect)
        screen.blit(circle2.image, circle2.rect)
        screen.blit(circle3.image, circle3.rect)
        
        # . . .
        
You can now run the code again and you should see a falling NPC that also
seeks the player while staying stuck to the ground.


.. _MoreComplexStuff:

More Complex Stuff
------------------

This was a very simple game to show the basic concepts that this library
uses, you can download the game `here <https://mega.nz/#!OpVlDazC!SBJqassdKXwJ_wOzxSfutcbICtefpZ1jRR-5Ksjh2S4>`_. 
You only need to run main.py while having pygame and pygame_ai installed.

If you are interested in knowing what else you can do with this library
you should check out the :ref:`example_game`. You can take a look at how
I implement things there, but you will find a lot of gibberish that is
not directly related to the library.

.. _guide_download: https://google.com/
