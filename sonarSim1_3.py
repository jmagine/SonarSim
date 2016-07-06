#!/usr/bin/env python

'''*-----------------------------------------------------------------------*---
                                                        Author: Jason Ma
                                                        Date  : Jun 14 2016
    File Name  : sonarSim1_3.py
    Description: Places several objects relative to an emitter, calculates
                 receiver times in a grid, and then prints a visualization of 
                 all possible object locations to a file named 'timeTable'.
---*-----------------------------------------------------------------------*'''

from __future__ import print_function
from __future__ import division
import numpy as np
from math import pow

#------------------------------------------------------------------------------
#[RUN VARS]--------------------------------------------------------------------
#------------------------------------------------------------------------------

NUM_OBJECTS   = 12        #num of objects

SENS_NUM      = 4        #num of sensors
SENS_X_DISP   = 0.2
SENS_Z_DISP   = 0.3
SENS_SAMPLE   = 200000   #sensor sample rate

TOLERANCE     = 1 / (SENS_SAMPLE / 10)
TOL_DIST      = 1          
SPEED_WAVE    = 1482       #speed of sound in water

sensArr       = np.zeros((SENS_NUM, 3 + NUM_OBJECTS))
  #sensArr[rcvr][0]  -> receiver x
  #sensArr[rcvr][1]  -> receiver y
  #sensArr[rcvr][2]  -> receiver z
  #sensArr[rcvr][3+] -> object times

sensArr[0][0] = 0
sensArr[0][1] = 0
sensArr[0][2] = 0

sensArr[1][0] = -1 * SENS_X_DISP
sensArr[1][1] = 0
sensArr[1][2] = 0

sensArr[2][0] = SENS_X_DISP
sensArr[2][1] = 0
sensArr[2][2] = 0

sensArr[3][0] = 0
sensArr[3][1] = 0
sensArr[3][2] = SENS_Z_DISP

xRegion       = 10
yRegion       = 5
xInc          = .1
yInc          = .1
center        = 0
timeTable     = np.zeros((yRegion / yInc + 1, xRegion / xInc + 1, SENS_NUM))

objs          = np.zeros((NUM_OBJECTS * 5, 3))
  #objs[object][0] -> object x
  #objs[object][1] -> object y
  #objs[object][2] -> object z

objs[0][0]    = 1
objs[0][1]    = 1
objs[0][2]    = 1

objs[1][0]    = -1
objs[1][1]    = 1
objs[1][2]    = 1

objs[2][0]    = 0
objs[2][1]    = 1
objs[2][2]    = 1

objs[3][0]    = 0
objs[3][1]    = 3
objs[3][2]    = -3

objs[4][0]    = 5
objs[4][1]    = 3
objs[4][2]    = 2

objs[5][0]    = -5
objs[5][1]    = 3
objs[5][2]    = -2

objs[6][0]    = 0
objs[6][1]    = 10
objs[6][2]    = 10

objs[7][0]    = 5
objs[7][1]    = 10
objs[7][2]    = 10

objs[8][0]    = -5
objs[8][1]    = 10
objs[8][2]    = 10

objs[9][0]    = 15
objs[9][1]    = 15
objs[9][2]    = 15

objs[10][0]   = -20
objs[10][1]   = 20
objs[10][2]   = 50

objs[11][0]   = 0
objs[11][1]   = 25
objs[11][2]   = 50


#DEBUG-------------------------------------------------------------------------
INTER_ELL_DEBUG = 1
CALC_TIME_DEBUG = 1

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

'''isInRange-------------------------------------------------------------------
Checks whether a value is in a given range (inclusive on both bounds)

lower    - lower bound of range
upper    - upper bound of range
value    - value to check
[return] - 1 if in range
           0 if not in range
----------------------------------------------------------------------------'''
def isInRange(lower, upper, value):
  if value >= lower and value <= upper:
    return 1
  return 0

'''quadSolver------------------------------------------------------------------
Solves quadratic equation

a        - variable
b        - variable
c        - variable
pluMin   - 0 for +
           1 for -
[return] - + or - solution based on input
----------------------------------------------------------------------------'''
def quadSolver(a, b, c, pluMin):

  if pow(b, 2) - 4 * a * c < 0 or a == 0:
    return 0

  #print(-1 * b, '\t', pow(pow(b, 2) - 4 * a * c, 1/2), '\t', 2 * a)
  if pluMin == 0:
    return (-1 * b + pow(pow(b, 2) - 4 * a * c, 1/2)) / (2 * a)
  else:
    return (-1 * b - pow(pow(b, 2) - 4 * a * c, 1/2)) / (2 * a)

