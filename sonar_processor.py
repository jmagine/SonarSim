'''*-----------------------------------------------------------------------*---
                                                          Author: Jason Ma
                                                          Date  : Jun 25 2017

    File Name  : sonar_processor.py
    Description: Uses extracted peak times to determine target locations.
                         
---*-----------------------------------------------------------------------*'''

import threading
import time

'''----------------------------------------------------------------------------
Config variables
----------------------------------------------------------------------------'''


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
  
  '''[callback]----------------------------------------------------------------
    Used for notifying this thread about certain events
  --------------------------------------------------------------------------'''
  def callback(self, message):
    if message == 'end':
      self.end_callback = True
      print('[s_p] End callback received. Shutting down.')

    if message == 'go':
      self.go_callback = True

  '''[spin]--------------------------------------------------------------------
    Process latest data
  --------------------------------------------------------------------------'''
  def spin(self):
    print('[s_p] spinning')
    #read from the latest array of sonar times and process it
    found = 0
    run_count = 0

    for obj1 in range(num_objs):
      obj2 = 0

      while obj2 < num_objs and times[obj2][1] < times[obj1][0]
        obj2 += 1

      for obj2 in range(obj2, num_objs):
        

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

      time.sleep(0.1)
      print('[s_p] running')

      self.spin()
