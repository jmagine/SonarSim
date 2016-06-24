#!/usr/bin/env python

'''*-----------------------------------------------------------------------*---
                                                        Author: Jason Ma
                                                        Date  : Jun 14 2016
    File Name  : sonarSim1_1.py
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

NUM_SENSORS = 3
SPACING     = 0.3
SAMPLE_RATE = 200000
sensArr     = np.array([NUM_SENSORS, SPACING, SAMPLE_RATE])

recArr      = np.array((NUM_SENSORS, 2))

xRegion     = 10
yRegion     = 5
xInc        = .1
yInc        = .1
center      = 0
timeTable   = np.zeros((yRegion / yInc + 1, xRegion / xInc + 1, sensArr[0]))

NUM_OBJECTS = 3
objs        = np.zeros((NUM_OBJECTS, 5))
#objs[object][0] -> object x
#objs[object][1] -> object y
#objs[object][2] -> object rec1 time
#objs[object][3] -> object rec2 time
#objs[object][4] -> object rec3 time

objs[0][0] = 3
objs[0][1] = 4

objs[1][0] = -3
objs[1][1] = 4

objs[2][0] = 3.5
objs[2][1] = 3.5

TOLERANCE   = 1 / (sensArr[2] / 10)
TOL_DIST = 0.1
SPEED_WAVE  = 1482

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

'''intersectEllipse------------------------------------------------------------
Calculates ellipse intersection locations using 3 receiver times.

time1    - receiver 1 time
time2    - receiver 2 time
time3    - receiver 3 time
tol      - tolerance for variance in x
[return] - array with 2 elements containing x and y coordinate of intersection
           will return 0 0 if finds nothing
