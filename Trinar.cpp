 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Dec 15 2016
                                      sonarSim

 File Name:       Trinar.cpp
 Description:     Contains ellipse triangulation functions for calculating
                  positions of objects as well as exact/simulated times given
                  and object and SensorTArray.
 *****************************************************************************/

#include <iostream>
#include <cmath>
#include "Trinar.h"
#include "SensorTArray.h"
#include "util.h"

using std::cout;
using std::endl;

 /********************************************************************
 | Routine Name: CEIntersect
 | File:         Trinar.cpp
 | 
 | Description: Circle-ellipse intersection calculator, attempts to find x
 |              locations of intersection between this circle and ellipse.
 | 
 | Parameter Descriptions:
 | name               description
 | ------------------ -----------------------------------------------
 | a                  
 | b                  
 | c                  
 | result             x locations of intersections
 | return             true if successful, false if unsuccessful
 ********************************************************************/
bool Trinar::CEIntersect(double a, double b, double c, double result[2]) {
  double d = pow(a, 2) * c / b;

  if(d < 0) {
    cout << "d: " << d << endl;
    return false;
  }

  d = b * sqrt(d);

  result[0] = (pow(a, 3) - d - a * b) / pow(a, 2);
  result[1] = (pow(a, 3) + d - a * b) / pow(a, 2);
  return true;
}

 /********************************************************************
 | Routine Name: resolveTArray
 | File:         Trinar.cpp
 | 
 | Description: Attempts to resolve the 4 given times using the SensorTArray
 |              and specified tolerance.
 | 
 | Parameter Descriptions:
 | name               description
 | ------------------ -----------------------------------------------
 | t1                 time to receiver 1
 | t2                 time to receiver 2
 | t3                 time to receiver 3
 | t4                 time to receiver 4
 | sensors            sensor array containing positions of the receivers
 | result             x, y, and z location of target if found
 | tol                tolerance for circle circle intersection distance
 | debug              whether to print debug statements
 | return             true if successful resolution, false otherwise.
 ********************************************************************/
bool Trinar::resolveTArray(double t1, double t2, double t3, double t4, SensorTArray sensors, double result[3], double tol, bool debug) {

  double tempIntersect[6][2] = {0};
  double ei[3][3] = {0};
  double rcvr[3][2] = {0};
  double ySqr[3][2] = {0};
  double circY[2][2] = {0};  
  double intersects[2] = {0};
  double r2;
  int ellipse;
  int i, j;
  bool successful;
  bool found;
  bool resultFound;

  r2 = pow(t1 * SPEED_WAVE / 2, 2);

  rcvr[0][0] = sensors.sensArr[1][0];
  rcvr[1][0] = sensors.sensArr[2][0];
  rcvr[2][0] = sensors.sensArr[3][2];

  rcvr[0][1] = t2;
  rcvr[1][1] = t3;
  rcvr[2][1] = t4;

  result[0] = 0;
  result[1] = 0;
  result[2] = 0;

  resultFound = false;

  //perform 3 ellipse circle intersections - r2, r3, and r4 intersected with r1

  for(ellipse = 0; ellipse < 3; ellipse++) {
    ei[ellipse][0] = rcvr[ellipse][0] / 2.0;
    ei[ellipse][1] = pow(rcvr[ellipse][1] * SPEED_WAVE / 2.0, 2);
    ei[ellipse][2] = ei[ellipse][1] - pow(ei[ellipse][0], 2);

    successful = CEIntersect(ei[ellipse][0], ei[ellipse][1], r2, intersects);

    //on intersection
    if(successful) {
      //get x locs of intersections
      tempIntersect[ellipse * 2][0] = intersects[0];
      tempIntersect[ellipse * 2 + 1][0] = intersects[1];

      //calculate y^2 for all found xs
      for(i = 0; i < 2; i++) {
        ySqr[ellipse][i % 2] = r2 - pow(tempIntersect[ellipse * 2 + i][0], 2);

        //store intersection coordinates in unique locations for each ellipse
        //this is for debug printing later
        if((tempIntersect[ellipse * 2 + i][0] != 0) && (ySqr[ellipse][i % 2] >= 0)) {
          tempIntersect[ellipse * 2 + i][1] = sqrt(ySqr[ellipse][i % 2]);
        }
      }

      //when 2 ellipse intersections have been calculated, attempt to resolve
      //a point in 2D space which can be rotated around the x axis later.
      if(ellipse == 1) {
        found = false;

        for(i = 0; i < 2; i++)
          for(j = 2; j < 4; j++)
            if(tempIntersect[i][0] != 0 && isInRange(tempIntersect[i][0] - tol, tempIntersect[i][0] + tol,
                           tempIntersect[j][0])) {
              found = true;
              result[0] = tempIntersect[i][0];
              result[1] = tempIntersect[i][1];
              
            }

        //end computation early if nothing is found
        if(!found)
          break;
      }
      //do circle circle intersections to resolve for point in 3D space.
      else if(ellipse == 2) {

        for(i = 4; i < 6; i++) {
          if(tempIntersect[i][1] != 0) {
            circY[i % 2][0] = pow(result[1], 2) - pow(tempIntersect[i][0], 2);
            circY[i % 2][1] = pow(tempIntersect[i][1], 2) - pow(result[0], 2);

            if(circY[i % 2][0] < 0 || circY[i % 2][1] < 0)
              continue;

            circY[i % 2][0] = sqrt(circY[i % 2][0]);
            circY[i % 2][1] = sqrt(circY[i % 2][1]);

            //if circles come close enough to intersection, result is found.
            if(isInRange(circY[i % 2][1] - tol, circY[i % 2][1] + tol, circY[i % 2][0])) {
              result[1] = (circY[i % 2][0] + circY[i % 2][1]) / 2.0;
              result[2] = tempIntersect[i][0];
              resultFound = true;
            }
          }
        }
      }

    }
  }

  
  if(debug) {
    //TODO print debug statements
    cout << "DEBUG - resolveTArray" << endl;
  }

  return resultFound;
}

 /********************************************************************
 | Routine Name: calcTime
 | File:         Trinar.cpp
 | 
 | Description: Calculates times received by each receiver when an object is
 |              placed at a certain location.
 | 
 | Parameter Descriptions:
 | name               description
 | ------------------ -----------------------------------------------
 | obj                contains x, y, and z locations of object
 | sensors            contains information on the locations/processing speed
                      of the sensors
 | result             where times are stored for each of the receivers
 | exact              whether to store exact time or processed time
 | debug              whether to print debug statements
 ********************************************************************/
