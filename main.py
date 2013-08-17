#! /usr/bin/env python

""" 
to do:
algorithm:
	draw blank tiles as sea level
	plot fault lines
	plot mountains - mountains have higher chance of existing along fault lines, esp if other mtns are nearby
	plot rivers - river springs are more likely at high z levels, rivers flow along 


	assign random high points
	assign random low points
	walk grid and assign unassigned tiles to
		avg of neighbors + random variance
"""

import math
import pygame
import random
import heightmap
from config import *


def main():

	# start with blank screen
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	screen.fill((0, 0, 0))
	pygame.display.flip()

	# create the height map
	height_map = heightmap.HeightMap(min_height=MIN_HEIGHT, max_height=MAX_HEIGHT, tile_size=TILE_SIZE, map_width=SCREEN_WIDTH, map_height=SCREEN_HEIGHT)
	
	#run the app
	loop()


def loop():
	# infinite loop
	running = 1
	while running:
	    event = pygame.event.poll()
	    if event.type == pygame.QUIT:
	        running = 0


if __name__ == "__main__":
    main()
