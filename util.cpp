 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Dec 17 2016
                                      sonarSim

 File Name:       util.cpp
 Description:     Contains timer and range check functions for ease of use
 *****************************************************************************/

#include "util.h"

 /********************************************************************
 | Routine Name: start
 | File:         util.cpp
 | 
 | Description: Starts timer
 ********************************************************************/
void Timer::start() {

  startTime = std::chrono::high_resolution_clock::now();

}

 /********************************************************************
 | Routine Name: end
 | File:         util.cpp
 | 
 | Description: Stops timer and returns time since started
 | 
 | Precondition: start() must be called first!
 | 
 | Parameter Descriptions:
 | name               description
 | ------------------ -----------------------------------------------
 | return             time since started in nanoseconds (10E-9s)
 ********************************************************************/
long long Timer::end() {

  std::chrono::time_point<std::chrono::high_resolution_clock> endTime;
  endTime = std::chrono::high_resolution_clock::now();

  return (long long)std::chrono::duration_cast<std::chrono::nanoseconds>(endTime-startTime).count();

}

 /********************************************************************
 | Routine Name: isInRange
 | File:         util.cpp
 | 
 | Description: Checks whether value is in range of the lower and upper bound.
 |              This check is inclusive on both bounds.
 | 
 | Parameter Descriptions:
 | name               description
 | ------------------ -----------------------------------------------
 | lower              lower bound
 | upper              upper bound
 | value              value to check
 | return             true if within bounds (inclusive), false otherwise
 ********************************************************************/
bool isInRange(double lower, double upper, double value) {
  if(value >= lower && value <= upper)
    return true;
  return false;
}