'''resolveTArray---------------------------------------------------------------
Calculates object location in 3D using 4 receiver times.

time1    - receiver 1 time
time2    - receiver 2 time
time3    - receiver 3 time
time4    - receiver 4 time
tol      - tolerance for variance in x
[return] - array with 3 elements containing x, y, and z coordinate of object
           will return 0 0 if finds nothing
----------------------------------------------------------------------------'''
def resolveTArray(time1, time2, time3, time4, tol, debug):
   
  #draw ellipses for each receiver of form: (x+a)^2 / b^2 + y^2 / c^2 = 1
  #draw circle for emitter which also receives
  print(time1, time2, time3, time4)
  tempIntersect = np.zeros((4, 2))
  result        = np.zeros((3))  

  r2 = pow(time1 * SPEED_WAVE / 2, 2)

  a = SENS_X_DISP / -2
  b = pow(time2 * SPEED_WAVE / 2, 2)
  c = b - pow(a, 2)

  #calc the a, b, and c of quadratic equation, NOT ellipses
  quada = 1 - c / b
  quadb = 2 * c * a / b
  quadc = c * (1 - pow(a, 2) / b) - r2
  #calculate z locs of intersections
  tempIntersect[0][0] = quadSolver(quada, quadb, quadc, 0)
  tempIntersect[1][0] = quadSolver(quada, quadb, quadc, 1)

  #DEBUG
  if debug:
    print('+-------------------------------------------+')
    print('| [DEBUG]   intersectEllipse   sonarSim 1.3 |')  
    print('+-------------------------------+-----------+-------------------+---------------')
    print('|  ABC: {}\t{}\t{}'.format(repr(round(a, 4)), 
                                        repr(round(b, 4)), 
                                        repr(round(c, 4))),
          end = '\t|')
    print(' XLocs: {}      {}'.format(repr(round(tempIntersect[0][0], 4)), 
                                    repr(round(tempIntersect[1][0], 4))),
           end = '\t|\n')
    print('+-------------------------------+-------------------------------+---------------')  
  
  #calculate y^2 for any found xs
  for i in range(0, 2):
    ySqr = r2 - pow(tempIntersect[i][0], 2)

    #check for invalid x or y locations
    if (tempIntersect[i][0] != 0) and (ySqr >= 0):
      tempIntersect[i][1] = pow(ySqr, 1/2)
      if debug:
        print('| + X{}:'.format(i + 1),
              repr(round(tempIntersect[i][0], 3)), 
              '\t\t\t| Y{}:'.format(i + 1),
              repr(round(tempIntersect[i][1], 3)),
              '\t\t\t|')
    elif debug:
      if tempIntersect[i][0] == 0:
        print('| - X{}: no solution\t\t|\t\t\t\t|'.format(i + 1))
      else:
        print('| - Y{}: undef sqrt({})\t|\t\t\t\t|'.format(i + 1, 
                                                        repr(round(ySqr, 3))))

  '''[PART 2] Use third ellipse to resolve for point------------------------'''

  a = SENS_X_DISP / 2
  b = pow(time3 * SPEED_WAVE / 2, 2)
  c = b - pow(a, 2)

  #calc the a, b, and c of quadratic equation, NOT ellipses
  quada = 1 - c / b
  quadb = 2 * c * a / b
  quadc = c * (1 - pow(a, 2) / b) - r2

  #calculate x locs of intersections
  tempIntersect[2][0] = quadSolver(quada, quadb, quadc, 0)
  tempIntersect[3][0] = quadSolver(quada, quadb, quadc, 1)

  #DEBUG
  if debug:
    print('+-------------------------------+-----------+-------------------+---------------')
    print('|  ABC: {}\t{}\t{}'.format(repr(round(a, 4)), 
                                        repr(round(b, 4)), 
                                        repr(round(c, 4))),
          end = '\t|')
    print(' XLocs: {}      {}'.format(repr(round(tempIntersect[2][0], 4)), 
                                    repr(round(tempIntersect[3][0], 4))),
           end = '\t|\n')
    print('+-------------------------------+-------------------------------+---------------')  
  
  #calculate y^2 for any found xs
  for i in range(2, 4):
    ySqr = r2 - pow(tempIntersect[i][0], 2)

    #check for invalid x or y locations
    if (tempIntersect[i][0] != 0) and (ySqr >= 0):
      tempIntersect[i][1] = pow(ySqr, 1/2)
      if debug:
        print('| + X{}:'.format(i + 1),
              repr(round(tempIntersect[i][0], 3)), 
              '\t\t\t| Y{}:'.format(i + 1),
              repr(round(tempIntersect[i][1], 3)),
              '\t\t\t|')
    elif debug:
      if tempIntersect[i][0] == 0:
        print('| - X{}: no solution\t\t|\t\t\t\t|'.format(i + 1))
      else:
        print('| - Y{}: undef sqrt({})\t|\t\t\t\t|'.format(i + 1, 
                                                        repr(round(ySqr, 3))))

  if debug:
    print('+-------------------------------+-------------------------------+---------------')

  #try all 4 possible intersection points with tolerance against 3rd ellipse
  for i in range(0, 2):
    for j in range(2, 4):
      if tempIntersect[i][0] != 0:
        if isInRange(tempIntersect[i][0] - tol, tempIntersect[i][0] + tol,
                     tempIntersect[j][0]):
          print('\t+ X: {}\tY: {}'.format(repr(round(tempIntersect[i][0], 3)), 
                                                     repr(round(tempIntersect[i][1], 3))))

          result[0] = tempIntersect[i][0]
          result[1] = tempIntersect[i][1]
        elif debug:
          print('\t- {} {}'.format(i, j))
      elif debug:
        print('\t- No i')
  
  if result[1] == 0:
    if debug:
      print('')
    return result

  '''[PART 3] Use fourth receiver for 3D resolution-------------------------'''
  
  a = SENS_Z_DISP / 2
  b = pow(time4 * SPEED_WAVE / 2, 2)
  c = b - pow(a, 2)

  #calc the a, b, and c of quadratic equation, NOT ellipses
  quada = 1 - c / b
  quadb = 2 * c * a / b
  quadc = c * (1 - pow(a, 2) / b) - r2

  #calculate z locs of intersections
  tempIntersect[0][0] = quadSolver(quada, quadb, quadc, 0)
  tempIntersect[1][0] = quadSolver(quada, quadb, quadc, 1)

  #DEBUG
  if debug:
    print('+-------------------------------+-------------------------------+---------------')    
    print('|  ABC: {}\t{}\t{}'.format(repr(round(a, 4)), 
                                      repr(round(b, 4)), 
                                      repr(round(c, 4))),
          end = '\t|')
    print(' ZLocs: {}   {}'.format(repr(round(tempIntersect[0][0], 4)), 
                                   repr(round(tempIntersect[1][0], 4))),
           end = '\t|\n')
    print('+-------------------------------+-------------------------------+---------------')  
  
  #calculate y^2 for any found xs
  for i in range(0, 2):
    ySqr = r2 - pow(tempIntersect[i][0], 2)

    #check for invalid x or y locations
    if (tempIntersect[i][0] != 0) and (ySqr >= 0):
      tempIntersect[i][1] = pow(ySqr, 1/2)
      if debug:
        print('| + Z{}:'.format(i + 1),
              repr(round(tempIntersect[i][0], 3)), 
              '\t\t\t| Y{}:'.format(i + 1),
              repr(round(tempIntersect[i][1], 3)),
              '\t\t\t|')
    elif debug:
      if tempIntersect[i][0] == 0:
        print('| - Z{}: no solution\t\t|\t\t\t\t|'.format(i + 1))
      else:
        print('| - Y{}: undef sqrt({})\t|\t\t\t\t|'.format(i + 1, 
                                                        repr(round(ySqr, 3))))

  if debug:
    print('+-------------------------------+-------------------------------+---------------')  
  
  

  #circle circle intersections in 3D space
  for i in range(0, 2):
    if(tempIntersect[i][1] != 0):
      y1 = pow(result[1], 2) - pow(tempIntersect[i][0], 2)
      y2 = pow(tempIntersect[i][1], 2) - pow(result[0], 2)

      if y1 < 0 or y2 < 0:
        print(' - invalid y1 or y2')
        continue

      y1 = pow(y1, 1/2)
      y2 = pow(y2, 1/2)

      if(isInRange(y2 - tol, y2 + tol, y1)):
        result[1] = (y1 + y2) / 2
        result[2] = tempIntersect[i][0]
      
        if debug:
          print(' + y1: {} y2: {}'.format(y1, y2))
          print('   x: {} y: {} z: {}'.format(result[0], result[1], result[2]))

      elif debug:
        print(' - y1: {} y2: {}'.format(y1, y2))

    elif debug:
      print(' - no Y')

  if debug:
    print('')

  return result

