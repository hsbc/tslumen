"""Interactive plots using `ploly`. Require extra dependencies to be installed."""
from tslumen.plot.interactive.line import TS, TSStack
from tslumen.plot.interactive.distribution import Histogram, SampleTheoretical, BoxPlot
from tslumen.plot.interactive.correlation import (
    LagCorrelation,
    LagMatrix,
    ScatterMatrix,
)
from tslumen.plot.interactive.comparison import Radar, Heatmap
from tslumen.plot.interactive.misc import GrangerMatrix
