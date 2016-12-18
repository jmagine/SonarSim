 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Dec 17 2016
                                      TODO

 File Name:       util.cpp
 Description:     TODO
 Sources of help: TODO
 *****************************************************************************/

#include "util.h"

void Timer::start() {

  startTime = std::chrono::high_resolution_clock::now();

}

long long Timer::end() {

  std::chrono::time_point<std::chrono::high_resolution_clock> endTime;
  endTime = std::chrono::high_resolution_clock::now();

  return (long long)std::chrono::duration_cast<std::chrono::nanoseconds>(endTime-startTime).count();

}

bool isInRange(double lower, double upper, double value) {
  if(value >= lower && value <= upper)
    return true;
  return false;
}
