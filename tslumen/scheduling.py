"""Provides options for the scheduling of tasks and computation."""
from typing import Optional, Union, Callable, Any, Sequence
from dataclasses import dataclass, asdict

from joblib import Parallel, delayed
from tqdm.auto import tqdm


__all__ = ["TqdmParallel", "Scheduler"]


class TqdmParallel(Parallel):  # type: ignore
    """For using ``tqdm`` with ``joblib``'s ``Parallel``"""

    def __init__(self, *args: Any, progress_disable: bool = True, **kwargs: Any) -> None:
        self.progress_disable = progress_disable
        super().__init__(*args, **kwargs)

    def __call__(
        self, *args: Any, total: Optional[int] = None, desc: str = "", **kwargs: Any
    ) -> Any:
        with tqdm(disable=self.progress_disable, total=total, desc=desc) as self._pbar:
            return Parallel.__call__(self, *args, **kwargs)

    def print_progress(self) -> None:
        self._pbar.total = self.n_dispatched_tasks
        self._pbar.n = self.n_completed_tasks
        self._pbar.refresh()


class Scheduler:
    """Wrapper around ``joblib``'s ``Parallel`` + ``delayed`` to integrate with ``Hydra``'s config
    and offer some syntactic sugar to the execution."""

    @dataclass
    class Config:
        """A ``dataclass`` representing ``joblib``'s ``Parallel`` default parameters."""

        n_jobs: Optional[int] = -2
        prefer: Optional[str] = "processes"
        verbose: int = 0
        timeout: Optional[float] = None
        backend: Optional[str] = None
        pre_dispatch: Any = "2 * n_jobs"
        batch_size: Any = "auto"
        temp_folder: Optional[str] = None
        max_nbytes: Optional[Any] = "1M"
        mmap_mode: Optional[str] = "r"
        require: Optional[str] = None
        progress_disable: bool = False

    def __init__(self, config: Optional[Union[Config, dict]] = None):
        if not config:
            self.config = asdict(self.Config())
        elif isinstance(config, self.Config):
            self.config = asdict(config)
        else:
            self.config = config
        self.parallel = TqdmParallel(**self.config)

    def run(self, fn: Callable, args: Sequence[tuple], desc: str = "") -> list:
        """Runs a single function with multiple args

        Args:
            fn (Callable): Function to be executed in parallel.
            args (Sequence[tuple]): A sequence of sets of arguments to pass on to ``fn``.
            desc (str): A description to accompany the progress bar.

        Returns:
            list: A list with the return values of each function.
        """
        results: list = self.parallel(
            (delayed(fn)(*arg) for arg in args), total=len(args), desc=desc
        )
        return results
