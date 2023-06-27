import pygame as pg
import math

paths = {
	'images': {
		'player': '../assets/player.png',
		'asteroids': '../assets/asteroids.png',
		'logo': '../assets/logo.png',
		'target': '../assets/target.png',
		'background': '../assets/bg.png',
		'loot_circle': '../assets/circle.png',
	},
	'animations': {
		'explosion': '../assets/explosion animation.png',
		'player': {
			'default': '../assets/player default.png',
			'cool': '../assets/player cool.png',
			'high': '../assets/player high.png',
			'raging': '../assets/player raging.png',
		},
		'guns': {
			'default': '../assets/gun default shot.png',
			'double': '',
		},
		'star1': '../assets/star 1.png',
		'star2': '../assets/star 2.png',
		'star3': '../assets/star 3.png',
		'star4': '../assets/star 4.png',
	},
	'guns': {
		'default': '../assets/gun.png',
		'double': '../assets/gun double.png',
		'slowdown': '../assets/gun slowing.png'
	},
	'bullets': {
		'default': '../assets/bullet default.png',
		'slowdown': '../assets/bullet slowdown.png'
	},
	'loot': {
		'doublegun': '../assets/gun double loot.png',
		'slowdown': '../assets/gun slowing loot.png'
	},
	'audio': {
		'explosion': '../audio/explosion.wav',
		'pl_explosion': '../audio/explosion_7.wav',
		'shoot 0': '../audio/shoot.flac',
		'shoot 1': '../audio/shoot 1.wav',
		'shoot 2': '../audio/shoot 2.wav',
		'shoot 3': '../audio/shoot 3.wav',
	},
	'font': {}
}

WIDTH, HEIGHT = 1000, 700
TARGET_FPS = 60

TEST_MODES = {
	'guntest': False,  # disable asteroid spawn
	'bullettest': False,  # bullet's speed is 0
	'silent': True,  # disable all sounds
	'nolootspawn': False,  # only asteroids can be spawned
	'showfps': False,  # shows fps
	'loottest': False,  # only loot can be spawned
	'loot_0': False,  # loot starts spawning at score of 0
}


def import_spritesheet_animation(path: str, size: pg.Vector2, scale: float) -> list[pg.image]:
	animation = []
	surface = pg.image.load(path).convert_alpha()
	tile_number_x = surface.get_width() // size.x
	tile_number_y = surface.get_height() // size.y
	for row in range(int(tile_number_y)):
		for col in range(int(tile_number_x)):
			x = col * size.x
			y = row * size.y
			frame = pg.Surface(size, pg.SRCALPHA)
			frame.blit(surface, (0, 0), (x, y, size.x, size.y))
			frame = pg.transform.scale_by(frame, scale)
			animation.append(frame)

	return animation


def is_visible(rect: pg.Rect) -> bool:
	if rect.left > WIDTH:
		return False
	if rect.right < 0:
		return False
	if rect.top > HEIGHT:
		return False
	if rect.bottom < 0:
		return False
	return True


def sine(frequency: float | int, amplitude: float | int, static_distance: float | int) -> int:
	x = pg.time.get_ticks()
	y = static_distance + math.sin(x * frequency) * amplitude
	return int(y)


def get_period(func, frequency: float | int, amplitude: float | int, static_distance: float | int) -> int:
	a = pg.time.get_ticks()
	b = static_distance + func(a * frequency) * amplitude
	return int(b)


def draw_fps(screen, pos, clock, color='white'):
	fps = round(clock.get_fps())
	font = pg.font.SysFont('Arial', 30)
	fps_surface = font.render(str(fps), True, color)
	screen.blit(fps_surface, pos)