'''
Uses 
'''

'''calcTime--------------------------------------------------------------------
Calculates processed time for given positions of object and receiver

xObj     - x displacement of object from emitter
yObj     - y displacement of object from emitter
rcvrX    - x displacement of receiver from emitter
rcvrY    - y displacement of receiver from emitter
exact    - whether to return exact or processed time
debug    - whether to print debug messages
[return] - time processed by receiver given the sample rate and speed of sound
----------------------------------------------------------------------------'''
def calcTime(xObj, yObj, zObj, xRcvr, yRcvr, zRcvr, exact, debug):
  distEmitterObj  = pow(pow(xObj, 2) + 
                        pow(yObj, 2) + 
                        pow(zObj, 2), 1/2)
  distObjReceiver = pow(pow(xObj - xRcvr, 2) + 
                        pow(yObj - yRcvr, 2) +
                        pow(zObj - zRcvr, 2), 1/2)
  totalDist = distEmitterObj + distObjReceiver
  totalTime = totalDist / SPEED_WAVE

  
  if debug:
    print('DEBUG - CT -',
          repr(round(xObj           , 2)).rjust(4), 
          repr(round(yObj           , 2)).rjust(4),
          repr(round(zObj           , 2)).rjust(4),
          repr(round(xRcvr          , 2)).rjust(4),
          repr(round(yRcvr          , 2)).rjust(4),
          repr(round(zRcvr          , 2)).rjust(4),
          repr(round(distEmitterObj , 5)).rjust(7),
          repr(round(distObjReceiver, 5)).rjust(7),
          repr(round(totalDist      , 5)).rjust(7),
          repr(round(totalTime      , 5)).rjust(7),
          end = '\n')
  
  if(exact):
    return totalTime
  else:
    return totalTime - totalTime % (1 / SENS_SAMPLE) + (1 / SENS_SAMPLE)

