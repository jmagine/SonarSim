#!/usr/bin/env python

'''*-----------------------------------------------------------------------*---
                                                        Author: Jason Ma
                                                        Date  : Jun 12 2016
    File Name  : sonarSim1_0.py
    Description: Places several objects relative to an emitter, calculates
                 receiver times in a grid, and then prints a visualization of 
                 all possible object locations to a file named 'timeTable'.
---*-----------------------------------------------------------------------*'''

from __future__ import print_function
from __future__ import division
import numpy as np
from math import pow
#import matplotlib.pyplot as plt #TODO possibly implement this

#[RUN VARS]--------------------------------------------------------------------
NUM_SENSORS = 3
SPACING     = 0.3
SAMPLE_RATE = 200000
sensArr     = np.array([NUM_SENSORS, SPACING, SAMPLE_RATE])

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
SPEED_WAVE  = 1482

#------------------------------------------------------------------------------

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
initTimeTable(xRegion, yRegion, xInc, yInc, 0)

#print(timeTable) #DEBUG

#initialize objs array with times
for obj in range(0, NUM_OBJECTS):
  for rcvr in range(0, int(sensArr[0])):
    objs[obj][rcvr + 2] = calcTime(objs[obj][0], objs[obj][1], sensArr[1] * (rcvr + 1))

#clear file
file = open('timeTable', 'w')
file.write('')

#all subsequent writes append to that file

#print time table with all possible locs of objects
printPossibleLocs(TOLERANCE)

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
