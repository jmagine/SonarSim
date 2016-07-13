#!/usr/bin/env python

'''*-----------------------------------------------------------------------*---
                                                        Author: Jason Ma
                                                        Date  : Jun 14 2016
    File Name  : sonarSim1_4.py
    Description: Places several objects relative to an emitter, then attempts
                 to locate them given processed times received in each 
                 receiver.
---*-----------------------------------------------------------------------*'''

from __future__ import print_function
from __future__ import division
import numpy as np
import time
from math import pow

#------------------------------------------------------------------------------
#[RUN VARS]--------------------------------------------------------------------
#------------------------------------------------------------------------------

NUM_OBJECTS   = 8          #num of objects
SENS_NUM      = 4          #num of sensors
SENS_SAMPLE   = 200000     #sensor sample rate

TOL_DIST      = 3          #ellipse-circle intersection tolerance
TOL_OBJ       = 0.25       #multiple object detection tolerance
SPEED_WAVE    = 1482       #speed of sound in water
EXTRA_FACTOR  = 2          #allocate space in case extra objects are found
sensArr       = np.zeros((SENS_NUM, 3 + NUM_OBJECTS))
  #sensArr[rcvr][0]  -> receiver x
  #sensArr[rcvr][1]  -> receiver y
  #sensArr[rcvr][2]  -> receiver z
  #sensArr[rcvr][3+] -> object times

sensArr[0][0] = 0
sensArr[0][1] = 0
sensArr[0][2] = 0

sensArr[1][0] = -0.15
sensArr[1][1] = 0
sensArr[1][2] = 0

sensArr[2][0] = .25
sensArr[2][1] = 0
sensArr[2][2] = 0

sensArr[3][0] = 0
sensArr[3][1] = 0
sensArr[3][2] = .20

objs          = np.zeros((NUM_OBJECTS * EXTRA_FACTOR, 3))
  #objs[object][0] -> object x
  #objs[object][1] -> object y
  #objs[object][2] -> object z

objs[0][0]    = -1
objs[0][1]    = 10
objs[0][2]    = 0

objs[1][0]    = -3
objs[1][1]    = 10
objs[1][2]    = 0

objs[2][0]    = -5
objs[2][1]    = 20
objs[2][2]    = -7

objs[3][0]    = -4
objs[3][1]    = 21
objs[3][2]    = -6.8

objs[4][0]    = -3
objs[4][1]    = 22
objs[4][2]    = -6.9

objs[5][0]    = -10
objs[5][1]    = 30
objs[5][2]    = -4

objs[6][0]    = -20
objs[6][1]    = 25
objs[6][2]    = -10

objs[7][0]    = -20
objs[7][1]    = 50
objs[7][2]    = -10

'''
objs[0][0]    = 5
objs[0][1]    = 3
objs[0][2]    = 2

objs[1][0]    = -5
objs[1][1]    = 3
objs[1][2]    = -2
'''
'''
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
'''
#DEBUG-------------------------------------------------------------------------
INTER_ELL_DEBUG = 0
CALC_TIME_DEBUG = 0

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

'''CEIntersect-----------------------------------------------------------------
Calculates X/Z intersect coordinates

a        - variable
b        - variable
[return] - 2 element array containing possible X/Z locs
----------------------------------------------------------------------------'''
def CEIntersect(a, b, c):
  intersects = np.zeros((2))
  d = pow(a, 2) * (pow(a, 4) - pow(a, 3) + b * (-1 * pow(a, 2) + a + c)) / pow(b, 2)
  
  if d < 0:
    return intersects

  d = pow(d, 1/2)
  intersects[0] = b * (d / pow(a, 2) - 1 / a) + a
  intersects[1] = b * (-1 * d / pow(a, 2) - 1 / a) + a

  return intersects

