import time

class Stopwatch:
  @classmethod
  def __get_time(cls):
    return time.perf_counter()

  def __init__(self):
    self.start()

  def start(self):
    self.__StartTime = Stopwatch.__get_time()

  def stop(self):
    return Stopwatch.__get_time() - self.__StartTime