----------------------------------------------------------------------------'''
def intersectEllipse(time1, time2, time3, tol):
   
  #draw ellipses for each receiver of form: (x+a)^2 / b^2 + y^2 / c^2 = 1

  #ellipses[rcvr][0] -> a
  #ellipses[rcvr][1] -> b^2
  #ellipses[rcvr][2] -> c^2
  ellipses = np.zeros((3, 3))
  tempIntersect = np.zeros((4, 2))
  
  #calculate a, b, and c for ellipses
  ellipses[0][0] = sensArr[1] / -2
  ellipses[0][1] = pow(time1 * SPEED_WAVE / 2, 2)
  ellipses[0][2] = pow(time1 * SPEED_WAVE / 2, 2) - pow(sensArr[1] / 2, 2)
  
  ellipses[1][0] = -1 * sensArr[1]
  ellipses[1][1] = pow(time2 * SPEED_WAVE / 2, 2)
  ellipses[1][2] = pow(time2 * SPEED_WAVE / 2, 2) - pow(sensArr[1], 2)

  ellipses[2][0] = sensArr[1] * -3 / 2
  ellipses[2][1] = pow(time3 * SPEED_WAVE / 2, 2)
  ellipses[2][2] = pow(time3 * SPEED_WAVE / 2, 2) - pow(sensArr[1] * 3 / 2, 2)

  #the a, b, and c of quadratic equation, NOT ellipses
  a = ellipses[0][2] / ellipses[0][1] - ellipses[1][2] / ellipses[1][1]
  b = 2 * (ellipses[0][2] * ellipses[0][0] / ellipses[0][1] - 
           ellipses[1][2] * ellipses[1][0] / ellipses[1][1])
  c = (ellipses[0][2] * pow(ellipses[0][0], 2) / ellipses[0][1] - 
      ellipses[1][2] * pow(ellipses[1][0], 2) / ellipses[1][1] -
      ellipses[0][2] + ellipses[1][2])

  #calculate x locs of intersections
  tempIntersect[0][0] = quadSolver(a, b, c, 0)
  tempIntersect[1][0] = quadSolver(a, b, c, 1)
  
  '''
  #DEBUG
  print('DEBUG - IE1 -----------------------------------')
  print('E1   :\t', ellipses[0][0], ellipses[0][1], ellipses[0][2])
  print('E2   :\t', ellipses[1][0], ellipses[1][1], ellipses[1][2])
  print('ABC  :\t', a, b, c)
  print('XLocs:\t', tempIntersect[0][0], tempIntersect[1][0])
  '''
  #calculate y^2
  ySqr = (1 - pow(tempIntersect[0][0] + ellipses[0][0], 2) / 
          ellipses[0][1]) * ellipses[0][2]

  #check for invalid x or y locations
  if (tempIntersect[0][0] != 0) and (ySqr >= 0):
    tempIntersect[0][1] = pow(ySqr, 1/2)
    '''
    print('X1: ',
          repr(round(tempIntersect[0][0], 5)), 
          '\tY1: ',
          repr(round(tempIntersect[0][1], 5)))
    '''

  '''
  elif tempIntersect[0][0] == 0:
    print('no X1 solution')
  else:
    print('no Y1 solution', ySqr)
  '''

  #calculate y^2
  ySqr = (1 - pow(tempIntersect[1][0] + ellipses[0][0], 2) / 
          ellipses[0][1]) * ellipses[0][2]

  #check for invalid x or y locations
  if (tempIntersect[1][0] != 0) and (ySqr >= 0):
    tempIntersect[1][1] = pow(ySqr, 1/2)
    '''
    print('X2: ',
          repr(round(tempIntersect[1][0], 5)), 
          '\tY2: ',
          repr(round(tempIntersect[1][1], 5)))
    '''

  '''
  elif tempIntersect[1][0] == 0:
    print('no X2 solution')
  else:
    print('no Y2 solution', ySqr)
  '''

  '''[PART 2] Use third ellipse to resolve for point------------------------'''
  #the a, b, and c of quadratic equation, NOT ellipses
  a = ellipses[0][2] / ellipses[0][1] - ellipses[2][2] / ellipses[2][1]
  b = 2 * (ellipses[0][2] * ellipses[0][0] / ellipses[0][1] - 
           ellipses[2][2] * ellipses[2][0] / ellipses[2][1])
  c = (ellipses[0][2] * pow(ellipses[0][0], 2) / ellipses[0][1] - 
      ellipses[2][2] * pow(ellipses[2][0], 2) / ellipses[2][1] -
      ellipses[0][2] + ellipses[2][2])

  #calculate x locs of intersections
  tempIntersect[2][0] = quadSolver(a, b, c, 0)
  tempIntersect[3][0] = quadSolver(a, b, c, 1)

  '''
  #DEBUG
  print('DEBUG - IE2 -----------------------------------')
  print('E1   :\t', ellipses[0][0], ellipses[0][1], ellipses[0][2])
  print('E2   :\t', ellipses[2][0], ellipses[2][1], ellipses[2][2])
  print('ABC  :\t', a, b, c)
  print('XLocs:\t', tempIntersect[2][0], tempIntersect[3][0])
  '''
  
  #try all 4 possible intersection points with tolerance against 3rd ellipse
  for i in range(0, 2):
    for j in range(2, 4):
      if tempIntersect[i][0] != 0:
        if isInRange(tempIntersect[i][0] - tol, tempIntersect[i][0] + tol,
                     tempIntersect[j][0]):
          print('+ res:\tX:', repr(round(tempIntersect[i][0], 5)), 
                '\tY:', repr(round(tempIntersect[i][1], 5)))
        #else:
        #  print('- res:\t', i, j)
      #else:
      #  print('- res:\tNo i')


'''calcTimeExact---------------------------------------------------------------
Calculates exact time for given positions of object and receiver

xObj     - x displacement of object from emitter
yObj     - y displacement of object from emitter
rcvrDist - x displacement of receiver from emitter
[return] - time processed by receiver given the sample rate and speed of sound
----------------------------------------------------------------------------'''
def calcTimeExact(xObj, yObj, rcvrDist):
  distEmitterObj = pow(pow(xObj, 2) + pow(yObj, 2), 1/2)
  #if (xObj >= 0 and rcvrDist > 0) or (xObj <= 0 and rcvrDist < 0):
    #print(pow(xObj - rcvrDist, 2), end = '')
  distObjReceiver = pow(pow(xObj - rcvrDist, 2) + pow(yObj, 2), 1/2)
  #else:
    #print(pow(xObj + rcvrDist, 2), end = '')
    #distObjReceiver = pow(pow(xObj - rcvrDist, 2) + pow(yObj, 2), 1/2)

  totalDist = distEmitterObj + distObjReceiver
  totalTime = totalDist / SPEED_WAVE

  #print(distEmitterObj, distObjReceiver, end = ' ')
  #print(totalDist, end = ' ')
  #print(totalTime, end = ' ')

  return totalTime

'''calcTime--------------------------------------------------------------------
Calculates processed time for given positions of object and receiver

