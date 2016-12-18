 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Dec 15 2016
                                      sonarSim

 File Name:       Trinar.h
 Description:     TODO
 *****************************************************************************/

#ifndef TRINAR_H
#define TRINAR_H

#include "SensorTArray.h"

class Trinar {

  public:
     static bool CEIntersect(double a, double b, double c, double result[2]);
    
    //possible alternative
    //TODO resolveTArray(double times[4], double tol, bool debug);
    static bool resolveTArray(double t1, double t2, double t3, double t4, SensorTArray sensors, double result[3], double tol, bool debug);
    
    //TODO same alternative applies here
    static void calcTime(double obj[3], SensorTArray sensors, double result[4], bool exact, bool debug);
    static double calcTime(double xObj, double yObj, double zObj, double xRcvr, double yRcvr, double zRcvr, int sampleRate, bool exact, bool debug);

    static void readTimes();

  private:
    double times[][4];
};

#endif /* TRINAR_H */
