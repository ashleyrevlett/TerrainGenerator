
import math
import pygame
from pygame.locals import *
import random
import pprint
from config import *
from helpers import *



""" 
Main HeightMap class 
"""

class HeightMap:
	
	def __init__(self, min_height=0, max_height=10, tile_size=5, map_width=100, map_height=100 ):
		
		screen = pygame.display.get_surface()

		# record starter vars
		self.min_height = min_height
		self.max_height = max_height
		self.tile_size = tile_size
		self.map_width = map_width
		self.map_height = map_height

		# calc tile grid
		self.cols = int(math.floor(map_width/tile_size))
		self.rows = int(math.floor(map_height/tile_size))
		self.tile_count = self.cols*self.rows
		self.tiles = [[0 for x in xrange(self.rows)] for x in xrange(self.cols)] 
		self.peaks = []
		self.basins = []

		# prep for random events, init font
		random.seed()
		pygame.font.init()
		
		# go through cols and rows to create initial tiles
		print 'cols:', self.cols
		print 'row:', self.rows
		print 'tile_count:', self.tile_count
		for i in xrange(self.rows):
			for j in xrange(self.cols):
				tile = {
					'tile_x': i,
					'tile_y': j,
					'x': (tile_size*i),
					'y': (tile_size*j),
					'z': (self.max_height/2),					
					'color': WHITE
				}				
				self.tiles[i][j]= tile

				if TESTING: 
					pprint.pprint(tile)
				

		# # loop through mountains, find nearest x rounds of neighbors, and change their height to interpolated value
		peaks = self.set_random_points( (self.tile_count * .2), max_height )
		basins = self.set_random_points( (self.tile_count * .01), min_height )
		features = peaks + basins
		random.shuffle(features)
		for tile in features:	
			neighbors = self.get_neighbors(tile)
			self.interpolate_neighbors( tile, 1 ) 
			for t in neighbors:
				self.interpolate_neighbors( t, 1 ) 
			


		# # interpolate all tiles twice to smooth
		self.smooth_map(1, 2)
		# self.smooth_map(1, 2)
						
		# draw each tile
		labels = []		
		for i in xrange(self.cols):		
			for j in xrange(self.rows):
				try:
					# update color field 
					new_color = self.tiles[i][j]['z'] * COLOR_SCALE
					new_color = clamp(new_color, 0, 255)
					self.tiles[i][j]['color'] = (new_color,new_color,new_color)
					pygame.draw.rect(screen, self.tiles[i][j]['color'], (self.tiles[i][j]['x'], self.tiles[i][j]['y'], tile_size, tile_size), 0)
					
					# draw label
					label = str(self.tiles[i][j]['z'])	
					font = pygame.font.Font(None, 14)
					text = font.render(label, 1, (10, 10, 10))
					screen.blit(text, (text.get_rect().move(i*tile_size,j*tile_size)))
				except Exception as e:
					pprint.pprint(e)


		# # self.create_fault_lines()

		pygame.display.update()
		pygame.display.flip()

	


	def get_neighbors(self, tile):
		""" return list of neighboring tiles """
		x_pos = int(tile['tile_x'])
		y_pos = int(tile['tile_y'])		
		neighbors = []
		i = 1
		try:		
			neighbors.append(self.tiles[x_pos - i][y_pos - i] ) #tile_top_left	
			neighbors.append(self.tiles[x_pos][y_pos - i] ) #tile_top_mid
			neighbors.append(self.tiles[x_pos + i][y_pos - i]) #top right
			neighbors.append(self.tiles[x_pos - i][y_pos]) #tile_mid_left
			neighbors.append(self.tiles[x_pos+ i ][y_pos] ) #tile_top_mid			
			neighbors.append(self.tiles[x_pos - i][y_pos + i]) #tile_mid_left
			neighbors.append(self.tiles[x_pos][y_pos + i]) #top right
			neighbors.append(self.tiles[x_pos + i][y_pos + i]) #mid right
			
		except Exception as e:
			pprint.pprint(tile)
			pass
		return neighbors


	def interpolate_neighbors( self, tile, variance ):
		""" take a point and smooth its z vals by avging w/ all neighbor tiles """
		x_pos = int(tile['tile_x'])
		y_pos = int(tile['tile_y'])

		neighbors = self.get_neighbors(tile)
		avgs = []
		for t in neighbors:			
			rnd_var = random.randint(0, variance)
			avg_z = (tile['z'] + t['z']) / 2			

			# print 'rnd_var:', rnd_var
			# print 'tile[z]:', tile['z']
			# print 'neighbor[z]:', t['z']
			# print 'avg_z: ', avg_z

			if (rnd_var % 2 == 0):
				avg_z += rnd_var 
			else:
				avg_z -= rnd_var 
			
			# print 'avg_z +- rnd_var: ', avg_z
			# avg_z = clamp(avg_z, self.min_height, self.max_height)
			# # print 'clamped:', avg_z
			# print ' '
			avgs.append(avg_z)
		
		# average and clamp z vals
		fin_avg_z = sum(avgs)/len(avgs)
		fin_avg_z = clamp( fin_avg_z, self.min_height, self.max_height )		
		self.tiles[ t['tile_x'] ][ t['tile_y'] ]['z'] = fin_avg_z

		# print 'final avg z', fin_avg_z
		# print '\n\n\n'


	def set_random_points( self, total_points, z_value):
		""" pick x random points and change z value of all """
		# tile coord
		points = []
		for point in xrange( int(total_points) ):
			rnd_x = random.randint(0, self.cols-1)
			rnd_y = random.randint(0, self.rows-1)
			try:
				self.tiles[rnd_x][rnd_y]['z'] = z_value			
				points.append(self.tiles[rnd_x][rnd_y])
			except Exception as e:
				print 'set_random_points: Exception:', e
		return points


	def smooth_map(self, strength, variance):
		""" choose x random tiles and smooth w/ their neighbors """
		tiles_stack = list(self.tiles)
		random.shuffle(tiles_stack)
		strength_count = int(self.tile_count * strength)
		tiles_stack = tiles_stack[1:strength_count]
		while len(tiles_stack) > 0:
			tile = tiles_stack.pop()
			if TESTING: pprint.pprint(tile)
			x = int(tile[0]['tile_x'])
			y = int(tile[0]['tile_y'])	
			save_tile = self.tiles[x][y]			
			self.interpolate_neighbors(save_tile, variance)  				



	def create_fault_lines(self):
		""" choose random points, connect them, draw line"""
		points = [random_point() for i in xrange(FAULT_POINTS)]
		for p in points:			
			# find nearest random point in collection
			neighbors = [x for x in points if (x[0] != p[0] or x[1] != p[1] )] 
			nearest = neighbors[0]
			for n in neighbors:
				if distance(p, n) < distance(p, nearest):
					nearest = n
			pygame.draw.line(self.screen, (0, 0, 255), p, nearest)



