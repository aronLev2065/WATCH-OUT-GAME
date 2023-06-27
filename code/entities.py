import pygame as pg
from support import paths, import_spritesheet_animation, TEST_MODES


class Player(pg.sprite.Sprite):
	def __init__(self, pos, scale):
		super().__init__()
		self.all_animations = {
			'default': import_spritesheet_animation(paths['animations']['player']['default'], pg.Vector2(32, 32), scale),
			'cool': import_spritesheet_animation(paths['animations']['player']['cool'], pg.Vector2(32, 32), scale),
			'high': import_spritesheet_animation(paths['animations']['player']['high'], pg.Vector2(32, 32), scale),
			'raging': import_spritesheet_animation(paths['animations']['player']['raging'], pg.Vector2(32, 32), scale),
		}
		self.current_image_set = self.all_animations['default']
		self.image = self.current_image_set[0]
		self.rect = self.image.get_rect(center=pos)
		self.mask = pg.mask.from_surface(self.image)
		self.frame_index = 0
		self.animation_speed = 0.13
		self.current_state = 'default'

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt
		if self.frame_index > len(self.current_image_set):
			self.frame_index = 0
		self.image = self.current_image_set[int(self.frame_index)]
		self.mask = pg.mask.from_surface(self.image)
		self.rect = self.image.get_rect(center=self.rect.center)

	def set_new_state(self, new_state):
		if new_state != self.current_state:
			self.current_image_set = self.all_animations[new_state]
			self.current_state = new_state

	def update(self, dt):
		self.animate(dt)


class Explosion(pg.sprite.Sprite):
	def __init__(self, pos, scale):
		super().__init__()
		self.pos = pos
		self.image_set = import_spritesheet_animation(paths['animations']['explosion'], pg.Vector2(32, 32), scale)
		self.image = self.image_set[0]
		self.rect = self.image.get_rect(center=pos)
		self.frame_index = 0
		self.animation_speed = 8/30
		self.explosion_sfx = pg.mixer.Sound(paths['audio']['explosion'])
		if not TEST_MODES['silent']:
			self.explosion_sfx.play()

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt
		if self.frame_index >= len(self.image_set):
			self.kill()
			return
		self.image = self.image_set[int(self.frame_index)]
		self.image.set_colorkey('white')

	def update(self, dt):
		self.animate(dt)


class Target(pg.sprite.Sprite):
	def __init__(self, scale):
		super().__init__()
		self.image = pg.image.load(paths['images']['target']).convert_alpha()
		self.image = pg.transform.scale_by(self.image, scale)
		self.rect = self.image.get_rect()

	def update(self):
		mouse_pos = pg.mouse.get_pos()
		self.rect.center = mouse_pos


class Star(pg.sprite.Sprite):
	def __init__(self, path, pos, scale):
		super().__init__()
		self.image_set = import_spritesheet_animation(path, pg.Vector2(8, 8), scale)
		self.image = self.image_set[0]
		self.image = pg.transform.scale_by(self.image, scale)
		self.rect = self.image.get_rect(center=pos)
		self.frame_index = 0
		self.animation_speed = 0.12

	def animate(self, dt):
		self.frame_index += self.animation_speed * dt
		if self.frame_index > len(self.image_set):
			self.frame_index = 0
		self.image = self.image_set[int(self.frame_index)]
		self.rect = self.image.get_rect(center=self.rect.center)

	def update(self, dt):
		self.animate(dt)
