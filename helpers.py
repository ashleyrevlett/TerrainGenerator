import math
import random
from config import *


""" 
Helper functions 
"""

def random_point():
	x = random.randint(0, SCREEN_WIDTH)
	y = random.randint(0, SCREEN_WIDTH)
	return (x,y)

def distance(p1, p2):
	return math.sqrt( math.pow(p2[0] - p1[0], 2) + math.pow(p2[1] - p1[1], 2) )

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)
