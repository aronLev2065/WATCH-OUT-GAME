import pygame as pg
import math
from random import randint

from support import is_visible, paths


class FlyingObject(pg.sprite.Sprite):
	def __init__(self, pos, speed, target):
		super().__init__()
		self.pos = pos
		self.speed = speed
		self.velocity = self.calculate_velocity(target)
		self.initial_velocity = self.velocity.copy()
		self.visible = False

	def calculate_velocity(self, target):
		y_offset = target.y - self.pos.y
		x_offset = target.x - self.pos.x
		angle_rad = math.atan2(y_offset, x_offset)
		velocity = pg.Vector2(0, 0)
		velocity.x = math.cos(angle_rad) * self.speed
		velocity.y = math.sin(angle_rad) * self.speed
		return velocity

	def check_collision(self, group, kill):
		return pg.sprite.spritecollide(self, group, kill, pg.sprite.collide_mask)

	def move(self, dt):
		self.pos += self.velocity * dt
		self.rect.center = self.pos

	def update(self, dt, borders):
		self.move(dt)
		check_visible = is_visible(self.rect)
		if self.visible and not check_visible:
			# if object goes off screen after being visible
			self.kill()
			return
		self.visible = check_visible


class Asteroid(FlyingObject):
	def __init__(self, pos, speed, target, image_set):
		super().__init__(pos, speed, target)
		self.image = image_set[randint(0, 3)]
		self.rect = self.image.get_rect(center=self.pos)
		self.mask = pg.mask.from_surface(self.image)

	def update(self, dt, borders):
		super().update(dt, borders)
		current_distance = math.sqrt(self.velocity.x ** 2 + self.velocity.y ** 2)
		initial_distance = math.sqrt(self.initial_velocity.x ** 2 + self.initial_velocity.y ** 2)
		if current_distance < initial_distance:
			self.velocity *= 1.01
		if current_distance > initial_distance * 3 / 4:
			self.velocity = self.initial_velocity * 3 / 4


class Loot(FlyingObject):
	def __init__(self, pos, speed, target, scale, path, loot_holder, loot_type, window):
		super().__init__(pos, speed, target)
		self.display_surface = window
		self.image = pg.image.load(path).convert_alpha()
		self.image = pg.transform.scale_by(self.image, scale)
		self.rect = self.image.get_rect(center=self.pos)
		self.mask = pg.mask.from_surface(self.image)
		self.create_loot_class = loot_holder
		self.loot_type = loot_type

		self.circle_img = pg.image.load(paths['images']['loot_circle']).convert_alpha()
		self.circle_img = pg.transform.scale(self.circle_img, self.rect.size)
		self.circle_rect = self.circle_img.get_rect(center=pos)
		self.angle = 0
		self.rotation_speed = 2

	def animate_circle(self):
		circle_rotated = pg.transform.rotate(self.circle_img, self.angle)
		rotated_rect = circle_rotated.get_rect(center=self.rect.center)
		self.angle += self.rotation_speed
		self.angle %= 360
		self.display_surface.blit(circle_rotated, rotated_rect)

	def update(self, dt, borders):
		super().update(dt, borders)
		self.animate_circle()
