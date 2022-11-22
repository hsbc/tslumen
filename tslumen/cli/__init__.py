"""CLI for tslumen."""
from typing import List, Any, Optional
import warnings
from dataclasses import dataclass, field

import yaml
import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import MISSING, OmegaConf

from tslumen.scheduling import Scheduler
from tslumen.cli.readers import Reader, ReaderCsv, ReaderFwf, ReaderExcel
from tslumen.profile import DefaultProfiler
from tslumen.report import HtmlReport

warnings.filterwarnings("ignore", module="omegaconf")


__all__ = ["CLIConfig", "cs", "main"]


@dataclass
class CLIConfig:
    """Configurations for the CLI."""

    defaults: List[Any] = field(default_factory=lambda: [{"reader": "csv"}, "_self_"])
    hydra: Any = field(
        default_factory=lambda: {
            "help": {"app_name": "tslumen"},
            "run": {"dir": "./out-tslumen/${now:%Y-%m-%d_%H-%M-%S}"},
            "job": {"name": "tslumen", "chdir": False},
        }
    )
    input: str = MISSING
    output: Optional[str] = None
    reader: Reader = MISSING
    profiler: Any = field(default_factory=lambda: DefaultProfiler.get_config_defaults(False))
    scheduler: Scheduler.Config = Scheduler.Config()


cs = ConfigStore.instance()
cs.store(group="reader", name="csv", node=ReaderCsv)
cs.store(group="reader", name="excel", node=ReaderExcel)
cs.store(group="reader", name="fwf", node=ReaderFwf)
cs.store(name="config", node=CLIConfig)


@hydra.main(config_name="config", config_path=None, version_base="1.1")
def main(cfg: CLIConfig) -> None:
    """CLI entrypoint, takes in all the configurations, instantiates a scheduler, reads the input
    data into a DataFrame using the supplied `Reader`, profiles the data using the
    `DefaultProfiler`, the results of which are supplied to `HtmlReport` and then write the HTML to
    the output file or stream.

    Args:
         cfg (CLIConfig): CLI configurations.
    """
    scheduler = Scheduler(cfg.scheduler)
    cfg.input = hydra.utils.to_absolute_path(cfg.input)
    cfg.reader.path = cfg.input
    reader = hydra.utils.instantiate(cfg.reader)
    df = reader.read()
    # solves pickling and improves speed
    pcfg = yaml.load(OmegaConf.to_yaml(cfg.profiler), Loader=yaml.FullLoader)
    profiler = DefaultProfiler(config=pcfg, scheduler=scheduler)
    report = HtmlReport(df=df, meta={}, profiler=profiler, scheduler=scheduler)
    if cfg.output:
        report.save(hydra.utils.to_absolute_path(cfg.output), mode="w", encoding="utf-8")
    else:
        print(report.save())


if __name__ == "__main__":
    main()
