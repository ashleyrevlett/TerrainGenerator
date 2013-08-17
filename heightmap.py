import time
import math
import pygame
from pygame.locals import *
import random
import pprint
from config import *
from helpers import *



""" 
Main HeightMap class 

TileMap is 2d array of tile objects, where the row and column of the array match the x and y tile coordinates
of the tile object. Within the object is its z-value and color.
"""

class HeightMap:
	
	def __init__(self, min_height=0, max_height=10, tile_size=5, map_width=100, map_height=100 ):
		
		# init
		random.seed()
		pygame.font.init()
		screen = pygame.display.get_surface()
		
		# set up our defaults
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

		# create initial tiles
		# print 'cols:', self.cols
		# print 'row:', self.rows
		# print 'tile_count:', self.tile_count
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
				

		# # loop through mountains, find nearest x rounds of neighbors, and change their height to interpolated value
		peaks = self.set_random_points( (self.tile_count * MOUNTAIN_FREQ), max_height )
		basins = self.set_random_points( (self.tile_count * BASIN_FREQ), min_height )
		features = peaks + basins
		random.shuffle(features)
		for tile in features:	
			neighbors = self.get_neighbors(tile)
			self.interpolate_neighbors( tile, 2 ) 
			for t in neighbors:
				self.interpolate_neighbors( t, 1 ) 
			


		# # interpolate all tiles to smooth			
		for i in xrange(1,SMOOTH_PASSES):
			print "smoothing"
			self.smooth_map(SMOOTH_STRENGTH, SMOOTH_VARIANCE)
			self.draw_map()

		pygame.display.update()
		pygame.display.flip()		


	def draw_map(self):	
		# draw each tile and its label
		screen = pygame.display.get_surface()
		for i in xrange(self.cols):		
			for j in xrange(self.rows):
				try:
					# update color field 
					self.tiles[i][j]['color'] = self.calc_color(self.tiles[i][j]['z'])
					# draw rect
					pygame.draw.rect(screen, self.tiles[i][j]['color'], (self.tiles[i][j]['x'], self.tiles[i][j]['y'], TILE_SIZE, TILE_SIZE), 0)					
					# draw label
					if SHOW_LABELS:
						label = str(self.tiles[i][j]['z'])	
						font = pygame.font.Font(None, 14)
						text = font.render(label, 1, (10, 10, 10))
						screen.blit(text, (text.get_rect().move(i*TILE_SIZE,j*TILE_SIZE)))
				except Exception as e:
					pprint.pprint(e)




	def calc_color(self, z_val):
		if z_val == 0: return CLR_SEA_3
		if z_val == 1: return CLR_SEA_2
		if z_val == 2: return CLR_SEA_1
		if z_val == 3: return CLR_BEACH
		if z_val == 4: return CLR_GRN_1
		if z_val == 5: return CLR_GRN_2
		if z_val == 6: return CLR_GRN_3
		if z_val == 7: return CLR_STN_1
		if z_val == 8: return CLR_STN_2
		if z_val == 9: return CLR_STN_3
		if z_val == 10: return CLR_PEAK
		return CLR_UNKNOWN




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
			# pprint.pprint(tile)
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

			print 'rnd_var:', rnd_var
			print 'tile[z]:', tile['z']
			print 'neighbor[z]:', t['z']
			print 'avg_z: ', avg_z

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
				pass
				# print 'set_random_points: Exception:', e
		return points


	def smooth_map(self, strength, variance):
		""" choose x random tiles and smooth w/ their neighbors """
		tiles_stack = list(self.tiles)
		random.shuffle(tiles_stack)
		strength_count = int(self.tile_count * strength)
		tiles_stack = tiles_stack[1:strength_count]
		while len(tiles_stack) > 0:
			tile = tiles_stack.pop()
			x = int(tile[0]['tile_x'])
			y = int(tile[0]['tile_y'])				
			self.interpolate_neighbors(self.tiles[x][y], variance)  				



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



