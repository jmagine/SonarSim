'''*-----------------------------------------------------------------------*---
                                                          Author: Jason Ma
                                                          Date  : Jun 25 2017

    File Name  : sensor_array.py
    Description: 
                         
---*-----------------------------------------------------------------------*'''

class sensor_array():
  '''[__init__]----------------------------------------------------------------
    Initializes sensor_array with the appropriate positions
  --------------------------------------------------------------------------'''
  def __init__(self, x1, x2, z3, sample):
    self.sensor_locs = [[0] * 3 for x in range(4)]
    self.sensor_locs[1][0] = x1
    self.sensor_locs[2][0] = x2
    self.sensor_locs[3][2] = z3
    self.sample_rate = sample

  '''[set_loc]-----------------------------------------------------------------
    Sets location of 1 receiver
  --------------------------------------------------------------------------'''
  def set_loc(self, rcvr, x, y, z):
    self.sensor_locs[rcvr][0] = x
    self.sensor_locs[rcvr][1] = y
    self.sensor_locs[rcvr][2] = z
