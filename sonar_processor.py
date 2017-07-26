'''*-----------------------------------------------------------------------*---
                                                          Author: Jason Ma
                                                          Date  : Jun 25 2017

    File Name  : sonar_processor.py
    Description: Uses extracted peak times to determine target locations.
---*-----------------------------------------------------------------------*'''

import numpy as np
import random
import threading
import time
import sensor_array

'''----------------------------------------------------------------------------
Config variables
----------------------------------------------------------------------------'''
TOL_INT = 3
TOL_OBJ = 0.25
SPEED_WAVE = 1482

'''[sonar_processor]-----------------------------------------------------------
  Processes set of times, doable in parallel with other sonar_processor threads
  which allows for fast resolution on a large set of times.
----------------------------------------------------------------------------'''
class sonar_processor(threading.Thread):
  '''[__init__]----------------------------------------------------------------
    Initializes sonar_processor to resolve times using a specified model.
  --------------------------------------------------------------------------'''
  def __init__(self, model=[]):
    super(sonar_processor, self).__init__()
    self.end_callback = False
    self.go_callback = False
    self.daemon = True

    self.sim_locs = []
    self.found_locs = []
    self.times = []
    self.num_objs = 10
    self.sensors = sensor_array.sensor_array(-0.15, 0.25, 0.2, 200000)

  '''[callback]----------------------------------------------------------------
    Used for notifying this thread about certain events
  --------------------------------------------------------------------------'''
  def callback(self, message):
    if message == 'END':
      self.end_callback = True
      #print('[s_p] End callback received. Shutting down.')

    if message == 'GO':
      self.go_callback = True

    print('[s_p] Callback received: ' + message)

  '''[spin]--------------------------------------------------------------------
    Process latest data
  --------------------------------------------------------------------------'''
  def spin(self):
    print('[s_p] spinning')
    #read from the latest array of sonar times and process it

    found = 0
    run_count = 0
    found_locs = []

    #TODO fix this
    time_tol_01 = (self.sensors.sensor_locs[1][0]) * -1 / SPEED_WAVE
    time_tol_02 = (self.sensors.sensor_locs[2][0]) / SPEED_WAVE
    time_tol_03 = (self.sensors.sensor_locs[3][2]) / SPEED_WAVE

    for obj1 in range(self.num_objs):
      obj2 = 0

      #start with valid obj2 times
      while obj2 < self.num_objs and self.times[obj2][1] < self.times[obj1][0] - time_tol_01:
        obj2 += 1

      for obj2 in range(obj2, self.num_objs):
        obj3 = 0
        
        #start with valid obj3 times
        while obj3 < self.num_objs and self.times[obj3][2] < self.times[obj1][0] - time_tol_02:
          obj3 += 1
        
        for obj3 in range(obj3, self.num_objs):
          obj4 = 0
          
          #start with valid obj4 times
          while obj4 < self.num_objs and self.times[obj4][3] < self.times[obj1][0] - time_tol_03:
            obj4 += 1

          for obj4 in range(obj4, self.num_objs):
            #make sure none of the times have already been removed
            if self.times[obj1][0] == 0 or self.times[obj2][1] == 0 or self.times[obj3][2] == 0 or self.times[obj4][3] == 0:
              continue

            success, locs = resolve_t_array(self.times[obj1][0], self.times[obj2][1], self.times[obj3][2], self.times[obj4][3], self.sensors, TOL_INT, False)

            run_count += 1
            print('Runs: ' + str(run_count))

            if success:
              dup = False

              for i in range(found):
                if in_range(found_locs[i][0] - TOL_OBJ, found_locs[i][0] + TOL_OBJ, locs[0]) and \
                   in_range(found_locs[i][1] - TOL_OBJ, found_locs[i][1] + TOL_OBJ, locs[1]) and \
                   in_range(found_locs[i][2] - TOL_OBJ, found_locs[i][2] + TOL_OBJ, locs[2]):
                  dup = True

              if dup == False:
                self.times[obj1][0] = 0
                self.times[obj2][1] = 0
                self.times[obj3][2] = 0
                self.times[obj4][3] = 0
                
                found_locs.append(locs)

                found += 1

                #print("Found: " + str(found))

    '''
    for i in range(self.num_objs):
      for j in range(4):
        print("{0}\t".format(self.times[i][j]))
    '''

    print(str(time_tol_01), str(time_tol_02), str(time_tol_03))

    print("Runs : " + str(run_count))
    print("Found: " + str(found))

    self.found_locs = found_locs

  def read_times(self):
    self.times = []

    with open(data, 'r') as f:
      for line in f:
        self.times.append(float(line))

    print(self.times)

  '''[run]---------------------------------------------------------------------
    Runs when thread is started
  --------------------------------------------------------------------------'''
  def run(self):
    while True:
      
      if self.end_callback:
        break;

      while not self.go_callback:
        time.sleep(0.1)

      self.go_callback = False

      print('[s_p] running')

      #self.gen_times()

      self.read_times()

      self.times = self.profiler(times, 200000, 0.5)

      self.spin()

      #self.calc_acc()

  '''[profiler]----------------------------------------------------------------
    Extracts peaks and times from intensity over time profile for use in model.
  --------------------------------------------------------------------------'''
  def profiler(samples, sample_rate, threshold):
    target_cooldown = 10

    for i in range(len(samples)):
      if samples[i] >= threshold and cooldown == 0:
        results.append(i * sample_rate)
        target_cooldown = 10
      taret_cooldown -= 1

    return results

  '''[preprocess_samples]------------------------------------------------------
    Generates a power over time curve using a raw signal
  --------------------------------------------------------------------------'''
  def preprocess_samples(self, samples):
    for i in range(len(samples)):
      samples[i] = (samples[i] * cos(i))^2 + (samples[i] + sin(i))^2

    return samples

  #TODO should be renamed
  '''[gen_times]---------------------------------------------------------------
    Fills sim_locs up with random locations
  --------------------------------------------------------------------------'''
  def gen_times(self):
    print('[s_p] generating times')

    self.sim_locs = []

    #gen random positions
    for i in range(self.num_objs):
      locs = []
      locs.append(random.randint(-50, 50))
      locs.append(random.randint(0, 100))
      locs.append(random.randint(-25, 25))
      self.sim_locs.append(locs)

    
    
    self.times = []
 
    #calc distances/times

    for i in range(self.num_objs):
      self.times.append(calc_times(self.sim_locs[i], self.sensors, False, True))

  '''[calc_acc]----------------------------------------------------------------
    Calculate accuracy of simulation based on actual locs
  --------------------------------------------------------------------------'''
  def calc_acc(self):
    print('[s_p] calculating accuracy')
    
    #triangulateTargets(sensors, times, results);
    print("---------------------------------------------")
    print("    Actual Positions   |   Found positions   ")
    print("---------------------------------------------")

    for i in range(self.num_objs):
      print(str(i), ": ", str(self.sim_locs[i][0]), str(self.sim_locs[i][1]), str(self.sim_locs[i][2]), "|", end="")

      if i < len(self.found_locs):
        print(str(self.found_locs[i][0]), str(self.found_locs[i][1]), str(self.found_locs[i][2]))
      
