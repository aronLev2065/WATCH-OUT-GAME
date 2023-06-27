import pygame as pg
from sys import exit
from time import time
from random import randint
import asyncio
from multipledispatch import dispatch

from support import draw_fps, sine, WIDTH, HEIGHT, TARGET_FPS, TEST_MODES, paths
from entities import Player, Explosion, Target, Star
from flying_entities import Asteroid, Loot
from spawner import Spawner
from guns import Gun
from bullets import SlowingBullet, Bullet
from ui import UI, draw_gradient

# region pygame setup
pg.init()
window = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption('WATCH OUT')
pg.mouse.set_visible(False)
clock = pg.time.Clock()


# endregion


class Game:
	def __init__(self):
		# game setup
		self.scale = 3.5
		self.last_time = time()
		self.borders = {
			'left': int(-WIDTH),
			'right': int(WIDTH * 2),
			'top': int(-HEIGHT),
			'bottom': int(HEIGHT * 2)
		}
		self.game_on = False
		self.last_round_time = 0
		self.update_screen = pg.Rect(0, 0, WIDTH, HEIGHT)
		self.bg_color = '#ef9bf0'
		self.spawner = Spawner(self.borders, (WIDTH / 2, HEIGHT / 2), self.scale, window)
		self.loot_spawn_permitted = True
		self.loot_picked_up_time = 0
		self.is_loot_picked_up = False
		self.max_loot_time = 0
		# entities
		player = Player((WIDTH / 2, HEIGHT / 2), self.scale)
		self.player_gr = pg.sprite.GroupSingle(player)
		self.default_gun = Gun((player.rect.centerx, player.rect.centery + 5), self.scale, window)
		self.gun_gr = pg.sprite.GroupSingle(self.default_gun)
		target = Target(self.scale)
		self.target_gr = pg.sprite.GroupSingle(target)
		self.entities = pg.sprite.Group()
		self.explosions = pg.sprite.Group()
		self.stars = pg.sprite.Group()
		self.scatter_stars()
		# ui
		self.ui = UI(self.bg_color, window)
		self.score = 0
		self.high_score = 0
		self.logo = pg.image.load(paths['images']['logo']).convert_alpha()
		self.logo.set_colorkey('white')
		icon = pg.Surface(self.logo.get_size())
		icon.fill(self.bg_color)
		icon.blit(self.logo, (0, 0))
		pg.display.set_icon(icon)
		self.logo = pg.transform.scale(self.logo, (WIDTH / 2, WIDTH / 2))
		self.logo.set_colorkey('white')
		self.logo_rect = self.logo.get_rect(center=(WIDTH / 2, HEIGHT / 2))
		self.test_label = pg.image.load('../assets/test label.png').convert_alpha()
		self.test_label = pg.transform.scale_by(self.test_label, 2)
		# sfx
		self.player_explosion_sfx = pg.mixer.Sound(paths['audio']['pl_explosion'])

	def scatter_stars(self):
		for i in range(25):
			pos = pg.Vector2(randint(0, WIDTH), randint(0, HEIGHT))
			star = Star(paths['animations'][f'star{str(randint(1, 4))}'], pos, self.scale)
			self.stars.add(star)

	def shoot(self):
		self.gun_gr.sprite.shoot()

	def kill_asteroid(self, asteroid):
		asteroid.kill()
		self.score += 1

	@dispatch(Loot, Bullet)
	def manage_bullet_collision(self, loot, _: Bullet):
		# if collided with a bullet, then it must have been shot
		# create an explosion, destroy both the bullet and the entity
		explosion = Explosion(loot.rect.center, self.scale)
		self.explosions.add(explosion)
		loot.kill()
		self.loot_spawn_permitted = True

	@dispatch(Asteroid, Bullet)
	def manage_bullet_collision(self, asteroid, bullet):
		# if collided with a bullet, then it must have been shot
		# create an explosion, destroy both the bullet and the entity
		explosion = Explosion(asteroid.rect.center, self.scale)
		self.explosions.add(explosion)
		bullet.shoot_asteroid(asteroid)
		if not isinstance(bullet, SlowingBullet):
			self.score += 1

	@dispatch(Asteroid)
	def manage_player_collision(self, _: Asteroid):
		# when asteroid collides with the player the game restarts
		if not TEST_MODES['silent']:
			self.player_explosion_sfx.play()
		self.restart()

	@dispatch(Loot)
	def manage_player_collision(self, entity: Loot):
		# when loot collides with the player it applies its effect
		distance = entity.pos - self.player_gr.sprite.rect.center
		if abs(distance[0]) < 2 and abs(distance[1]) < 2:  # when the loot's center == player's center
			pos = (self.player_gr.sprite.rect.centerx, self.player_gr.sprite.rect.centery + 5)
			if entity.loot_type == 'gun':
				gun = entity.create_loot_class(pos, self.scale, window)
				gun.bullets = self.default_gun.bullets.copy()
				self.gun_gr.add(gun)
				self.loot_picked_up_time = pg.time.get_ticks()
				self.max_loot_time = gun.max_time
				self.is_loot_picked_up = True
				if hasattr(gun, 'player_state'):
					self.player_gr.sprite.set_new_state(gun.player_state)
				entity.kill()

	def destroy_loot(self):
		self.default_gun.bullets = self.gun_gr.sprite.bullets.copy()
		self.gun_gr.add(self.default_gun)
		self.is_loot_picked_up = False
		self.loot_spawn_permitted = True
		self.player_gr.sprite.set_new_state('default')

	def play(self, now):
		if not TEST_MODES['guntest']:
			if self.entities.__len__() < self.spawner.loot_quantity:
				# spawn entities when not enough
				entity = self.spawner.spawn(self.score, self.loot_spawn_permitted)
				while entity.check_collision(self.entities, False):
					entity = self.spawner.spawn(self.score, self.loot_spawn_permitted)
				if isinstance(entity, Loot):
					self.loot_spawn_permitted = False
				self.entities.add(entity)
				self.spawner.increase_difficulty(self.score)

		for entity in self.entities.sprites():  # check each asteroid collide with a bullet and the player
			if bullets_collided := entity.check_collision(self.gun_gr.sprite.bullets, kill=True):
				self.manage_bullet_collision(entity, bullets_collided[0])
			elif entity.check_collision(self.player_gr, kill=False):
				self.manage_player_collision(entity)

		if self.is_loot_picked_up:
			if now - self.loot_picked_up_time > self.max_loot_time:
				self.destroy_loot()

	def restart(self):
		self.game_on = False
		self.last_round_time = pg.time.get_ticks()
		# entities
		self.player_gr.sprite.set_new_state('default')
		self.gun_gr.sprite.bullets.empty()
		self.gun_gr.add(self.default_gun)
		self.entities.empty()
		self.explosions.empty()
		self.spawner.reset()
		self.loot_spawn_permitted = True
		self.loot_picked_up_time = 0
		self.is_loot_picked_up = False
		self.max_loot_time = 0
		# ui
		if self.score > self.high_score:
			self.high_score = self.score

	def update_sprites(self, dt):
		# update sprites
		self.stars.update(dt)
		self.player_gr.update(dt)
		self.entities.update(dt, self.borders)
		self.gun_gr.update(dt, self.borders)
		self.explosions.update(dt)
		# draw sprites
		self.stars.draw(window)
		self.entities.draw(window)
		self.player_gr.draw(window)
		self.gun_gr.sprite.draw_bullets(window)
		self.gun_gr.draw(window)
		self.explosions.draw(window)
		if any(TEST_MODES.values()):
			window.blit(self.test_label, (WIDTH - 114, 10))

	async def run(self):
		running = True
		while running:
			now = pg.time.get_ticks()
			events = pg.event.get()
			for e in events:
				if e.type == pg.QUIT:
					running = False
				if e.type == pg.KEYUP:
					if e.key == pg.K_ESCAPE:
						running = False
					if self.game_on:  # if game has started - shoot!
						if e.key == pg.K_SPACE:
							self.shoot()
				if e.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
					if self.game_on:  # if game has started and the ЛКМ is pressed - shoot!
						self.shoot()
					elif (
							self.last_round_time and now - self.last_round_time > 500) or not self.last_round_time:
						# if it hasn't started or this is the next round - start the game
						self.game_on = True
						self.score = 0

			dt = (time() - self.last_time) * 60
			self.last_time = time()
			draw_gradient(window, window.get_rect())

			if self.game_on:
				self.play(now)
				self.update_sprites(dt)
			else:
				self.stars.update(dt)
				self.stars.draw(window)
				self.logo_rect.centery = sine(1 / 300, 5, HEIGHT / 2)
				window.blit(self.logo, self.logo_rect)
				self.ui.display_description(self.logo_rect.midbottom)

			self.ui.display_score(self.score)
			self.ui.display_high_score(self.high_score)
			self.target_gr.update()
			self.target_gr.draw(window)
			if TEST_MODES['showfps']:
				draw_fps(window, (950, 25), clock, 'black')
			await asyncio.sleep(0)
			pg.display.update(self.update_screen)
			clock.tick(TARGET_FPS)

		pg.quit()
		exit()


if __name__ == '__main__':
	game = Game()
	asyncio.run(game.run())
