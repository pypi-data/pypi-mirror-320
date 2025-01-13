from .tasks.init import *
from pyemon.list import *
from pyemon.path import *
from pyemon.string import *
from pyemon.status import *
import graspgraph as gg

class ImageWriteTask(Task):
  def run(self, argv):
    perfaitFilePath = List.shift(argv)
    ext = Path.from_file_path(perfaitFilePath).Ext
    match ext:
      case "json":
        perfait = Command.json_load(perfaitFilePath)
      case "yaml":
        perfait = Command.yaml_load(perfaitFilePath)
      case _:
        perfait = None
    imageFilePath = List.shift(argv)
    if perfait is None or imageFilePath is None:
      return
    pivotgraph = gg.Pivotgraph(gg.PivotgraphAxis(gg.PivotTable.from_array(perfait["Array"]), gg.FigureTick(perfait["Tick"]["Dtick"], perfait["Tick"]["Format"])))
    figure = pivotgraph.to_figure()
    figure.LayoutTitleText = perfait["LayoutTitleText"]
    figure.XTitleText = perfait["XTitleText"]
    figure.YTitleText = perfait["YTitleText"]
    figure.Write(imageFilePath)
    print(Status(imageFilePath, "done"))
Task.set(ImageWriteTask("<perfait file path> <image file path>"))

Task.parse_if_main(__name__, Task.get("help"))
def main():
  pass
