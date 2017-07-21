 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Jul 04 2017
                                      sonarSim

 File Name:       main.h
 Description:     TODO
 *****************************************************************************/

#ifndef MAIN_H
#define MAIN_H

#define NUM_TARGETS 100

void detectionAccuracySimulation(SensorTArray sensors, int numObjects);
void sigintHandler(int x);
void generateTimes(double times[4][NUM_TARGETS], double[NUM_TARGETS][3]);
void triangulateTargets(SensorTArray sensors, double times[4][NUM_TARGETS], double results[4][NUM_TARGETS * 2]);

#endif /* MAIN_H */
