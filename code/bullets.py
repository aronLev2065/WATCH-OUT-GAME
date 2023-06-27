import pygame as pg
import math
from random import randint

from support import TEST_MODES, paths, is_visible


class Bullet(pg.sprite.Sprite):
	def __init__(self, pos, angle_deg, scale, path=paths['bullets']['default']):
		super().__init__()
		self.pos = pg.Vector2(pos)
		self.speed = 21
		if TEST_MODES['bullettest']:
			self.speed = 0
		self.image = pg.image.load(path).convert_alpha()
		self.image = pg.transform.scale_by(self.image, scale)
		self.image = pg.transform.rotate(self.image, angle_deg)
		self.mask = pg.mask.from_surface(self.image)
		self.mask_rect = self.mask.get_rect(center=pos)
		self.rect = self.image.get_rect(center=pos)
		self.velocity = pg.Vector2(0, 0)
		self.velocity.x = math.cos(math.radians(angle_deg)) * self.speed
		self.velocity.y = -math.sin(math.radians(angle_deg)) * self.speed
		self.visible = True

	def shoot_asteroid(self, asteroid):
		asteroid.kill()

	def move(self, dt):
		self.pos += self.velocity * dt
		self.rect.center = self.pos
		self.mask_rect.center = self.pos

	def update(self, dt, borders):
		self.move(dt)
		self.visible = is_visible(self.mask_rect)
		if not self.visible:
			self.kill()


class SlowingBullet(Bullet):
	def __init__(self, pos, angle_deg, scale):
		super().__init__(pos, angle_deg, scale, paths['bullets']['slowdown'])

	def shoot_asteroid(self, asteroid):
		asteroid.velocity *= 0.1