'''[calc_times]----------------------------------------------------------------
  Calculates times generated by an object placed at a certain loc.
----------------------------------------------------------------------------'''
def calc_times(obj_locs, sensors, exact, debug):
  times = []

  dist_EO = pow(pow(obj_locs[0], 2) + pow(obj_locs[1], 2) + pow(obj_locs[2], 2), 0.5)
    
  for i in range(4):
    dist_OR = pow(pow(obj_locs[0] - sensors.sensor_locs[i][0], 2) + pow(obj_locs[1] - sensors.sensor_locs[i][1], 2) + pow(obj_locs[2] - sensors.sensor_locs[i][2], 2), 0.5)
    
    total_time = (dist_EO + dist_OR) / SPEED_WAVE

    if exact:
      times.append(total_time)
    else:
      times.append(total_time - total_time % (1 / sensors.sample_rate) + (1 / sensors.sample_rate))
    
  if debug:
    print("Times: " + str(times))
    
  return times

'''[in_range]------------------------------------------------------------------
  Checks whether val is within low and high, inclusive.
  low  - low bound
  high - high bound
  val  - value to check range of
----------------------------------------------------------------------------'''
def in_range(low, high, val):
  if val >= low and val <= high:
    return True
  return False

'''[CEIntersect]---------------------------------------------------------------
Calculates X/Z intersect coordinates

a        - variable
b        - variable
[return] - 2 element array containing possible X/Z locs
----------------------------------------------------------------------------'''
def CEIntersect(a, b, c):
  intersects = np.zeros((2))
  d = pow(a, 2) * c / b

  if d < 0:
    return intersects

  d = b * pow(d, 1/2)
  intersects[0] = (pow(a, 3) - d - a * b) / pow(a, 2)
  intersects[1] = (pow(a, 3) + d - a * b) / pow(a, 2)
  return intersects

