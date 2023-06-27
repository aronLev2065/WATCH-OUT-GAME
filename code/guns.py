import pygame as pg
import math
from random import randint

from support import paths, TEST_MODES
from bullets import Bullet, SlowingBullet


class Gun(pg.sprite.Sprite):
	def __init__(self, pos, scale, display_surface):
		super().__init__()
		self.scale = scale
		self.pivot = pg.Vector2(pos)
		self.offset = pg.Vector2(45, 0)
		self.muzzle_offset = pg.Vector2(15, 5)
		self.image_orig = pg.image.load(paths['guns']['default']).convert_alpha()
		self.image_orig = pg.transform.scale_by(self.image_orig, scale)
		self.image_orig.set_colorkey('white')
		self.image = self.image_orig.copy()
		self.rect = self.image.get_rect(center=pos)
		self.angle = 0
		self.gun_flip = False
		self.shoot_sfx = pg.mixer.Sound(paths['audio']['shoot 1'])
		self.bullets = pg.sprite.Group()
		self.lifebar = pg.Surface((150, 30))
		self.lifebar_rect = self.lifebar.get_rect(center=self.pivot + pg.Vector2(0, 70))
		self.display_surface = display_surface

	def display_lifebar(self):
		time_left = 100 - (pg.time.get_ticks() - self.creation_time) / self.max_time * 100
		width = abs(self.lifebar_rect.width * time_left / 100)
		lifebar_inner = pg.Surface((width, self.lifebar_rect.height))
		lifebar_inner_rect = lifebar_inner.get_rect(topleft=self.lifebar_rect.topleft)
		pg.draw.rect(self.display_surface, '#ff285e', lifebar_inner_rect, 0)
		pg.draw.rect(self.display_surface, 'white', self.lifebar_rect, 2)

	def shoot(self):
		bullet = Bullet(
			self.pivot + self.offset.rotate(-self.angle) + self.muzzle_offset.rotate(-self.angle), self.angle,
			self.scale)
		self.bullets.add(bullet)
		if not TEST_MODES['silent']:
			self.shoot_sfx.play()

	def follow_mouse(self, mouse: tuple):
		x_offset = mouse[0] - self.pivot.x
		y_offset = self.pivot.y - mouse[1]

		if x_offset != 0:
			# using trigonometry to calculate the angle (inverse tangent)
			self.angle = math.degrees(math.atan2(y_offset, x_offset))

		if self.angle >= 90 or -180 <= self.angle <= -90:
			self.gun_flip = True
			self.muzzle_offset.y = abs(self.muzzle_offset.y)
		else:
			self.gun_flip = False
			self.muzzle_offset.y = -abs(self.muzzle_offset.y)

		self.image, self.rect = self.rotate_image(
			self.image_orig.copy(), self.angle, self.pivot, self.offset, self.gun_flip)

		self.image.set_colorkey('white')

	@staticmethod
	def rotate_image(surface, angle, pivot: pg.Vector2, offset: pg.Vector2, flip: bool) -> tuple:
		"""rotate the surface around the pivot point"""
		surface = pg.transform.flip(surface, False, flip).convert_alpha()  # flip around X axes
		rotated_image = pg.transform.rotate(surface, angle)  # rotate the image
		rotated_offset = offset.rotate(-angle)  # rotate the offset vector
		# Add the offset vector to the center/pivot point to shift the rect
		rect = rotated_image.get_rect(center=pivot + rotated_offset)
		return rotated_image, rect  # Return the rotated image and shifted rect

	def draw_bullets(self, display):
		self.bullets.draw(display)

	def update(self, dt, borders):
		mouse = pg.mouse.get_pos()
		self.follow_mouse(mouse)
		self.bullets.update(dt, borders)


class DoubleGun(Gun):
	def __init__(self, pos, scale, window):
		super().__init__(pos, scale, window)
		self.image_orig = pg.image.load(paths['guns']['double']).convert_alpha()
		self.image_orig = pg.transform.scale_by(self.image_orig, scale)
		self.image = self.image_orig.copy()
		self.rect = self.image.get_rect(center=pos)
		self.offset = pg.Vector2(0, 0)
		self.muzzle_offset = pg.Vector2(50, 0)
		self.player_state = 'raging'
		self.max_time = 10_000  # time after which it disappears
		self.creation_time = pg.time.get_ticks()
		self.shoot_sfx = pg.mixer.Sound(paths['audio']['shoot 2'])

	def shoot(self):
		for i in range(2):
			bullet = Bullet(
				self.pivot + self.offset.rotate(-self.angle) + self.muzzle_offset.rotate(-self.angle + i * 180),
				self.angle + i * 180,
				self.scale)
			self.bullets.add(bullet)
		if not TEST_MODES['silent']:
			self.shoot_sfx.play()

	def update(self, dt, borders):
		super().update(dt, borders)
		self.display_lifebar()


class SlowingGun(Gun):
	def __init__(self, pos, scale, window):
		super().__init__(pos, scale, window)
		self.image_orig = pg.image.load(paths['guns']['slowdown']).convert_alpha()
		self.image_orig = pg.transform.scale_by(self.image_orig, scale)
		self.image = self.image_orig.copy()
		self.rect = self.image.get_rect(center=pos)
		self.max_time = 7_000  # time after which it disappears
		self.creation_time = pg.time.get_ticks()
		self.player_state = 'cool'
		self.shoot_sfx = pg.mixer.Sound(paths['audio']['shoot 3'])

	def shoot(self):
		bullet = SlowingBullet(
			self.pivot + self.offset.rotate(-self.angle) + self.muzzle_offset.rotate(-self.angle), self.angle,
			self.scale)
		self.bullets.add(bullet)
		if not TEST_MODES['silent']:
			self.shoot_sfx.play()

	def update(self, dt, borders):
		super().update(dt, borders)
		self.display_lifebar()
