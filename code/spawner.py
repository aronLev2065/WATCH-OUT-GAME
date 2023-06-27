import pygame as pg
import math
from random import random, randint

from support import WIDTH, HEIGHT, paths, import_spritesheet_animation, TEST_MODES
from flying_entities import Asteroid, Loot
from guns import SlowingGun, DoubleGun


class Spawner:
	def __init__(self, borders, target, scale, window):
		self.borders = borders
		self.target = target
		self.scale = scale
		self.loot_min_speed = 0
		self.loot_quantity = 6
		self.max_loot = 15
		self.asteroid_image_set = import_spritesheet_animation(paths['images']['asteroids'], pg.Vector2(16, 16), scale)
		self.permission_level = 0
		self.min_loot_score = 30 if not TEST_MODES['loot_0'] else 0
		self.loot_list = [  # items: (item name in paths, Class, type)
			('doublegun', DoubleGun, 'gun'),
			('slowdown', SlowingGun, 'gun'),
		]
		self.display_surface = window

	def reset(self):
		self.permission_level = 0
		self.loot_min_speed = 1
		self.loot_quantity = 6

	def increase_difficulty(self, score):
		self.loot_quantity = math.sqrt(score/4) + 6
		self.loot_quantity = min(self.max_loot, int(self.loot_quantity))  # <= self.max_loot
		# self.loot_min_speed = math.sqrt((self.loot_quantity-6)/10)
		self.loot_min_speed = (self.loot_quantity - 2) / 10
		if self.loot_min_speed > 1:
			self.loot_min_speed = 1

	def get_random_pos(self):
		side = random()
		pos = pg.Vector2(0, 0)
		if side < 0.5:
			pos.y = randint(0, HEIGHT)
			if side < 0.25:  # left side
				pos.x = randint(self.borders['left'], 0)
			else:  # right side
				pos.x = randint(WIDTH, self.borders['right'])
		else:
			pos.x = randint(0, WIDTH)
			if side < 0.75:  # top side
				pos.y = randint(self.borders['top'], 0)
			else:  # bottom side
				pos.y = randint(HEIGHT, self.borders['bottom'])

		return pos

	def spawn(self, score, loot_permission):
		pos = self.get_random_pos()
		speed = random() + self.loot_min_speed

		# if it is permitted to spawn loot - do it with a 15% chance
		if (loot_permission and not TEST_MODES['nolootspawn']) or TEST_MODES['loottest']:
			if (score >= 50 and random() > 0.85) or TEST_MODES['loottest']:
				return self.spawn_loot(pos, speed)

		# otherwise spawn an asteroid
		return self.spawn_asteroid(pos, speed)

	def spawn_asteroid(self, pos, speed):
		asteroid = Asteroid(pos, speed, pg.Vector2(self.target), self.asteroid_image_set)
		return asteroid

	def spawn_loot(self, pos, speed):
		loot_index = randint(0, self.permission_level)
		if loot_index == self.permission_level and loot_index < len(self.loot_list) - 1:
			self.permission_level += 1

		loot_params = self.loot_list[loot_index]
		return Loot(
			pos, speed, pg.Vector2(self.target), self.scale,
			paths['loot'][loot_params[0]], loot_params[1], loot_params[2], self.display_surface
		)
