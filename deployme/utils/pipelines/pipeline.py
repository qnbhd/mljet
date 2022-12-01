"""Module that contains the Pipeline implementation."""

import copy
import logging
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    NoReturn,
    Optional,
)

import joblib

from deployme.utils.pipelines.dag import DirectedAcyclicGraph
from deployme.utils.pipelines.stage import Stage
from deployme.utils.utils import drop_unnecessary_kwargs

log = logging.getLogger(__name__)


@dataclass
class Context:
    """Context for pipeline."""

    _parameters: Dict[str, Any]
    _stages_results: Dict[str, Any]

    def __init__(
        self,
        parameters: Optional[Dict[str, Any]] = None,
        stages_results: Optional[Dict[str, Any]] = None,
    ):
        self._parameters = parameters or {}
        self._stages_results = stages_results or {}

    def set(self, key: str, value: Any):
        """Set parameter."""
        self._parameters[key] = value

    def get(self, key: str) -> Any:
        """Get parameter."""
        return self._parameters[key]

    def set_result(self, key: str, value: Any):
        """Set result."""
        self._stages_results[key] = value

    def get_result(self, key: str) -> Any:
        """Get result."""
        return self._stages_results[key]

    def __repr__(self):
        return f"Context(parameters={self._parameters}, stages_results={self._stages_results})"


class FrozenContext(Context):
    """Frozen context for pipeline."""

    def set(self, key: str, value: Any) -> NoReturn:
        raise RuntimeError("Cannot set parameter in frozen context.")

    def set_result(self, key: str, value: Any) -> NoReturn:
        raise RuntimeError("Cannot set result in frozen context.")

    @classmethod
    def from_context(cls, context: Context):
        return cls(
            copy.deepcopy(context._parameters),
            copy.deepcopy(context._stages_results),
        )

    def __repr__(self):
        return f"FrozenContext(parameters={self._parameters}, stages_results={self._stages_results})"


RunResult = Dict[str, Any]

RuntimeCheckAbleStage = Any


class IncorrectDependsError(Exception):
    """Incorrect `depends_on` error."""


class Pipeline:
    """
    Stages pipeline.
    Run stages with resolved order.
    """

    def __init__(self, context: Context):
        self._dag: DirectedAcyclicGraph[str] = DirectedAcyclicGraph()
        self._context = context
        self._name2stage: Dict[str, Stage] = {}

    def add(self, stage: RuntimeCheckAbleStage):
        """Add stage to pipeline.

        Args:
            stage: stage to add

        Raises:
            ValueError: if passed parameter has not `Stage` trait.
        """

        if not isinstance(stage, Stage):
            raise TypeError("Stage parameter must be instance of `Stage`")

        self._dag.add(stage.name)

        for early in stage.depends_on:
            self._dag.add(early, stage.name)

        self._name2stage[stage.name] = stage

    def get_actual_params(self, fun):
        """
        Get actual parameters for stage.
        If stage needs some parameters from context,
        need to add `ctx` parameter to stage function.
        """

        # noinspection PyProtectedMember
        pars = drop_unnecessary_kwargs(
            fun,
            {
                "ctx": FrozenContext.from_context(self._context),
                **self._context._parameters,
            },
        )

        return pars

    def __call__(self, allow_isolated_concurrency: bool = False) -> RunResult:
        """
        Run stages in pipeline.

        Args:
            allow_isolated_concurrency: allow concurrent execution
                of stages that are not depends on each other.

        """

        for j in filter(lambda x: x not in self._name2stage, self._dag.ordered):
            edges_to = self._dag.edges_from(j)
            edges_joined = ", ".join(edges_to)
            raise IncorrectDependsError(
                f"Stages `{edges_joined}` depends on `{j}`, "
                f"but `{j}` is not in pipeline."
            )

        # take isolated stages
        isolated = [self._name2stage[x] for x in self._dag.isolated]

        # take the rest stages
        jobs = [self._name2stage[x] for x in self._dag.ordered]

        # if allow isolated concurrency
        # run isolated stages in parallel
        if allow_isolated_concurrency:

            log.info(f"Running {[x.name for x in isolated]} in parallel")

            # create joblib tasks and parallel
            delayed = (joblib.delayed(item) for item in isolated)
            parallel = joblib.Parallel(n_jobs=-1)

            # run tasks
            run_results = parallel(
                stage_delayed(**self.get_actual_params(stage))
                for stage, stage_delayed in zip(isolated, delayed)
            )

            # update context and remove from jobs
            for stage, result in zip(isolated, run_results):
                self._context.set_result(stage.name, result)
                jobs.remove(stage)

        # run sequential stages
        for stage in jobs:
            log.info("Running stage `%s`" % stage.name)
            result = stage(**self.get_actual_params(stage))
            self._context.set_result(stage.name, result)

        # noinspection PyProtectedMember
        return copy.deepcopy(self._context._stages_results)  # noqa: W0212
