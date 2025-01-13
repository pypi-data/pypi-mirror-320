from pyemon.task import *
from pyemon.status import *
from pyemon.command import *
import os

class InitTask(Task):
  def run(self, argv):
    srcRootDir = os.path.abspath("""{}/../scripts""".format(os.path.dirname(__file__)))

    for scriptDir in ["perfait_scripts"]:
      Command.rmkdir(scriptDir)
      for path in Command.find("""{}/{}/*.*""".format(srcRootDir, scriptDir)):
        self.copy(os.path.dirname(path), scriptDir, os.path.basename(path))

    for scriptDir in ["perfait_scripts/perfait"]:
      Command.mkdir(scriptDir)
      for path in Command.find("""{}/{}/*.*""".format(srcRootDir, scriptDir)):
        self.copy(os.path.dirname(path), scriptDir, os.path.basename(path))
Task.parse_if_main(__name__, InitTask())
