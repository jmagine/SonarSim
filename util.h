 /*****************************************************************************

                                                         Author: Jason Ma
                                                         Date:   Dec 17 2016
                                      TODO

 File Name:       util.h
 Description:     TODO
 Sources of help: TODO
 *****************************************************************************/

#include <chrono>

class Timer{
  private:
    std::chrono::time_point<std::chrono::high_resolution_clock> startTime;

  public:

    /*
     * Function called when starting the timer.
     */
    void start();

    /*
     * Function called when ending the timer. Returns duration in nanoseconds
     * PRECONDITION: begin_timer() must be called before this function
     */
    long long end();


};

bool isInRange(double lower, double upper, double value);
