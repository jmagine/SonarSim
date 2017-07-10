'''*-----------------------------------------------------------------------*---
                                                          Author: Jason Ma
                                                          Date  : Jun 25 2017

    File Name  : top_level_sonar.py
    Description: Capable of interfacing with FPGA board, performing live sonar,
                 and outputting results to DSM buffers. 
                 
                 .-------------top_level_sonar-----------.
                /     /              |          \         \

                         
---*-----------------------------------------------------------------------*'''

import sonar_processor
import sys
import time
'''----------------------------------------------------------------------------
Config variables
----------------------------------------------------------------------------'''
USE_DSM = True
CLIENT_SERV = 42
CLIENT_ID = 0

HYDROPHONE_POS = [[0] * 2] * 4

HYDROPHONE_POS[0][0] = 0
HYDROPHONE_POS[0][1] = 0

HYDROPHONE_POS[1][0] = -0.15
HYDROPHONE_POS[1][1] = 0

HYDROPHONE_POS[2][0] = 0.25
HYDROPHONE_POS[2][1] = 0

HYDROPHONE_POS[3][0] = 0
HYDROPHONE_POS[3][1] = 0.2

'''----------------------------------------------------------------------------
Conditional imports
----------------------------------------------------------------------------'''
if USE_DSM:
  sys.path.insert(0, './DistributedSharedMemory/build')
  sys.path.insert(0, './PythonSharedBuffers/src')
  import pydsm

'''[main]----------------------------------------------------------------------
  Initializes profiler, processor, and DSMClient. Then monitors status of the
  processor/profiler, keeps things in sync, and outputs to DSM buffers.
----------------------------------------------------------------------------'''
def main():
  try:

    print('[main] Initializing model')
    #model = model(HYDROPHONE_POS)
    print('[main] Initializing threads')
    #start profiler
    #pf = sonar_profiler()

    #start processor
    s_p = sonar_processor.sonar_processor()

    print('[main] Starting DSM')
    #begin interfacing with DSM
    client = pydsm.Client(CLIENT_SERV, CLIENT_ID, True)

    print('[main] Starting threads')
    #pf.start()
    s_p.start()
    
    #TODO probably don't need to reg remote buffers, but if need to, it is here
    #for i in range(len(bufNames)):
    #  client.registerRemoteBuffer(bufNames[i], bufIps[i], int(bufIds[i]))
    
    for i in range(100):
      s_p.callback('go')

      print(str(s_p.found_locs))

      time.sleep(0.5)

    pc.join()
  except KeyboardInterrupt:
    print('\n[main] Ctrl+c received. Ending program')

    #send end_callbacks to all threads
    s_p.callback('end')
    
    sys.exit(1)

  print('[main] Ending program')

if __name__ == '__main__':
  main()
