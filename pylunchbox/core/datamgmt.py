""" This module is responsible for housing the central point for data.
"""

__author__ = "lunchboxmg"

import ecs

class DataManager(object):
    
    def __init__(self):
        
        pass
    
class DataEvent(object):
    
    def process(self):
        
        raise NotImplementedError