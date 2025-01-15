# -*- coding: utf-8 -*-
"""Collection of helper functions."""
from types import ModuleType
from typing import Optional, Union
import os
import sys

import numpy as np

import ray
from ray import tune
from ray.util.placement_group import placement_group, remove_placement_group, PlacementGroup
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy


def get_output_dir(run_config: ModuleType, array: bool = False, array_index: int = 0) -> str:
    """Builds the string to be used as the name of the output directory.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported `run-config`-file.
    array : bool
        Is the optimization executed using an array job? (Default value = False)
    array_index : int
        If the optimization is running as an array job, the ``array_index`` is needed to prevent file access conflicts. (Default value = 0)

    Returns
    -------
    str
        Path to the output directory.
    """
    if run_config.use_exact_name:
        output_folder = run_config.output_name
    else:
        output_folder = (
            "OPTIMA"
            + ("_varOpt" if run_config.perform_variable_opt else "")
            + (
                (
                    "+optuna+ASHA"
                    if run_config.perform_main_hyperopt and run_config.perform_variable_opt
                    else "_optuna+ASHA"
                )
                if run_config.perform_main_hyperopt
                else ""
            )
            + (
                (
                    "+PBT"
                    if run_config.perform_PBT_hyperopt
                    and (run_config.perform_variable_opt or run_config.perform_main_hyperopt)
                    else "_PBT"
                )
                if run_config.perform_PBT_hyperopt
                else ""
            )
            + (("_" + run_config.output_name) if run_config.output_name != "" else "")
        )

    output_path = os.path.join(run_config.output_path, output_folder)
    if array:
        output_path = os.path.join(output_path, str(array_index))
    return output_path


def check_optimization_finished(
    results_grid: tune.ResultGrid, target_num_samples: int, success_string: str, failure_string: str
) -> None:
    """Checks if the requested number of trials ran and terminated, i.e. the experiment finished successfully.

    Depending on the success of the experiment, one of two strings is printed. If the experiment did not finish successfully,
    the program is terminated with exit code ``1``.

    Parameters
    ----------
    results_grid : tune.ResultGrid
        The ``ResultGrid`` returned by the ``Tuner``.
    target_num_samples : int
        The number of trials that were to be run.
    success_string : str
        The string to print if the experiment was successful.
    failure_string : str
        The string to print if the experiment was not successful.
    """
    # make sure all trails ran and finished successfully
    finished_successfully = (len(results_grid) == target_num_samples) and (
        results_grid.num_terminated == target_num_samples
    )

    if finished_successfully:
        print(success_string)
    else:
        print(failure_string)
        sys.exit(1)


def get_max_seeds() -> tuple[int]:
    """Helper function to check if 32- or 64-bit integers are used by numpy and return a corresponding range of seed values.

    Returns
    -------
    tuple[int]
        Tuple containing the minimal and maximal seed value to use.
    """
    if np.int_ == np.int32:
        max_seeds = (-2147483648, 2147483648)
    else:
        max_seeds = (0, 4294967295)
    return max_seeds


def get_placement_group(
    cluster_cpus: int, cluster_gpus: int, cpus_per_bundle: Optional[int] = None, gpus_per_bundle: Optional[int] = None
) -> PlacementGroup:
    """Helper function to generate a ray placement group for the provided resources.

    At least one of ``cpus_per_bundle`` and ``gpus_per_bundle`` must not be ``None``.

    Parameters
    ----------
    cluster_cpus : int
        The number of cpus to reserve for the placement group.
    cluster_gpus : int
        The number of gpus to reserve for the placement group.
    cpus_per_bundle : Optional[int]
        The number of cpus to reserve for each bundle in the placement group. (Default value = None)
    gpus_per_bundle : Optional[int]
        The number of cpus to reserve for each bundle in the placement group. (Default value = None)

    Returns
    -------
    PlacementGroup
        A ray placement group for the provided resources.
    """
    assert (
        cpus_per_bundle is not None or gpus_per_bundle is not None
    ), "At least one of cpus_per_bundle and gpus_per_bundle must be provided."
    if cpus_per_bundle is not None and gpus_per_bundle is None:
        assert cpus_per_bundle > 0, "CPUs per bundle must be larger than 0."
    elif gpus_per_bundle is not None and cpus_per_bundle is None:
        assert gpus_per_bundle > 0, "GPUs per bundle must be larger than 0."
    else:
        assert (
            cpus_per_bundle > 0 or gpus_per_bundle > 0
        ), "At least one of CPUs per bundle and GPUs per bundle must be larger than 0."

    # calculate the maximum number of bundles possible
    bundles = int(
        min(
            cluster_cpus // cpus_per_bundle if cpus_per_bundle > 0 else np.inf,
            cluster_gpus // gpus_per_bundle if gpus_per_bundle > 0 else np.inf,
        )
    )

    # reserve the placement group
    bundle_resources = {}
    if cpus_per_bundle > 0:
        bundle_resources.update({"CPU": cpus_per_bundle})
    if gpus_per_bundle > 0:
        bundle_resources.update({"GPU": gpus_per_bundle})
    pg_resources = [bundle_resources for _ in range(bundles)]
    return placement_group(pg_resources)


def free_placement_group(placement_group: PlacementGroup) -> None:
    """A helper function to remove a placement group.

    Parameters
    ----------
    placement_group : PlacementGroup
        The placement group to remove
    """
    remove_placement_group(placement_group)


def apply_placement_group_strategy(
    placement_group: Optional[PlacementGroup] = None,
    task: Optional[ray.remote_function.RemoteFunction] = None,
    actor: Optional[ray.actor.ActorClass] = None,
) -> Union[ray.remote_function.RemoteFunction, ray.actor.ActorClass]:
    """Helper function that applies a placement group to a provided ray task or actor.

    Either a ``task`` or an ``actor`` must be provided.

    Parameters
    ----------
    placement_group : Optional[PlacementGroup]
        The placement group to apply. If ``None``, the task or actor is returned unchanged. (Default value = None)
    task : Optional[ray.remote_function.RemoteFunction]
        A ray task to apply the placement group to. (Default value = None)
    actor : Optional[ray.actor.ActorClass]
        A ray actor to apply the placement group to. (Default value = None)

    Returns
    -------
    Union[ray.remote_function.RemoteFunction, ray.actor.ActorClass]
        The ray task or actor with the placement group applied.
    """
    assert (task is not None and actor is None) or (
        actor is not None and task is None
    ), "Either a remote function or an actor class must be provided."

    # apply the placement group strategy
    if placement_group is not None:
        if task is not None:
            return task.options(scheduling_strategy=PlacementGroupSchedulingStrategy(placement_group=placement_group))
        else:
            return actor.options(scheduling_strategy=PlacementGroupSchedulingStrategy(placement_group=placement_group))
    else:
        return task if task is not None else actor
