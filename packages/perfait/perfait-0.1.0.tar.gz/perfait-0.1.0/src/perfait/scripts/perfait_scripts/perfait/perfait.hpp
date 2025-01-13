#ifndef __PERFAIT_H__
#define __PERFAIT_H__
#include <cstdlib>
#include <stdio.h>
#include <time.h>

namespace Perfait {
  class Stopwatch {
    private:
      static double __GetTime(){
        struct timespec ts;
        clock_gettime(CLOCK_REALTIME, &ts);
        return (double)ts.tv_sec + ((double)ts.tv_nsec / 1000000000);
      }

      double __StartTime;

    public:
      Stopwatch(){
        Start();
      }

      void Start(){
        __StartTime = __GetTime();
      }

      double Stop(){
        return __GetTime() - __StartTime;
      }
  };
}
#endif