'''quadSolver-[DEPRECATED]-----------------------------------------------------
Solves quadratic equation

a        - variable
b        - variable
c        - variable
pluMin   - 0 for +
           1 for -
[return] - + or - solution based on input
----------------------------------------------------------------------------'''
def quadSolver(a, b, c):

  if pow(b, 2) - 4 * a * c < 0 or a == 0:
    return 0
  
  roots = np.zeros((2))

  #print(-1 * b, '\t', pow(pow(b, 2) - 4 * a * c, 1/2), '\t', 2 * a)
  roots[0] = (-1 * b + pow(pow(b, 2) - 4 * a * c, 1/2)) / (2 * a)
  roots[1] = (-1 * b - pow(pow(b, 2) - 4 * a * c, 1/2)) / (2 * a)

  return roots

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
  #                  r3
  #                  |
  #             r1---E---r2
  #draw ellipses for r1, r2, and r3 of form: (x+a)^2 / b^2 + y^2 / c^2 = 1
  #draw circle for E
  
  A = 0
  B = 1
  C = 2

  circY         = np.zeros((2, 2))
  ySqr          = np.zeros((3, 2))
  intersects    = np.zeros((2))
  tempIntersect = np.zeros((6, 2))
  ei            = np.zeros((3, 3))
  result        = np.zeros((3))  
  
  #emitter radius squared
  r2 = pow(time1 * SPEED_WAVE / 2, 2)

  '''[PART 1] Use time1 and time2 to come up with possible locations in 2D--'''
  for ellipse in range(0, 3):
    #calculate x locs for EOE EO1
    ei[0][A] = sensArr[1][0] / 2
    ei[0][B] = pow(time2 * SPEED_WAVE / 2, 2)
    ei[0][C] = ei[0][B] - pow(ei[0][A], 2)

    #calculate x locs of intersections
    quada = 1 - ei[0][C] / ei[0][B]
    quadb = 2 * ei[0][C] * ei[0][A] / ei[0][B]
    quadc = ei[0][C] * (1 - pow(ei[0][A], 2) / ei[0][B]) - r2

    #intersects = CEIntersect(ei[0][A], ei[0][B], r2)
    intersects = quadSolver(quada, quadb, quadc)
    tempIntersect[0][0] = intersects[0]
    tempIntersect[1][0] = intersects[1]

    #calculate y^2 for any found xs
    for i in range(0, 2):
      ySqr[0][i % 2] = r2 - pow(tempIntersect[i][0], 2)

      #check for invalid x or y locations
      if (tempIntersect[i][0] != 0) and (ySqr[0][i % 2] >= 0):
        tempIntersect[i][1] = pow(ySqr[0][i % 2], 1/2)

  '''[PART 2] Use third receiver to resolve for point-----------------------'''

  #calculate x locs for EOE EO1
  ei[1][A] = sensArr[2][0] / 2
  ei[1][B] = pow(time3 * SPEED_WAVE / 2, 2)
  ei[1][C] = ei[1][B] - pow(ei[1][A], 2)

  #calculate x locs of intersections
  quada = 1 - ei[1][C] / ei[1][B]
  quadb = 2 * ei[1][C] * ei[1][A] / ei[1][B]
  quadc = ei[1][C] * (1 - pow(ei[1][A], 2) / ei[1][B]) - r2

  #intersects = CEIntersect(ei[1][A], ei[1][B], r2)
  intersects = quadSolver(quada, quadb, quadc)
  tempIntersect[2][0] = intersects[0]
  tempIntersect[3][0] = intersects[1]
 
  #calculate y^2 for any found xs
  for i in range(2, 4):
    ySqr[1][i - 2] = r2 - pow(tempIntersect[i][0], 2)

    #check for invalid x or y locations
    if (tempIntersect[i][0] != 0) and (ySqr[1][i - 2] >= 0):
      tempIntersect[i][1] = pow(ySqr[1][i - 2], 1/2)
  
  found = 0
  #try all 4 possible intersection points with tolerance against 3rd ellipse
  for i in range(0, 2):
    for j in range(2, 4):
      if tempIntersect[i][0] != 0:
        if isInRange(tempIntersect[i][0] - tol, tempIntersect[i][0] + tol,
                     tempIntersect[j][0]):
          found = 1
          result[0] = tempIntersect[i][0]
          result[1] = tempIntersect[i][1]

  '''[PART 3] Use fourth receiver for 3D resolution-------------------------'''
  if found == 1:
    #calculate z locs for EOE EO3
    ei[2][A] = sensArr[3][2] / 2
    ei[2][B] = pow(time4 * SPEED_WAVE / 2, 2)
    ei[2][C] = ei[2][B] - pow(ei[2][A], 2)

    #calculate x locs of intersections
    quada = 1 - ei[2][C] / ei[2][B]
    quadb = 2 * ei[2][C] * ei[2][A] / ei[2][B]
    quadc = ei[2][C] * (1 - pow(ei[2][A], 2) / ei[2][B]) - r2

    #intersects = CEIntersect(ei[2][A], ei[2][B], r2)
    intersects = quadSolver(quada, quadb, quadc)
    tempIntersect[4][0] = intersects[0]
    tempIntersect[5][0] = intersects[1]

    #calculate y^2 for any found xs
    for i in range(4, 6):
      ySqr[2][i - 4] = r2 - pow(tempIntersect[i][0], 2)
  
      #check for invalid x or y locations
      if (tempIntersect[i][0] != 0) and (ySqr[2][i - 4] >= 0):
        tempIntersect[i][1] = pow(ySqr[2][i - 4], 1/2)

    #circle circle intersections in 3D space
    for i in range(4, 6):
      if(tempIntersect[i][1] != 0):
        circY[i % 2][0] = pow(result[1], 2) - pow(tempIntersect[i][0], 2)
        circY[i % 2][1] = pow(tempIntersect[i][1], 2) - pow(result[0], 2)
  
        if circY[i % 2][0] < 0 or circY[i % 2][1] < 0:
          continue

        circY[i % 2][0] = pow(circY[i % 2][0], 1/2)
        circY[i % 2][1] = pow(circY[i % 2][1], 1/2)

        if(isInRange(circY[i % 2][1] - tol, circY[i % 2][1] + tol, circY[i % 2][0])):
          result[1] = (circY[i % 2][0] + circY[i % 2][1]) / 2
          result[2] = tempIntersect[i][0]


  #DEBUG
  if debug:
    print('+=[DEBUG]===============================+======================================+')
    print('| resolveTArray      sonarSim 1.4       ', end = '')
    print('| Data: {0:7} {1:7} {2:7} {3:7}\t|'.format(repr(round(time1, 5)), 
                                                      repr(round(time2, 5)), 
                                                      repr(round(time3, 5)), 
                                                      repr(round(time4, 5))))
    for i in range(0, 3):
      print('+-[Part{} EOE EO{}]-----------------------+--------------------------------------+'.format(i, i + 1))
      print('|  ABC: {0:9} {1:9} {2:9}\t|'.format(repr(round(ei[0][A], 3)), 
                                                  repr(round(ei[0][B], 3)), 
                                                  repr(round(ei[0][C], 3))), 
                                                  end = '')
      print(' XLocs: {0:9} {1:9}\t\t|'.format(repr(round(tempIntersect[0][0], 2)), 
                                              repr(round(tempIntersect[1][0], 2))))
      for j in range(i * 2, (i + 1) * 2):
        if tempIntersect[j][0] == 0:
          print('| - X{}: no solution\t\t\t|\t\t\t\t\t|'.format(j + 1))
        elif tempIntersect[j][1] == 0:
          print('| - Y{0:}: undef sqrt({1:18})\t|\t\t\t\t\t|'.format(j + 1,
          repr(round(ySqr[0][j % 2], 3))))
        else:
          print('| + X{0:}: {1:8}\t\t\t| Y{0:}: {2:8}\t\t\t\t|'.format(j + 1,
                                            repr(round(tempIntersect[j][0], 3)), 
                                            repr(round(tempIntersect[j][1], 3))))
    print('+---------------------------------------+--------------------------------------+'.format(i, i + 1))
    if found:
      print('| +  X: {0:10} Y: {1:10}\t\t\t\t\t\t|'.format(repr(round(result[0], 3)), 
                                                    repr(round(result[1], 3))))
      for i in range(0, 2):
        if circY[i][0] < 0 or circY[i][1] < 0:
          print('| - invalid Y1 or Y2\t\t\t\t\t\t\t\t|')
        elif circY[i][0] == 0 and circY[i][1] == 0:
          print('| - no Y\t\t\t\t\t\t\t\t\t|')
        elif result[2] != 0:
          print('| + Y1: {0:10} Y2: {1:10}\t> X: {2:8} Y: {3:8} Z: {4:8}\t|'.format(
                                                 repr(round(circY[i][0], 3)),
                                                 repr(round(circY[i][1], 3)),
                                                 repr(round(result[0], 3)),
                                                 repr(round(result[1], 3)),
                                                 repr(round(result[2], 3))))
        else:
          print('| - Y1: {0:10} Y2: {1:10}\t\t\t\t\t\t|'.format(repr(round(circY[i][0], 3)),
                                                 repr(round(circY[i][1], 3))))
    print('+=======================================+======================================+\n')
  
  return result

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
  start = time.time() * 1000

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
  locs = np.zeros((NUM_OBJECTS * EXTRA_FACTOR, 3))
  for obj1 in range(0, NUM_OBJECTS):
    for obj2 in range(0, NUM_OBJECTS):
      for obj3 in range(0, NUM_OBJECTS):
        for obj4 in range(0, NUM_OBJECTS):
          result = resolveTArray(sensArr[0][3 + obj1], sensArr[1][3 + obj2],
                                 sensArr[2][3 + obj3], sensArr[3][3 + obj4],
                                 TOL_DIST, INTER_ELL_DEBUG)
          if(result[2] != 0):
            match = 0
            for j in range(0, i):
              if(isInRange(locs[j][0] - TOL_OBJ, locs[j][0] + TOL_OBJ, result[0]) and
                 isInRange(locs[j][1] - TOL_OBJ, locs[j][1] + TOL_OBJ, result[1]) and
                 isInRange(locs[j][2] - TOL_OBJ, locs[j][2] + TOL_OBJ, result[2])):
                match = 1
            if match == 0:
              locs[i][0] = result[0]
              locs[i][1] = result[1]
              locs[i][2] = result[2]
              i = i + 1
  
  end = time.time() * 1000
  print('Time: ', start - end, 'ms')
  print('      +===================================================+')
  print('      |  E: {0:5} {1:5} {2:5}   | R1: {3:5} {4:5} {5:5}   |'.format(
                                                           sensArr[0][0],
                                                           sensArr[0][1],
                                                           sensArr[0][2],
                                                           sensArr[1][0],
                                                           sensArr[1][1],
                                                           sensArr[1][2]))
  print('      | R2: {0:5} {1:5} {2:5}   | R3: {3:5} {4:5} {5:5}   |'.format(
                                                           sensArr[2][0],
                                                           sensArr[2][1],
                                                           sensArr[2][2],
                                                           sensArr[3][0],
                                                           sensArr[3][1],
                                                           sensArr[3][2]))

  print('      +=========================+=========================+')
  print('      |  In no particular Order:                          |')
  print('      +-------------------------+-------------------------+')
  print('      |  Found Locs             |  Actual Locs            |')  
  print('      +-------------------------+-------------------------+')
  print('      |  X       Y       Z      |  X       Y       Z      |')  
  print('      +=========================+=========================+')
  for i in range(0, NUM_OBJECTS * EXTRA_FACTOR):
    print('   {} '.format(repr(i + 1).rjust(2)), end = '|\t')
    if(locs[i][2] == 0):
      print('\t\t\t|', end = '')
    else:
      print('{0:7} {1:7} {2:7}'.format(repr(round(locs[i][0], 3)), 
                                       repr(round(locs[i][1], 3)),
                                       repr(round(locs[i][2], 3))),
                                       end = '\t|')
    if(objs[i][0] == 0) and objs[i][1] == 0 and objs[i][2] == 0:
      print('\t\t\t  |')
    else:
      print(' {0:7} {1:7} {2:7} |'.format(repr(round(objs[i][0], 3)),
                                          repr(round(objs[i][1], 3)),
                                          repr(round(objs[i][2], 3))))
  print('      +-------------------------+-------------------------+')  

driver()
