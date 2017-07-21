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
#include <cstdlib>
#include "Trinar.h"
#include "SensorTArray.h"
#include "util.h"
#include "DSMClient.h"

using std::cout;
using std::cin;
using std::setw;
using std::endl;
using std::string;
using std::stoi;
using std::rand;

//TODO make these dependent on number of objects generated instead of constants
#define NUM_OBJECTS 8
#define EXTRA_FACTOR 2

void detectionAccuracySimulation(SensorTArray sensors, int numObjects);

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
  //SensorTArray sensors(-0.15, 0.25, 0.2, 200000);  
  //SensorTArray sensors(-0.3, 0.5, 0.4, 2000000);
  SensorTArray sensors(-0.25, 0.35, 0.2, 2000000);
  string input = "";

  while(input.compare("q") && input.compare("Q") && !cin.eof()) {
    cout << "+----------+" << endl;
    cout << "| SONARSIM |" << endl;
    cout << "+----------+----------------------------+" << endl;
    cout << "| 0 - Run detection accuracy simulation |" << endl;
    cout << "| 1 - Calc times for target             |" << endl;
    cout << "| q - Quit                              |" << endl;
    cout << "+---------------------------------------+" << endl;
    cout << ":";
    cin >> input;

    //if(!input.compare("0"))
    //  detectionAccuracySimulation(8);

    if(!input.compare("0")) {

      cout << "Number of objects:";
      cin >> input;

      detectionAccuracySimulation(sensors, stoi(input));

    }
    if(!input.compare("1")) {
      string x;
      string y;
      string z;
      double locs[3];
      double times[4];

      cout << "Enter x y z:";

      cin >> x >> y >> z;

      locs[0] = stod(x);
      locs[1] = stod(y);
      locs[2] = stod(z);

      Trinar::calcTime(locs, sensors, times, false, false);
      
      cout << "Times" << endl;
      cout << times[0] << " " << times[1] << " " << times[2] << " " << times[3] << endl;
    }
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
void detectionAccuracySimulation(SensorTArray sensors, int numObjects) {
  double objActualLocs[numObjects][3]; //contains array of objects
  double objPredLocs[numObjects * EXTRA_FACTOR][3];
  double times[numObjects][NUM_SENSORS];
  long long benchTime;
  int i, j, k, runCount, found, obj, obj1, obj2, obj3, obj4;
  bool successful;

  Timer timer;

  //init array of objects
  for(i = 0; i < numObjects; i++) {
    objActualLocs[i][0] = rand() % 100 - 50;
    objActualLocs[i][1] = rand() % 50;
    objActualLocs[i][2] = rand() % 100 - 50;
    cout << i << ": " << setw(10) << objActualLocs[i][0] << " " << 
            setw(10) << objActualLocs[i][1] << " " << 
            setw(10) << objActualLocs[i][2] << endl;
  }
 
  //TODO implement read in from a file
  
  //calculate times for each object and receiver pair
  for(obj = 0; obj < numObjects; obj++) {
    Trinar::calcTime(objActualLocs[obj], sensors, times[obj], false, false);
  }

  cout << "DEBUG - Printing times" << endl;
  //TODO debug
  for(i = 0; i < numObjects; i++) {
    cout << i << ": ";

    for(j = 0; j < 4; j++) {
      cout << setw(10) << times[i][j] << " ";
    }
    cout << endl;
  }
  cout << "Printing times complete" << endl << endl;

  //sort times to simulate real data.
  //also, this way range checks can skip more intelligently
  //for each receiver
  for(i = 0; i < 4; i++) {
    //selection min sort on times
    for(j = 0; j < numObjects; j++) {

      double min = 1000;
      int minInd = -1;
      
      //find minimum time
      for(k = j; k < numObjects; k++) {
        if(times[k][i] < min) {
          min = times[k][i];
          minInd = k;
        }
      }

      //swap minimum time
      if(minInd != -1) {
        double temp = times[j][i];
        times[j][i] = times[minInd][i];
        times[minInd][i] = temp;
      }
    }
  }

  cout << "DEBUG - Printing sorted times" << endl;
  //TODO debug
  for(i = 0; i < numObjects; i++) {
    cout << i << ": ";

    for(j = 0; j < 4; j++) {
      cout << setw(10) << times[i][j] << " ";
    }
    cout << endl;
  }
  cout << "Printing times complete" << endl << endl;

  double timeTol01 = (sensors.sensArr[0][0] - sensors.sensArr[1][0]) / SPEED_WAVE;
  double timeTol02 = (sensors.sensArr[2][0] - sensors.sensArr[0][0]) / SPEED_WAVE;
  double timeTol03 = (sensors.sensArr[3][2] - sensors.sensArr[0][2]) / SPEED_WAVE;

  timer.start();
  found = 0;
  runCount = 0;
  //i = 0;

  
  for(obj1 = 0; obj1 < numObjects; obj1++) {
    obj2 = 0;
    
    //find lowest times that fall within range
    while(times[obj2][1] < times[obj1][0] - timeTol01 && obj2 < numObjects)
      obj2++;
       
    //start iterating through each combination of times from rcvrs 1-4
    for(; obj2 < numObjects && times[obj2][1] <= times[obj1][0] + timeTol01; obj2++) {
       obj3 = 0;
       while(times[obj3][2] < times[obj1][0] - timeTol02 && obj3 < numObjects)
         obj3++;

      //need to reset obj3
      for(; obj3 < numObjects && times[obj3][2] <= times[obj1][0] + timeTol02; obj3++) {
        obj4 = 0;
        while(times[obj4][3] < times[obj1][0] - timeTol03 && obj4 < numObjects)
          obj4++;

        //need to reset obj4
        for(; obj4 < numObjects && times[obj4][3] <= times[obj1][0] + timeTol03; obj4++) {
          
          //make sure none of the times have already been removed
          if(times[obj1][0] == 0 || times[obj2][1] == 0 || 
             times[obj3][2] == 0 || times[obj4][3] == 0)
            continue;

          successful = Trinar::resolveTArray(times[obj1][0], times[obj2][1], 
              times[obj3][2], times[obj4][3], sensors, objPredLocs[found], 
              TOL_DIST, false);
          runCount++;

          if(successful) {
            //check for duplicate positioning or close positioning of targets
            bool dup = false;

            for(j = 0; j < found; j++) {
              if(isInRange(objPredLocs[j][0] - TOL_OBJ, 
                      objPredLocs[j][0] + TOL_OBJ, objPredLocs[found][0]) &&
                  isInRange(objPredLocs[j][1] - TOL_OBJ, 
                      objPredLocs[j][1] + TOL_OBJ, objPredLocs[found][1]) &&
                  isInRange(objPredLocs[j][2] - TOL_OBJ, 
                      objPredLocs[j][2] + TOL_OBJ, objPredLocs[found][2]))
                dup = true;
            }
            
            //set this result in stone and remove times from times array
            if(!dup) {
              times[obj1][0] = 0;
              times[obj2][1] = 0;
              times[obj3][2] = 0;
              times[obj4][3] = 0;
              //i++;
              found++;

              cout << "Found: " << found << " " << endl;
            }
          }
        }
      }
    }
  }

  benchTime = timer.end();

  for(i = 0; i < numObjects; i++) {
    cout << i << ": ";
    for(j = 0; j < 4; j++) {
      cout << times[i][j] << " ";
    }
    cout << endl; 
  }

  //TODO sort found positions to correspond to actual positions if possible
  //need to account for both when actual < found and actual > found

  cout << "-------------------------------------------------" << endl;
  cout << "    Actual positions    |    Found positions     " << endl;
  cout << "-------------------------------------------------" << endl;
  for(i = 0; i < numObjects; i++) {
    cout << i << ": " << setw(3) << objActualLocs[i][0] << " " << 
                         setw(3) << objActualLocs[i][1] << " " << 
                         setw(3) << objActualLocs[i][2] << " | ";

    if(i < found) {
      cout << setw(10) << objPredLocs[i][0] << " " <<
              setw(10) << objPredLocs[i][1] << " " <<
              setw(10) << objPredLocs[i][2] << endl;
    }
    else
      cout << endl;
  }
  cout << endl;
  cout << "===== Detection Accuracy Simulation Results =====" << endl;
  cout << "Rcvr min time diffs: " << setw(7) << timeTol01 << " " <<
                                            setw(7) << timeTol02 << " " <<
                                            setw(7) << timeTol03 << endl;
  cout << "Time : " << benchTime / 1000000.0 << " ms" << endl;
  cout << "Runs : " << runCount << endl;
  cout << "Found: " << found << endl;
  cout << "-------------------------------------------------" << endl;
  cout << endl;

}