xObj     - x displacement of object from emitter
yObj     - y displacement of object from emitter
rcvrDist - x displacement of receiver from emitter
[return] - time processed by receiver given the sample rate and speed of sound
----------------------------------------------------------------------------'''
def calcTime(xObj, yObj, rcvrDist):
  distEmitterObj = pow(pow(xObj, 2) + pow(yObj, 2), 1/2)
  distObjReceiver = pow(pow(xObj - rcvrDist, 2) + pow(yObj, 2), 1/2)
  totalDist = distEmitterObj + distObjReceiver
  totalTime = totalDist / SPEED_WAVE

  '''
  #DEBUG
  print('DEBUG - CT - ',
        repr(round(xObj           , 2)), '\t', 
        repr(round(yObj           , 2)), '\t', 
        repr(round(rcvrDist       , 2)), '\t',
        repr(round(distEmitterObj , 5)), '\t',
        repr(round(distObjReceiver, 5)), '\t',
        repr(round(totalDist      , 5)), '\t',
        repr(round(totalTime      , 5)), '\t',
        end = '\n')
  '''

  return totalTime - totalTime % (1 / sensArr[2]) + (1 / sensArr[2])

'''initTimeTable---------------------------------------------------------------
Initializes time table for given receiver positions

xRegion - total size of x region to be stored
yRegion - total size of y region to be stored
xInc    - x grid unit tile spacing
yInc    - y grid unit tile spacing
center  - 0 for y uncentered                       TODO hasn't been implemented
          1 for y centered
----------------------------------------------------------------------------'''
def initTimeTable(xRegion, yRegion, xInc, yInc):
  numXObj = xRegion / xInc
  numYObj = yRegion / yInc

  for row in range(0, int(numYObj) + 1):
    for col in range(0, int(numXObj) + 1):
      for rcvr in range(1, int(sensArr[0]) + 1):
        '''
        #DEBUG
        print('DEBUG - ITT - ',
              repr(row) .rjust(3), '\t', 
              repr(col) .rjust(3), '\t', 
              repr(rcvr).rjust(3), '\t', 
              repr(round(col * xInc - xRegion / 2, 3)), '\t', 
              repr(round(yRegion - row * yInc    , 3)), '\t',
              end = '')
        '''
        timeTable[row][col][rcvr - 1] = calcTime(col * xInc - xRegion / 2,
                                 yRegion - row * yInc, sensArr[1] * rcvr)

        #print(repr(round(timeTable[row][col][rcvr - 1], 12))) #DEBUG        

'''printPossibleLocs-----------------------------------------------------------
Prints a visualization of possible object locations given an array of receiver
times.

tol - tolerance when comparing times to the grid of possible objects
----------------------------------------------------------------------------'''
def printPossibleLocs(tol):
  file = open('timeTable', 'a')

  file.write('      ')
  for col in range(0, int(xRegion / xInc) + 1):
    file.write('{0:4.1f}|'.rjust(4).format(col * xInc - xRegion / 2))

  file.write('\n\n      ' +
             repr(round(xRegion * -1 / 2, 3)) + ' <-- ' +
             repr(round(xInc, 3)) + ' --> ' +
             repr(round(xRegion / 2, 3)) +
             '\n')

  for row in range(0, int(yRegion / yInc) + 1):
    #print leading label
    file.write('{0:4.1f} '.rjust(5).format(yRegion - yInc * row)) 

    for col in range(0, int(xRegion / xInc) + 1):
      #print ^ for emitter location
      if col == (int(xRegion / xInc)) / 2 and row == int(yRegion / yInc):
        file.write('^')
        continue

      empty = 1
      for obj1 in range(0, NUM_OBJECTS):
        for obj2 in range(0, NUM_OBJECTS):
          for obj3 in range(0, NUM_OBJECTS):
            #print o for times in matching range, . otherwise
            if   isInRange(objs[obj1][2] - tol, 
                           objs[obj1][2] + tol, 
                           timeTable[row][col][0]) == 0:
              continue
            elif isInRange(objs[obj2][3] - tol, 
                           objs[obj2][3] + tol, 
                           timeTable[row][col][1]) == 0:
              continue
            elif isInRange(objs[obj3][4] - tol, 
                           objs[obj3][4] + tol, 
                           timeTable[row][col][2]) == 0:
              continue
            else:
              empty = 0
              print(row, '\t',
                    col, '\t',
                    objs[obj1][2], '\t', 
                    objs[obj2][3], '\t', 
                    objs[obj3][4])
                
      #check if value at timeTable[r][c] is within range time-tol, time+tol
      #print o if it is, otherwise print .
      if empty == 0:
        file.write('o')
      else:
       file.write('.')
    
    file.write('\n') #newline
  file.write('\n') #newline


'''printTimeTable--------------------------------------------------------------
Prints a visualization of possible object locations for a single set of times

