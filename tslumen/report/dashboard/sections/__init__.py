"""Package with all sections and blocks."""
from tslumen.report.dashboard.sections.summary import (
    SectionSummary,
    BlockPreview,
    BlockStats,
    BlockStatus,
)
from tslumen.report.dashboard.sections.timeseries import (
    SectionTimeSeries,
    BlockTSSelect,
    BlockTSAutoCorrelation,
    BlockTSComponents,
    BlockTSDetails,
    BlockTSDist,
    BlockTSLagPlots,
    BlockTSPlot,
    BlockTSSeasonality,
    BlockTSSmoothing,
    BlockTSStats,
)
from tslumen.report.dashboard.sections.features import (
    SectionFeatures,
    BlockTSFTSelect,
    BlockTSFeaturesHeatmap,
    BlockTSFeaturesRadar,
)
from tslumen.report.dashboard.sections.relations import (
    SectionRelations,
    BlockTSRelSelect,
    BlockTSCorrelations,
    BlockTSGranger,
)