'''Driver----------------------------------------------------------------------
Initializes time table, object times, and prints time table through delegation
----------------------------------------------------------------------------'''
def driver():
  #initTimeTable(xRegion, yRegion, xInc, yInc)

  #print(timeTable) #DEBUG

  #initialize objs array with times
  for obj in range(0, NUM_OBJECTS):
    for rcvr in range(0, SENS_NUM):
      sensArr[rcvr][3 + obj] = calcTime(objs[obj][0], objs[obj][1], 
                                        objs[obj][2], sensArr[rcvr][0], 
                                        sensArr[rcvr][1], sensArr[rcvr][2], 
                                        0, CALC_TIME_DEBUG)

  #clear file, all subsequent writes append to this file
  #file = open('timeTable', 'w')
  #file.write('')

  #print time table with all possible locs of objects
  #printPossibleLocs(TOLERANCE)
  '''
  #single object ellipse intersection detection
  for obj1 in range(0, NUM_OBJECTS):
    intersectEllipse(objs[obj1][2], objs[obj1][3], objs[obj1][4], TOL_DIST)
  '''
  #multiple object ellipse intersection detection
  i = 0
  locs = np.zeros((NUM_OBJECTS * 5, 3))
  for obj1 in range(0, NUM_OBJECTS):
    for obj2 in range(0, NUM_OBJECTS):
      for obj3 in range(0, NUM_OBJECTS):
        for obj4 in range(0, NUM_OBJECTS):
          result = resolveTArray(sensArr[0][3 + obj1], sensArr[1][3 + obj2],
                                 sensArr[2][3 + obj3], sensArr[3][3 + obj4],
                                 TOL_DIST, INTER_ELL_DEBUG)
          if(result[2] != 0):
            locs[i][0] = result[0]
            locs[i][1] = result[1]
            locs[i][2] = result[2]
            i = i + 1

  print('      +-------------------------+-------------------------+')
  print('      |  In no particular Order:                          |')
  print('      +-------------------------+-------------------------+')
  print('      |  Found Locs             |  Actual Locs            |')  
  print('      +-------------------------+-------------------------+')
  print('      |  X       Y       Z      |  X       Y       Z      |')  
  print('      +=========================+=========================+')
  for i in range(0, NUM_OBJECTS * 5):
    print('   {} '.format(repr(i + 1).rjust(2)), end = '|\t')
    if(locs[i][2] == 0):
      print('\t\t\t|', end = '')
    else:
      print('{}\t{}\t{}'.format(repr(round(locs[i][0], 3)), 
                                repr(round(locs[i][1], 3)),
                                repr(round(locs[i][2], 3))),
                                end = '\t|')
    if(objs[i][0] == 0) and objs[i][1] == 0 and objs[i][2] == 0:
      print('\t\t\t  |')
    else:
      print(' {}\t  {}\t  {}\t  |'.format(repr(round(objs[i][0], 3)),
                                          repr(round(objs[i][1], 3)),
                                          repr(round(objs[i][2], 3))))
  print('      +-------------------------+-------------------------+')  

driver()