void Trinar::calcTime(double obj[3], SensorTArray sensors, double result[4], bool exact, bool debug) {
  
  int i;

  //calculate distance from emitter to object
  double distEO = sqrt(pow(obj[0], 2) + 
                       pow(obj[1], 2) + 
                       pow(obj[2], 2));

  //for each receiver
  for(i = 0; i < 4; i++) {
    //calculate distance from object to receiver and then total time.
    double distOR = sqrt(pow(obj[0] - sensors.sensArr[i][0], 2) + 
                         pow(obj[1] - sensors.sensArr[i][1], 2) + 
                         pow(obj[2] - sensors.sensArr[i][2], 2));

    double totalTime = (distEO + distOR) / SPEED_WAVE;

    //record this time in result

    //record exact time
    if(exact) {
      result[i] = totalTime;
    }
    //record processed time (in units of 1/sampleRate rounded up)
    else {
      result[i] = totalTime - fmod(totalTime, 1.0 / sensors.sampleRate) + (1.0 / sensors.sampleRate);
    }

    if(debug)
      cout << result[i] << " ";
  }

  if(debug)
    cout << endl;
}

 /********************************************************************
 | Routine Name: calcTime
 | File:         Trinar.cpp
 | 
 | Description: Calculates time received by individual receiver when object
 |              is placed at specified location.
 | 
 | Parameter Descriptions:
 | name               description
 | ------------------ -----------------------------------------------
 | xObj               x location of object
 | yObj               y location of object
 | zObj               z location of object
 | xRcvr              x location of receiver
 | yRcvr              y location of receiver
 | zRcvr              z location of receiver
 | sampleRate         sample rate of receiver (only matters if exact == false)
 | exact              whether to return exact or processed time
 | debug              whether to print debug statements
 | return             calculated time
 ********************************************************************/
double Trinar::calcTime(double xObj, double yObj, double zObj, double xRcvr, double yRcvr, double zRcvr, int sampleRate, bool exact, bool debug) {
  double distEO = sqrt(pow(xObj, 2) + 
                       pow(yObj, 2) + 
                       pow(zObj, 2));
  double distOR = sqrt(pow(xObj - xRcvr, 2) + 
                       pow(yObj - yRcvr, 2) + 
                       pow(zObj - zRcvr, 2));
  double totalTime = (distEO + distOR) / SPEED_WAVE;

  //TODO add actual prints
  if(debug)
    cout << "DEBUG - CT" << endl;

  if(exact)
    return totalTime;

  return totalTime - fmod(totalTime, 1.0 / sampleRate) + (1.0 / sampleRate);
}

void readTimes() {

}
