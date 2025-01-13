import sys
import time
import gc
import subprocess

def measure_command(maxCount, args):
  elapsedTimes = []
  for _ in range(maxCount):
    gc.disable()
    startTime = time.perf_counter()
    result = subprocess.run(args, capture_output = True, text = True, encoding = "utf-8")
    elapsedTime = time.perf_counter() - startTime
    gc.enable()
    try:
      internalElapsedTime = float(result.stdout)
    except:
      internalElapsedTime = elapsedTime
    externalElapsedTime = elapsedTime - internalElapsedTime
    if externalElapsedTime < 0.0:
      internalElapsedTime = elapsedTime
      externalElapsedTime = 0.0
    elapsedTimes.append([internalElapsedTime, externalElapsedTime, result.stdout, result.stderr])
  elapsedTimes.sort(key = lambda value: value[0])
  centerIndex = int(len(elapsedTimes) / 2)
  return {
    "internalElapsedTime": elapsedTimes[centerIndex][0],
    "externalElapsedTime": elapsedTimes[centerIndex][1],
    "stdout": elapsedTimes[centerIndex][2],
    "stderr": elapsedTimes[centerIndex][3],
  }

if __name__ == "__main__":
  args = sys.argv[1:]
  maxCount = int(args.pop(0))
  print(measure_command(maxCount, args))
