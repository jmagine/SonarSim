 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Dec 15 2016
                                      sonarSim

 File Name:       sonarSim.cpp
 Description:     Contains tools for simulating and benchmarking sonar
                  algorithms. 
 *****************************************************************************/

#include <iostream>
#include <iomanip>
#include <string>
#include "sonarSim.h"
#include "Trinar.h"
#include "SensorTArray.h"
#include "util.h"

using std::cout;
using std::cin;
using std::setw;
using std::endl;
using std::string;

//TODO make these dependent on number of objects generated instead of constants
#define NUM_OBJECTS 8
#define EXTRA_FACTOR 2

void detectionAccuracySimulation(int numObjects);

 /********************************************************************
 | Routine Name: main
 | File:         sonarSim.cpp
 | 
 | Description: Driver, runs tests used in the simulation based on user input.
 |
 | Parameter Descriptions:
 | name               description
 | ------------------ -----------------------------------------------
 | return             0 on successful run
 ********************************************************************/
int main(int argc, char * argv[]) {
  string input = "";

  while(input.compare("q") && input.compare("Q") && !cin.eof()) {
    cout << "+----------+" << endl;
    cout << "| SONARSIM |" << endl;
    cout << "+----------+----------------------------+" << endl;
    cout << "| 0 - Run detection accuracy simulation |" << endl;
    cout << "| q - Quit                              |" << endl;
    cout << "+---------------------------------------+" << endl;
    cout << ":";
    cin >> input;

    if(!input.compare("0"))
      detectionAccuracySimulation(8);
  }

  cout << endl;
  
  return 0;
}

 /********************************************************************
 | Routine Name: detectionAccuracySimulation
 | File:         sonarSim.cpp
 | 
 | Description: Generates object locations, calculates processed times that
 |              actual receivers would produce, and attempts to resolve target
 |              positions from those times.
 |
 | Parameter Descriptions:
 | name               description
 | ------------------ -----------------------------------------------
 | numObjects         number of objects to simulate
 ********************************************************************/
void detectionAccuracySimulation(int numObjects) {
  double objActualLocs[numObjects][3]; //contains array of objects
  double objPredLocs[numObjects * EXTRA_FACTOR][3];
  double times[numObjects][NUM_SENSORS];
  long long benchTime;
  int i, j, runCount, found, obj, obj1, obj2, obj3, obj4;
  bool successful;

  SensorTArray sensors(-0.15, 0.25, 0.2, 200000);
  Timer timer;
  
  //TODO this is disgusting
  objActualLocs[0][0]    = -1;
  objActualLocs[0][1]    = 10;
  objActualLocs[0][2]    = 0;

  objActualLocs[1][0]    = -3;
  objActualLocs[1][1]    = 10;
  objActualLocs[1][2]    = 0;

  objActualLocs[2][0]    = -5;
  objActualLocs[2][1]    = 20;
  objActualLocs[2][2]    = -7;

  objActualLocs[3][0]    = -4;
  objActualLocs[3][1]    = 21;
  objActualLocs[3][2]    = -6.8;

  objActualLocs[4][0]    = -3;
  objActualLocs[4][1]    = 22;
  objActualLocs[4][2]    = -6.9;

  objActualLocs[5][0]    = -10;
  objActualLocs[5][1]    = 30;
  objActualLocs[5][2]    = -4;

  objActualLocs[6][0]    = -20;
  objActualLocs[6][1]    = 25;
  objActualLocs[6][2]    = -10;

  objActualLocs[7][0]    = -20;
  objActualLocs[7][1]    = 50;
  objActualLocs[7][2]    = -10;

  //init array of objects. TODO read in from a file

  //calculate times for each object and receiver pair
  for(obj = 0; obj < numObjects; obj++) {
    Trinar::calcTime(objActualLocs[obj], sensors, times[obj], false, false);
  }

  double timeTol01 = (sensors.sensArr[0][0] - sensors.sensArr[1][0]) / SPEED_WAVE;
  double timeTol02 = (sensors.sensArr[2][0] - sensors.sensArr[0][0]) / SPEED_WAVE;
  double timeTol03 = (sensors.sensArr[3][2] - sensors.sensArr[0][2]) / SPEED_WAVE;

  timer.start();
  found = 0;
  runCount = 0;
  i = 0;
  for(obj1 = 0; obj1 < numObjects; obj1++) {
    for(obj2 = 0; obj2 < numObjects; obj2++) {
      for(obj3 = 0; obj3 < numObjects; obj3++) {
        for(obj4 = 0; obj4 < numObjects; obj4++) {
          if(times[obj1][0] == 0 || times[obj2][1] == 0 || 
             times[obj3][2] == 0 || times[obj4][3] == 0)
            continue;

          if(!isInRange(times[obj1][0] - timeTol01, times[obj1][0] + timeTol01, times[obj2][1]))
            continue;

          if(!isInRange(times[obj1][0] - timeTol02, times[obj1][0] + timeTol02, times[obj3][2]))
            continue;
          
          if(!isInRange(times[obj1][0] - timeTol03, times[obj1][0] + timeTol03, times[obj4][3]))
            continue;

          successful = Trinar::resolveTArray(times[obj1][0], times[obj2][1], 
              times[obj3][2], times[obj4][3], sensors, objPredLocs[i], 
              TOL_DIST, false);
          runCount++;

          if(successful) {

            //check for duplicate positioning or close positioning of targets
            bool dup = false;

            for(j = 0; j < i; j++) {
              if(isInRange(objPredLocs[j][0] - TOL_OBJ, 
                      objPredLocs[j][0] + TOL_OBJ, objPredLocs[i][0]) &&
                  isInRange(objPredLocs[j][1] - TOL_OBJ, 
                      objPredLocs[j][1] + TOL_OBJ, objPredLocs[i][1]) &&
                  isInRange(objPredLocs[j][2] - TOL_OBJ, 
                      objPredLocs[j][2] + TOL_OBJ, objPredLocs[i][2]))
                dup = true;
            }
            
            //set this result in stone and remove times from times array
            if(!dup) {
              times[obj1][0] = 0;
              times[obj2][1] = 0;
              times[obj3][2] = 0;
              times[obj4][3] = 0;
              i++;
              found++;
            }
          }
        }
      }
    }
  }

  benchTime = timer.end();
  
  cout << "--- Detection Accuracy Simulation Results ---" << endl;
  cout << "Rcvr time closeness bounds: " << setw(10) << timeTol01 << " " <<
                                            setw(10) << timeTol02 << " " <<
                                            setw(10) << timeTol03 << endl;
  cout << "Time : " << benchTime / 1000000.0 << " ms" << endl;
  cout << "Runs : " << runCount << endl;
  cout << "Found: " << found << endl;    
  cout << "---------------------------------------------" << endl;
  for(obj = 0; obj < found; obj++) {
    cout << setw(10) << objPredLocs[obj][0] << " " <<
            setw(10) << objPredLocs[obj][1] << " " <<
            setw(10) << objPredLocs[obj][2] << endl;
  }

  cout << endl;

}