time1 - receiver 1 time
time2 - receiver 2 time
time3 - receiver 3 time
tol   - tolerance when comparing times to the grid of possible objects
----------------------------------------------------------------------------'''
def printTimeTable(time1, time2, time3, tol):

  file = open('timeTable', 'a')

  file.write('     ')
  for col in range(0, int(xRegion / xInc) + 1):
    file.write('{0:4.1f}|'.rjust(4).format(col * xInc - xRegion / 2))

  file.write('\n\n      ' +
             repr(round(xRegion * -1 / 2, 3)) + ' <-- ' +
             repr(round(xInc, 3)) + ' --> ' +
             repr(round(xRegion / 2, 3)) +
             '\n')

  for row in range(0, int(yRegion / yInc) + 1):
    #print leading label
    file.write('{0:4.1f} '.rjust(5).format(yRegion - yInc * row)) 

    for col in range(0, int(xRegion / xInc) + 1):
      #check if printing all or only matching times
      if time1 != 0 and time2 != 0 and time3 != 0:
        #printing times in matching range
        if col == (int(xRegion / xInc)) / 2 and row == int(yRegion / yInc):
          file.write('^')
        elif isInRange(time1 - tol, time1 + tol, timeTable[row][col][0]) == 0:
          file.write('.')
        elif isInRange(time2 - tol, time2 + tol, timeTable[row][col][1]) == 0:
          file.write('.')
        elif isInRange(time3 - tol, time3 + tol, timeTable[row][col][2]) == 0:
          file.write('.')
        else:
          file.write('o')
    
    file.write('\n') #newline
  file.write('\n') #newline

'''Driver----------------------------------------------------------------------
Initializes time table, object times, and prints time table through delegation
----------------------------------------------------------------------------'''
initTimeTable(xRegion, yRegion, xInc, yInc)

#print(timeTable) #DEBUG

#initialize objs array with times
for obj in range(0, NUM_OBJECTS):
  for rcvr in range(0, int(sensArr[0])):
    objs[obj][rcvr + 2] = calcTime(objs[obj][0], objs[obj][1], 
                                   sensArr[1] * (rcvr + 1))

#clear file, all subsequent writes append to this file
file = open('timeTable', 'w')
file.write('')

#print time table with all possible locs of objects
#printPossibleLocs(TOLERANCE)
'''
#single object ellipse intersection detection
for obj1 in range(0, NUM_OBJECTS):
  intersectEllipse(objs[obj1][2], objs[obj1][3], objs[obj1][4], TOL_DIST)
'''
#multiple object ellipse intersection detection
intersectEllipse
for obj1 in range(0, NUM_OBJECTS):
  for obj2 in range(0, NUM_OBJECTS):
    for obj3 in range(0, NUM_OBJECTS):
      intersectEllipse(objs[obj1][2], objs[obj2][3], objs[obj3][4], TOL_DIST)


'''Single Object Resolution----------------------------------------------------
Places single object relative to emitter, calculates times and displays all
matching locations on grid
----------------------------------------------------------------------------'''
'''
objX = 5
objY = 5

objT1 = calcTime(objX, objY, sensArr[1] * 1)
objT2 = calcTime(objX, objY, sensArr[1] * 2)
objT3 = calcTime(objX, objY, sensArr[1] * 3)

printTimeTable(objT1, objT2, objT3, TOLERANCE)
'''

'''Single Time Resolution------------------------------------------------------
Uses one set of times and displays all matching locations on grid
----------------------------------------------------------------------------'''
'''
time1 = 
time2 = 
time3 = 

printTimeTable(time1, time2, time3, TOLERANCE)
'''
