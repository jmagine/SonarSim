 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Dec 17 2016
                                      sonarSim

 File Name:       util.h
 Description:     Contains timer and range check functions for ease of use
 *****************************************************************************/

#include <chrono>

class Timer{
  private:
    std::chrono::time_point<std::chrono::high_resolution_clock> startTime;

  public:

    void start();

    long long end();

};

bool isInRange(double lower, double upper, double value);