'''[resolve_t_array]-----------------------------------------------------------
  Solves for a location given a set of receiver times.
----------------------------------------------------------------------------'''
def resolve_t_array(time1, time2, time3, time4, sensors, tol, debug):
  #                  r3
  #                  |
  #             r1---E---r2
  #draw ellipses for r1, r2, and r3 of form: (x+a)^2 / b^2 + y^2 / c^2 = 1
  #draw circle for E
  
  if debug:
    print('[res] called')
  A = 0
  B = 1
  C = 2

  rcvr          = np.zeros((3, 2))
  circY         = np.zeros((2, 2))
  ySqr          = np.zeros((3, 2))
  intersects    = np.zeros((2))
  tempIntersect = np.zeros((6, 2))
  ei            = np.zeros((3, 3))
  result        = np.zeros((3))  
  
  #emitter radius squared
  r2 = pow(time1 * SPEED_WAVE / 2, 2)

  rcvr[0][0] = sensors.sensor_locs[1][0]
  rcvr[1][0] = sensors.sensor_locs[2][0]
  rcvr[2][0] = sensors.sensor_locs[3][2]

  rcvr[0][1] = time2
  rcvr[1][1] = time3
  rcvr[2][1] = time4
  success = False

  for ellipse in range(0, 3):
    #calculate x locs for EOE EO1
    ei[ellipse][A] = rcvr[ellipse][0] / 2
    ei[ellipse][B] = pow(rcvr[ellipse][1] * SPEED_WAVE / 2, 2)
    ei[ellipse][C] = ei[ellipse][B] - pow(ei[ellipse][A], 2)

    #calculate x locs of intersections
    intersects = CEIntersect(ei[ellipse][A], ei[ellipse][B], r2)
    tempIntersect[ellipse * 2][0] = intersects[0]
    tempIntersect[ellipse * 2 + 1][0] = intersects[1]

    #calculate y^2 for any found xs
    for i in range(0, 2):
      ySqr[ellipse][i % 2] = r2 - pow(tempIntersect[ellipse * 2 + i][0], 2)

      #check for invalid x or y locations
      if (tempIntersect[ellipse * 2 + i][0] != 0) and (ySqr[ellipse][i % 2] >= 0):
        tempIntersect[ellipse * 2 + i][1] = pow(ySqr[ellipse][i % 2], 1/2)

    if ellipse == 1:
      found = 0
      #try all 4 possible intersection points with tolerance against 3rd ellipse
      for i in range(0, 2):
        for j in range(2, 4):
          if tempIntersect[i][0] != 0:
            if in_range(tempIntersect[i][0] - tol, tempIntersect[i][0] + tol,
                         tempIntersect[j][0]):
              found = 1
              result[0] = tempIntersect[i][0]
              result[1] = tempIntersect[i][1]
      
      if found == 0:
        break
    elif ellipse == 2:
      #circle circle intersections in 3D space
      for i in range(4, 6):
        if(tempIntersect[i][1] != 0):
          circY[i % 2][0] = pow(result[1], 2) - pow(tempIntersect[i][0], 2)
          circY[i % 2][1] = pow(tempIntersect[i][1], 2) - pow(result[0], 2)
  
          if circY[i % 2][0] < 0 or circY[i % 2][1] < 0:
            continue

          circY[i % 2][0] = pow(circY[i % 2][0], 1/2)
          circY[i % 2][1] = pow(circY[i % 2][1], 1/2)

          if(in_range(circY[i % 2][1] - tol, circY[i % 2][1] + tol, circY[i % 2][0])):
            result[1] = (circY[i % 2][0] + circY[i % 2][1]) / 2
            result[2] = tempIntersect[i][0]
            success = True
 
  #DEBUG
  if debug:
    print('+=[DEBUG]===============================+======================================+')
    print('| resolveTArray      sonarSim 1.4       ', end = '')
    print('| Data: {0:7.5f} {1:7.5f} {2:7.5f} {3:7.5f}\t|'.format(time1, 
                                                                  time2, 
                                                                  time3, 
                                                                  time4))
    for i in range(0, 3):
      print('+-[Part{} EOE EO{}]-----------------------+--------------------------------------+'.format(i, i + 1))
      print('|  ABC: {0:9.3f} {1:9.3f} {2:9.3f}\t|'.format(ei[i][A], 
                                                          ei[i][B], 
                                                          ei[i][C]), 
                                                  end = '')
      print(' XLocs: {0:9.2f} {1:9.2f}\t\t|'.format(tempIntersect[i * 2][0], 
                                                  tempIntersect[i * 2 + 1][0]))
      for j in range(i * 2, (i + 1) * 2):
        if tempIntersect[j][0] == 0:
          print('| - X{}: no solution\t\t\t|\t\t\t\t\t|'.format(j + 1))
        elif tempIntersect[j][1] == 0:
          print('| - Y{0:}: undef sqrt({1:18.3f})\t|\t\t\t\t\t|'.format(j + 1,
                                                               ySqr[0][j % 2]))
        else:
          print('| + X{0:}: {1:8.3f}\t\t\t| Y{0:}: {2:8.3f}\t\t\t\t|'.format(j + 1,
                                                          tempIntersect[j][0], 
                                                          tempIntersect[j][1]))
    print('+---------------------------------------+--------------------------------------+'.format(i, i + 1))
    if found:
      print('| +  X: {0:10.3f} Y: {1:10.3f}\t\t\t\t\t\t\t|'.format(result[0], 
                                                               result[1]))
      for i in range(0, 2):
        if circY[i][0] < 0 or circY[i][1] < 0:
          print('| - invalid Y1 or Y2\t\t\t\t\t\t\t\t|')
        elif circY[i][0] == 0 and circY[i][1] == 0:
          print('| - no Y\t\t\t\t\t\t\t\t\t|')
        elif result[2] != 0:
          print('| + Y1: {0:10.3f} Y2: {1:10.3f}\t> X: {2:8.3f} Y: {3:8.3f} Z:{4:8.3f}\t|'.format(
                                                                   circY[i][0],
                                                                   circY[i][1],
                                                                   result[0],
                                                                   result[1],
                                                                   result[2]))
        else:
          print('| - Y1: {0:10.3f} Y2: {1:10.3f}\t\t\t\t\t\t|'.format(circY[i][0],
                                                                  circY[i][1]))
    print('+=======================================+======================================+\n')
  
  return success, result

