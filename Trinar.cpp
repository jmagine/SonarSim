 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Dec 15 2016
                                      sonarSim

 File Name:       Trinar.cpp
 Description:     TODO
 *****************************************************************************/

#include <iostream>
#include <cmath>
#include "Trinar.h"
#include "SensorTArray.h"
#include "util.h"

using namespace std;



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

bool Trinar::resolveTArray(double t1, double t2, double t3, double t4, SensorTArray sensors, double result[3], double tol, bool debug) {
  int ellipse;
  int i, j;
  bool successful;
  bool found;
  bool resultFound;

  //
  double rcvr[3][2] = {0};
  double circY[2][2] = {0};
  double ySqr[3][2] = {0};
  double intersects[2] = {0};
  double tempIntersect[6][2] = {0};
  double ei[3][3] = {0};
  double r2;

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

  for(ellipse = 0; ellipse < 3; ellipse++) {
    ei[ellipse][0] = rcvr[ellipse][0] / 2.0;
    ei[ellipse][1] = pow(rcvr[ellipse][1] * SPEED_WAVE / 2.0, 2);
    ei[ellipse][2] = ei[ellipse][1] - pow(ei[ellipse][0], 2);

    successful = CEIntersect(ei[ellipse][0], ei[ellipse][1], r2, intersects);

    if(successful) {
      //calculate x locs of intersections
      tempIntersect[ellipse * 2][0] = intersects[0];
      tempIntersect[ellipse * 2 + 1][0] = intersects[1];

      //calculate y^2 for any found xs
      for(i = 0; i < 2; i++) {
        ySqr[ellipse][i % 2] = r2 - pow(tempIntersect[ellipse * 2 + i][0], 2);

        if((tempIntersect[ellipse * 2 + i][0] != 0) && (ySqr[ellipse][i % 2] >= 0)) {
          tempIntersect[ellipse * 2 + i][1] = sqrt(ySqr[ellipse][i % 2]);
        }
      }

      if(ellipse == 1) {
        found = false;

        //try all 4 possible intersection points with tolerance against 3rd ellipse
        for(i = 0; i < 2; i++)
          for(j = 2; j < 4; j++)
            if(tempIntersect[i][0] != 0 && isInRange(tempIntersect[i][0] - tol, tempIntersect[i][0] + tol,
                           tempIntersect[j][0])) {
              found = true;
              result[0] = tempIntersect[i][0];
              result[1] = tempIntersect[i][1];
              
            }

        if(!found)
          break;
      }
      else if(ellipse == 2) {
        //circle circle intersections in 3D space

        for(i = 4; i < 6; i++) {
          if(tempIntersect[i][1] != 0) {
            circY[i % 2][0] = pow(result[1], 2) - pow(tempIntersect[i][0], 2);
            circY[i % 2][1] = pow(tempIntersect[i][1], 2) - pow(result[0], 2);

            if(circY[i % 2][0] < 0 || circY[i % 2][1] < 0)
              continue;

            circY[i % 2][0] = sqrt(circY[i % 2][0]);
            circY[i % 2][1] = sqrt(circY[i % 2][1]);

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

void Trinar::calcTime(double obj[3], SensorTArray sensors, double result[4], bool exact, bool debug) {
  double distEO = sqrt(pow(obj[0], 2) + 
                       pow(obj[1], 2) + 
                       pow(obj[2], 2));
  int i;

  if(debug)
    cout << "DEBUG - CT --"; 

  for(i = 0; i < 4; i++) {
    double distOR = sqrt(pow(obj[0] - sensors.sensArr[i][0], 2) + 
                         pow(obj[1] - sensors.sensArr[i][1], 2) + 
                         pow(obj[2] - sensors.sensArr[i][2], 2));
    double totalTime = (distEO + distOR) / SPEED_WAVE;

    if(exact) {
      result[i] = totalTime;
    }
    else {
      result[i] = totalTime - fmod(totalTime, 1.0 / sensors.sampleRate) + (1.0 / sensors.sampleRate);
    }

    if(debug)
      cout << result[i] << " ";
  }

  if(debug)
    cout << endl;
}

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
