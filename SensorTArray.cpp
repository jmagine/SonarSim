 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Dec 15 2016
                                      TODO

 File Name:       SensorTArray.cpp
 Description:     TODO
 Sources of help: TODO
 *****************************************************************************/

#include "SensorTArray.h"

 /********************************************************************
 | Routine Name: SensorTArray
 | File:         SensorTArray.cpp
 | 
 | Description: Constructor, Initializes the sensor array's positions according
 |              to passed in parameters.
 | 
 | Parameter Descriptions:
 | name               description
 | ------------------ -----------------------------------------------
 | x1                 x offset of sensor 1
 | x2                 x offset of sensor 2
 | z                  z offset of sensor 3
 ********************************************************************/
SensorTArray::SensorTArray(double x1, double x2, double z, int sample) {
  int i, j;
  
  for(i = 0; i < NUM_SENSORS; i++)
    for(j = 0; j < DIMENSIONS; j++)
      sensArr[i][j] = 0;

  sensArr[1][0] = x1;
  sensArr[2][0] = x2;
  sensArr[3][2] = z;

  sampleRate = sample;
}
