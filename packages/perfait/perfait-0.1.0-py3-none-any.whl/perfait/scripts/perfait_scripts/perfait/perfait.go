package perfait

import (
  "time"
)

func __get_time()(float64){
  nowTime := time.Now()
  return float64(nowTime.Unix()) + (float64(nowTime.UnixNano()) / 1000000000)
}

type Stopwatch struct {
  __StartTime float64
}

func StopwatchNew()(*Stopwatch){
  stopwatch := &Stopwatch{}
  stopwatch.Start()
  return stopwatch
}

func (stopwatch *Stopwatch)Start(){
  stopwatch.__StartTime = __get_time()
}

func (stopwatch *Stopwatch)Stop()(float64){
  return __get_time() - stopwatch.__StartTime
}
