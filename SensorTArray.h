 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Dec 15 2016
                                      sonarSim

 File Name:       SensorTArray.h
 Description:     Contains information about receiver positioning as well as 
                  environment variables.
 *****************************************************************************/

#ifndef SENSORTARRAY_H
#define SENSORTARRAY_H

#define SPEED_WAVE 1482 //in m/s
#define TOL_DIST 3      //in m
#define TOL_OBJ 0.25    //in m
#define NUM_SENSORS 4
#define DIMENSIONS 3

class SensorTArray {
  public:
    SensorTArray(double x1, double x2, double z, int sample);
    

    double sensArr[NUM_SENSORS][DIMENSIONS];
    int sampleRate;

  private:
    
};

#endif /* SENSORTARRAY_H */
