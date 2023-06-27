import pygame as pg
from support import sine, WIDTH, paths


class UI:
	def __init__(self, color, display):
		self.display_surface = display
		self.bg_color = '#ff1753'
		self.font40 = pg.font.SysFont('arial', 40)
		self.font20 = pg.font.SysFont('arial', 20)
		self.description = self.font20.render('CLICK THE MOUSE TO START', True, 'black')
		self.description_rect = self.description.get_rect()

	def display_description(self, midbottom):
		self.description_rect.midtop = midbottom
		self.display_surface.blit(self.description, self.description_rect)

	def display_score(self, score):
		score_label = self.font40.render(str(score), True, 'black')
		score_rect = score_label.get_rect(midtop=(WIDTH / 2, 25))
		score_rect.y = sine(1 / 300, 5, 25)
		self.display_surface.blit(score_label, score_rect)

	def display_high_score(self, high_score):
		if high_score > 0:
			text = f'HIGH SCORE: {str(high_score)}'
		else:
			text = f'HIGH SCORE: ---'
		high_score_label = self.font20.render(text, True, 'black')
		high_score_rect = high_score_label.get_rect(topleft=(35, 25))
		high_score_rect.y = sine(1 / 300, 5, 25)
		self.display_surface.blit(high_score_label, high_score_rect)


def draw_gradient(surface, target_rect):
	color_rect = pg.image.load(paths['images']['background'])
	color_rect = pg.transform.smoothscale(color_rect, (target_rect.width, target_rect.height))  # stretch!
	surface.blit(color_rect, target_rect)  # paint it
