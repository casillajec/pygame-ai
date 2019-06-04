from unittest import TestCase

import pygame_ai

class TestJoke(TestCase):
    def test_is_string(self):
        s = pygame_ai.joke()
        self.assertTrue(isinstance(s, basestring))
