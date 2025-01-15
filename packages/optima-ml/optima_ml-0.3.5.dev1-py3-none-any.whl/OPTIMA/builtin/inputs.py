# -*- coding: utf-8 -*-
"""Collection of classes and functions to handle data loading and preprocessing for classification tasks."""
from types import ModuleType
from typing import Union, Optional, Callable, Any, Literal
from typing_extensions import Self

import copy
import os
import pickle
import sys

import numpy as np
import pandas as pd
import sklearn.preprocessing
from matplotlib import pyplot as plt

import ray


class InputHandler:
    """Helper class to handle the currently used input variables and corresponding non-linear scalings."""

    def __init__(self, run_config: ModuleType) -> None:
        """Constructor of ``InputHandler``.

        Grabs the available input variables and corresponding non-linear transformations from the ``run_config``. If
        the list of input variables is not specified in ``run_config.input_vars``, ``get_vars()`` will return ``None``.
        The same is true for the non-linear input scaling expected in ``run_config.input_scaling``. If variables are set
        via ``set_vars`` and no input scaling is available for a variable, the scaling will be set to the identity.

        Parameters
        ----------
        run_config : ModuleType
            Reference to the imported ``run_config`` file.
        """
        self.run_config = run_config

        # get the list of variables to use; if they are not available, set to None and use all variables later
        if hasattr(run_config, "input_vars"):
            self.vars_in_use = run_config.input_vars
            self.as_indices = False
        else:
            self.vars_in_use = None
            self.as_indices = True

        # do the same for the dictionary of non-linear scalings, but also check if any variable in self.vars_in_use does
        # not have an entry in run_config.input_scaling
        if hasattr(run_config, "input_scaling"):
            self.scaling_dict = run_config.input_scaling
            if self.vars_in_use is not None:
                for var in self.vars_in_use:
                    if var not in self.scaling_dict.keys():
                        self.scaling_dict[var] = ("linear", (1.0, 0.0))
        else:
            if self.vars_in_use is not None:
                self.scaling_dict = {var: ("linear", (1.0, 0.0)) for var in self.vars_in_use}
            else:
                self.scaling_dict = None

    def set_vars(self, input_vars: list[Union[str, tuple[int]]], as_indices: Optional[bool] = False) -> None:
        """Update the currently used input variables and the scaling dictionary.

        Parameters
        ----------
        input_vars : list[Union[str, tuple[int]]]
            List containing the names of the input variables to use.
        as_indices : Optional[bool]
            Indicates if ``input_vars`` contains a list of variable names or a list of tuples of indices. (Default value = False)
        """
        # if the inputs are given as a list of indices, generate labels of type '2_3_1' for index (2, 3, 1)
        self.as_indices = as_indices
        if not as_indices:
            self.vars_in_use = input_vars
        else:
            self.vars_in_use = ["_".join([str(index) for index in indices]) for indices in input_vars]

        # if no non-linear scalings are given, use identity instead
        if hasattr(self.run_config, "input_scaling"):
            self.scaling_dict = {}
            for var in self.vars_in_use:
                if self.run_config.input_scaling.get(var) is None:
                    self.scaling_dict[var] = ("linear", (1.0, 0.0))
                else:
                    self.scaling_dict[var] = self.run_config.input_scaling[var]
        else:
            self.scaling_dict = {var: ("linear", (1.0, 0.0)) for var in self.vars_in_use}

    def get_vars(self, as_indices: Optional[bool] = False) -> Optional[Union[list[str], list[tuple[int]]]]:
        """Get the list of currently used input variables.

        Parameters
        ----------
        as_indices : Optional[bool]
            If True, returns the input variables as indices instead of strings. This only works if the input variables
            have originally been provided as indices. (Default value = False)

        Returns
        -------
        Optional[Union[list[str], list[tuple[int]]]]
            _description_
        """
        # if the variables were provided as indices, we extract them again from the corresponding labels
        if (not as_indices) or self.vars_in_use is None:
            return self.vars_in_use
        else:
            return [tuple(int(index) for index in indices_str.split("_")) for indices_str in self.vars_in_use]

    def get_nonlinear_scaling(self) -> dict[str, tuple[str, tuple[float, float]]]:
        """Get the dictionary containing the non-linear transformation (as a callable) to apply to all input variables in use.

        Returns
        -------
        dict[str : dict[str, tuple[str, tuple[float, float]]]
            Dictionary of non-linear transformations for the input variables in use.
        """
        return self.scaling_dict

    def copy(self) -> "InputHandler":
        """Performs a shallow copy of the ``InputHandler``.

        Returns
        -------
        "InputHandler"
            New ``InputHandler`` instance with the same state.
        """
        new_input_handler = InputHandler(self.run_config)
        new_input_handler.set_vars(copy.deepcopy(self.vars_in_use))
        return new_input_handler


class DummyScaler:
    """Dummy scaler used when the input variables don't need scaling."""

    def __init__(self) -> None:
        """Constructor of DummyScaler."""
        pass

    def fit(self, x: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> Self:
        """`Placeholder`.

        Parameters
        ----------
        x : np.ndarray
            `Unused`.
        sample_weight : Optional[np.ndarray]
            `Unused`. (Default value = None)

        Returns
        -------
        Self
            Returns itself.
        """
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        """`Placeholder`.

        Parameters
        ----------
        x : np.ndarray
            `Unused`.

        Returns
        -------
        np.ndarray
            Returns the inputs unchanged.
        """
        return x


class ManualScaler:
    """Scaler that applies the manually chosen, non-linear transformations saved in the InputHander."""

    def __init__(self, input_handler: InputHandler) -> None:
        """Constructor of ``ManualScaler``. Needs a reference to an ``InputHandler`` instance to get the non-linear transformations.

        Parameters
        ----------
        input_handler : InputHandler
            Reference to an instance of ``InputHandler``.
        """
        self.input_handler = input_handler
        scaling_dict = input_handler.get_nonlinear_scaling()

        self.non_linear_ops = []
        for var in input_handler.get_vars():
            scaling = scaling_dict.get(var)
            if scaling is not None and scaling[0] == "sqrt":
                self.non_linear_ops.append((np.sqrt, scaling[1][0], scaling[1][1]))
            elif scaling is not None and scaling[0] == "log10":
                self.non_linear_ops.append((np.log10, scaling[1][0], scaling[1][1]))
            elif scaling is not None and scaling[0] == "linear":
                self.non_linear_ops.append((lambda x: x, scaling[1][0], scaling[1][1]))
            elif scaling is None:
                self.non_linear_ops.append((lambda x: x, 1.0, 0.0))
            else:
                raise ValueError(f"Unknown scaling type {scaling}.")

    def fit(self, input_data: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> Self:
        """Placeholder function.

        This function is provided to be consistent with the other scalers, although fitting to data is not required.

        Parameters
        ----------
        input_data : np.ndarray
            `Unused`.
        sample_weight : Optional[np.ndarray]
            `Unused`. (Default value = None)

        Returns
        -------
        Self
            Returns itself
        """
        return self

    def transform(self, input_data: np.ndarray) -> np.ndarray:
        """Transform a given input according to the non-linear transformations given in the ``InputHandler``.

        Parameters
        ----------
        input_data : np.ndarray
            The data to be transformed.

        Returns
        -------
        np.ndarray
            The transformed data.
        """
        vars_in_use = self.input_handler.get_vars()

        transformed_inputs = np.empty_like(input_data)
        for i in range(len(vars_in_use)):
            transformation, scale, offset = self.non_linear_ops[i]
            transformed_inputs[:, i] = transformation(scale * input_data[:, i] + offset)
        return transformed_inputs


class ManualPlusPowerTransformer(sklearn.preprocessing.PowerTransformer):
    """Extends `sklearn`'s ``PowerTransformer`` by the manual non-linear transformations specified in the ``run_config``.

    Before giving the inputs to the ``PowerTransformer``, the non-linear transformations given in the ``InputHandler`` are
    applied.
    """

    def __init__(self, input_handler: InputHandler, method: str = "yeo-johnson", *, standardize: bool = True) -> None:
        """Constructor of ``ManualPlusPowerTransformer``.

        Parameters
        ----------
        input_handler : InputHandler
            Reference to an ``InputHandler`` instance.
        method : str
            The power transform method. Parameter of `sklearn`'s ``PowerTransformer``. (Default value = "yeo-johnson")
        standardize : bool
            Set to ``True`` to apply zero-mean, unit-variance normalization to the transformed output. Parameter of
            `sklearn`'s PowerTransformer. (Default value = True)
        """
        self.manual_scaler = ManualScaler(input_handler)
        super(ManualPlusPowerTransformer, self).__init__(method, standardize=standardize, copy=False)

    def fit(self, X: np.ndarray, y: Any = None) -> Self:
        """Estimate the optimal parameters of the ``PowerTransformer``.

        The ``PowerTransformer`` is fitted to the transformed inputs, i.e. the non-linear transformations given in the
        ``InputHandler`` are applied to the inputs before giving them to the ``PowerTransformer``'s ``fit``-function.

        Parameters
        ----------
        X : np.ndarray
            The data used to estimate the optimal transformation parameters.
        y : Any
            Parameter of the ``fit``-function of the ``PowerTransformer``. (Default value = None)

        Returns
        -------
        Self
            Returns itself with the ``PowerTransformer``-parameters fitted to the input data.
        """
        X_manually_scaled = self.manual_scaler.transform(X)
        return super(ManualPlusPowerTransformer, self).fit(X_manually_scaled, y=y)

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transforms the given input data.

        Firstly, the manual transformations given in the ``InputHandler`` instance are applied, afterwards the inputs are
        scaled by the ``PowerTransformer``. The transformed inputs are returned. Before transforming, the scaler needs to be
        fitted to data by calling the ``fit``-function.

        Parameters
        ----------
        X : np.ndarray
            The data to be transformed.

        Returns
        -------
        np.ndarray
            The transformed data.
        """
        X_manually_scaled = self.manual_scaler.transform(X)
        X_scaled = super(ManualPlusPowerTransformer, self).transform(X_manually_scaled)
        return X_scaled

    def inverse_transform(self, X: np.ndarray) -> None:
        """`Not implemented`.

        Parameters
        ----------
        X : np.ndarray
            The transformed data.
        """
        raise NotImplementedError


class ManualPlusStandardScaler(sklearn.preprocessing.StandardScaler):
    """Extends `sklearn`'s ``StandardScaler`` by the manual non-linear transformations specified in the ``run_config``.

    Before giving the inputs to the ``StandardScaler``, the non-linear transformations given in the ``InputHandler`` are
    applied.
    """

    def __init__(self, input_handler: InputHandler) -> None:
        """Constructor of the ``ManualPlusStandardScaler``.

        Parameters
        ----------
        input_handler : InputHandler
            Reference to an ``InputHandler`` instance.
        """
        self.input_handler = input_handler
        self.manual_scaler = ManualScaler(input_handler)
        super(ManualPlusStandardScaler, self).__init__(copy=False)

    def fit(self, X: np.ndarray, y: Any = None) -> Self:
        """Applies the manual non-linear transformations, then fits the ``StandardScaler`` on the transformed input.

        Parameters
        ----------
        X : np.ndarray
            The data used to estimate the optimal transformation parameters.
        y : Any
            Parameter of the ``StandardScaler``'s fit function. (Default value = None)

        Returns
        -------
        Self
            Returns itself, with the parameters of the ``StandardScaler`` fitted to the input data.
        """
        X_manually_scaled = self.manual_scaler.transform(X)
        return super(ManualPlusStandardScaler, self).fit(X_manually_scaled, y=y)

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transforms a given input by first applying the manual, non-linear and then the ``StandardScaler``'s linear transformations.

        The non-linear transformation is given by the transformations specified in the provided ``InputHandler`` instance.
        The transformed data is returned. Before transforming, the scaler needs to be fitted to data by calling the
        ``fit``-function.

        Parameters
        ----------
        X : np.ndarray
            The data to be transformed.

        Returns
        -------
        np.ndarray
            The transformed data.
        """
        X_manually_scaled = self.manual_scaler.transform(X)
        X_scaled = super(ManualPlusStandardScaler, self).transform(X_manually_scaled)
        return X_scaled

    def inverse_transform(self, X: np.ndarray) -> None:
        """`Not implemented`.

        Parameters
        ----------
        X : np.ndarray
            The transformed data.
        """
        raise NotImplementedError


class CustomManualPlusStandardScaler:
    """Simpler version of the ``ManualPlusStandardScaler`` without the `sklearn` dependency when saving.

    In case the scaler shall be used in an environment with a different `sklearn` version (e.g. in the CAF environment),
    the scaler cannot be a subclass of an `sklearn` scaler. Thus, provide crude version of a Manual+Linear scaler for
    these cases and only import the ``StandardScaler`` during the fit for the mean and scale calculation.
    """

    def __init__(self, input_handler: InputHandler) -> None:
        """The constructor of ``CustomManualPlusStandardScaler``.

        Parameters
        ----------
        input_handler : InputHandler
            Reference to an ``InputHandler`` instance.
        """
        self.input_handler = input_handler
        self.manual_scaler = ManualScaler(input_handler)
        self.mean_ = None
        self.scale_ = None

    def fit(self, X: np.ndarray, sample_weight: Optional[np.ndarray] = None, y: Any = None) -> Self:
        """Fit the parameters of the linear transformation to the given input data.

        First, the manually specified non-linear transformations given in the ``InputHandler`` are applied. Afterwards,
        `sklearn`'s ``StandardScaler`` is imported and fitted to the transformed data. The scale and offset parameters
        (``mean_`` and ``scale_``) are extracted and saved. An instance of the ``CustomManualPlusStandardScaler``-class is
        returned with the adjusted parameters.

        Parameters
        ----------
        X : np.ndarray
            The data used to estimate the optimal transformation parameters.
        sample_weight : Optional[np.ndarray]
            Weight of each individual sample in ``X``. Parameter of the ``StandardScaler``'s ``fit``-function. (Default value = None)
        y : Any
            Parameter of the ``StandardScaler``'s ``fit``-function. (Default value = None)

        Returns
        -------
        Self
            Returns itself, with the transformation parameters adjusted.
        """
        X_manually_scaled = self.manual_scaler.transform(X)

        from sklearn.preprocessing import StandardScaler

        standard_scaler = StandardScaler()
        standard_scaler.fit(X_manually_scaled, sample_weight=sample_weight, y=y)

        self.mean_ = standard_scaler.mean_
        self.scale_ = standard_scaler.scale_

        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transforms a given input by first applying the manual, non-linear and then a linear transformation.

        The non-linear transformation is given by the transformations specified in the provided ``InputHandler`` instance.
        The linear transformation is calculated according to ``x_scaled = (x - mean_) / scale_``. The transformed inputs
        are returned. Before transforming, the scaler needs to be fitted to data by calling the ``fit``-function.

        Parameters
        ----------
        X : np.ndarray
            The data to transform.

        Returns
        -------
        np.ndarray
            The transformed data.
        """
        assert (
            self.mean_ is not None and self.scale_ is not None
        ), "The scaler needs to be fitted to data first before applying the transformation!"

        X_manually_scaled = self.manual_scaler.transform(X)
        X_scaled = (X_manually_scaled - self.mean_) / self.scale_

        return X_scaled

    def save(self, path: str) -> None:
        """Saves the parameters of the linear transformation to a pickle-file.

        Parameters
        ----------
        path : str
            Path of the pickle-file.
        """
        with open(path, "wb") as f:
            pickle.dump((self.mean_, self.scale_), f)

    def load(self, path: str) -> None:
        """Loads the parameters of the linear transformation from a pickle-file.

        Parameters
        ----------
        path : str
            Path of the pickle-file.
        """
        with open(path, "rb") as f:
            self.mean_, self.scale_ = pickle.load(f)


def get_inputs(
    run_config: ModuleType,
    nevts: Union[int, float, Literal[np.inf], list[int]],
    input_vars_list: Optional[list[Union[str, tuple[int]]]] = None,
    disable_printing: bool = False,
) -> ray.data.Dataset:
    """From a given pickle-file, the input data is loaded and the event weights of all classes are normalized.

    The path of the pickle-file is taken from the ``run_config``. The pickle-file is expected to contain a pandas dataframe
    concatenated from two dataframes with keys ``'features'`` and ``'targets'`` containing the event information and
    corresponding class label, respectively. The features-dataframe must contain the columns ``'Weight'`` and
    ``'EventNumber'`` assigning each event a weight and a number. The remaining columns are interpreted as input variables.
    The targets-dataset is assumed to have the shape ``(Nevents, Nclasses)``, with ``Nevents`` the total number of events.

    The number of events read from the pickle-file is controlled by the ``nevts``-parameter. It can either be specified
    as a list of Nclasses elements (thus explicitly specifying the number of events to load per class), as a single
    number (resulting in an equal split between the classes, when possible), or be set to ``np.inf`` to load the full
    available dataset.

    The event weights are reweighted to give the same total weight (sum over all weights) for all classes. If the
    ``max_event_weight``-parameter is set in the ``run_config``, an event duplication are performed where events with
    weight larger than ``max_event_weight`` times the median weight are duplicated and the corresponding weight is halved.
    This is repeated until all event weights are small enough. Finally, all event weights are normalized to reach an
    average weight (over all classes) of one.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported ``run_config``.
    nevts : Union[int, float, Literal[np.inf], list[int]]
        Parameter controlling the number of events loaded from the pickle-file input file whose path is specified in the
        ``run_config``.
    input_vars_list : Optional[list[Union[str, tuple[int]]]]
        List of input variables to load from the input data. They are assumed to be present as columns in
        ``events_df["features"]``. If a value of ``None`` is given, all columns besides ``'Weight'``, ``'weight'`` and
        ``'EventNumber'`` will be used. (Default value = None)
    disable_printing : bool
        If ``True``, no messages are printed. (Default value = False)

    Returns
    -------
    ray.data.Dataset
        A ray dataset containing the input features as column ``Input``, the target labels as column ``Target``, the
        normalized event weight as column ``weight``, the un-normalized event weight as column ``ScaledWeight`` and the
        event numbers as column ``EventNumber``.
    """
    # load events from input file
    events_df = pd.read_pickle(run_config.inputs_file)
    features_df = events_df["features"]
    targets_df = events_df["targets"]
    del events_df

    # check if the input data is for binary or multiclass classification
    num_classes = targets_df.shape[1]
    if num_classes == 1:
        binary_classification = True
        num_classes = 2
    else:
        binary_classification = False

    # get available number of events for each class in case any of them are underrepresented in the input data
    avail_events = []
    if binary_classification:
        avail_events.append(targets_df[targets_df.iloc[:, 0] == 1].shape[0])
        avail_events.append(targets_df[targets_df.iloc[:, 0] == 0].shape[0])
    else:
        for i in range(num_classes):
            avail_events.append(targets_df[targets_df.iloc[:, i] == 1].shape[0])

    # sanity check
    if nevts == np.inf:
        target_events = [round(features_df.shape[0])] * num_classes
    else:
        if isinstance(nevts, int) or isinstance(nevts, float):
            requested_events = [round(nevts / num_classes)] * num_classes
        elif isinstance(nevts, list) or isinstance(nevts, tuple):
            assert (
                len(nevts) == num_classes
            ), f"nevents has to be int or list/tuple with the same length as the number of classes ({num_classes})!"
            requested_events = nevts
        else:
            raise TypeError

        # check if enough signal and background are available
        target_events = np.minimum(avail_events, requested_events)
        if not (target_events == requested_events).all():
            print(f"Not enough events to satisfy the request of {requested_events}, can only provide {target_events}.")

    # we need to shuffle the events and targets first in case they are ordered by process --> would introduce bias when
    # not using all events!
    features_df = features_df.sample(frac=1, random_state=4242)
    targets_df = targets_df.sample(frac=1, random_state=4242)

    # select the desired number of events for each class
    features_dfs_per_class = []
    targets_dfs_per_class = []
    if binary_classification:
        features_dfs_per_class.append(features_df[targets_df.iloc[:, 0] == 1][: target_events[0]])
        features_dfs_per_class.append(features_df[targets_df.iloc[:, 0] == 0][: target_events[1]])
        targets_dfs_per_class.append(targets_df[targets_df.iloc[:, 0] == 1][: target_events[0]])
        targets_dfs_per_class.append(targets_df[targets_df.iloc[:, 0] == 0][: target_events[1]])
    else:
        for i in range(num_classes):
            features_dfs_per_class.append(features_df[targets_df.iloc[:, i] == 1][: target_events[i]])
            targets_dfs_per_class.append(targets_df[targets_df.iloc[:, i] == 1][: target_events[i]])
    del targets_df

    # get the inputs
    features_df = pd.concat(features_dfs_per_class)
    if input_vars_list is None:
        inputs = features_df.drop(
            [col for col in ["Weight", "weight", "EventNumber"] if col in features_df.columns], axis=1
        ).to_numpy()
    else:
        inputs = features_df[input_vars_list].to_numpy()

    targets = pd.concat(targets_dfs_per_class).to_numpy()
    if "weight" in features_df.columns:
        weights = features_df["weight"].to_numpy()
    elif "Weight" in features_df.columns:
        weights = features_df["Weight"].to_numpy()
    else:
        raise KeyError(
            f'No weight found in the input features {list(features_df.columns)}. Valid keys for the weights are "Weight" and "weight"'
        )
    if "EventNumber" in features_df.columns:
        event_nums = features_df["EventNumber"].to_numpy()
    else:
        raise KeyError(f"No 'EventNumber' found in the input features {list(features_df.columns)}.")
    del features_df

    # examine input data
    if not disable_printing:
        print("input data features (number of events, number of features): {}".format(inputs.shape))
        print("Printing example inputs:")
        print(inputs[1:5])
        print("Input labels (number of events, number of features) ", targets.shape)
        print(targets[1:5])

    # get the total event weight for each class
    total_weights = []
    if binary_classification:
        total_weights.append(np.sum(weights[targets[:, 0] == 1]))
        total_weights.append(np.sum(weights[targets[:, 0] == 0]))
    else:
        for i in range(num_classes):
            total_weights.append(np.sum(weights[targets[:, i] == 1]))
    if not disable_printing:
        print(f"Total weights for each class: {total_weights}")

    # reweight to get the same total weight for all classes
    normalized_weights = weights.copy()
    if binary_classification:
        normalized_weights[targets[:, 0] == 1] /= total_weights[0]
        normalized_weights[targets[:, 0] == 0] /= total_weights[1]
    else:
        for i in range(num_classes):
            normalized_weights[targets[:, i] == 1] /= total_weights[i]

    # check for maximal event weight
    if not np.isinf(run_config.max_event_weight):
        # normalize the weights by the median
        normalized_weights /= np.median(normalized_weights)

        # for large event weights, duplicate corresponding event and reduce the event weight correspondingly
        while np.any(normalized_weights > run_config.max_event_weight):
            if not disable_printing:
                print(
                    f"{normalized_weights[normalized_weights > run_config.max_event_weight].shape[0]} events with normalized "
                    f"weight greater than {run_config.max_event_weight} found, duplicating..."
                )
            inputs = np.concatenate((inputs, inputs[normalized_weights > run_config.max_event_weight, :]))
            targets = np.concatenate((targets, targets[normalized_weights > run_config.max_event_weight, :]))
            weights = np.concatenate((weights, weights[normalized_weights > run_config.max_event_weight]))
            event_nums = np.concatenate((event_nums, event_nums[normalized_weights > run_config.max_event_weight]))
            normalized_weights = np.concatenate(
                (normalized_weights, normalized_weights[normalized_weights > run_config.max_event_weight])
            )
            weights[normalized_weights > run_config.max_event_weight] /= 2
            normalized_weights[normalized_weights > run_config.max_event_weight] /= 2

    # set the average weight to 1
    normalized_weights /= np.mean(normalized_weights)
    if not disable_printing:
        print("average weight after normalization: {}".format(np.mean(normalized_weights)))

    # shuffle all arrays in the same way to mix the classes again
    random_indices = np.arange(targets.shape[0])
    rng = np.random.RandomState(42)
    rng.shuffle(random_indices)
    targets = targets[random_indices]
    inputs = inputs[random_indices]
    weights = weights[random_indices]
    normalized_weights = normalized_weights[random_indices]
    event_nums = event_nums[random_indices]

    # combine into a ray dataset
    dataset = ray.data.from_items(
        [
            {
                "Input": inputs[i, :],
                "Target": targets[i, :],
                "Weight": normalized_weights[i],
                "ScaledWeight": weights[i],
                "EventNumber": event_nums[i],
            }
            for i in range(len(inputs))
        ]
    )

    return dataset


def plot_input_data(
    run_config: ModuleType, dataset: ray.data.Dataset, outdir: str, input_vars_list: Optional[list] = None
) -> None:
    """Plots the distribution of each target class for each input variable and saves them to ``outdir``.

    The dataset is expected to have columns ``Input`` and ``Target`` containing the input features and target labels,
    respectively.

    Optionally, if columns ``ScaledWeight`` or ``Weight`` are present, its values will be used as sample weights.
    If both columns are present, ``ScaledWeight`` is used.

    The ``input_vars_list`` is used for the filename of each plot. The order of input variables in ``input_vars_list``
    is expected to correspond to the order in the array of input features.

    Parameters
    ----------
    run_config : ModuleType
        A reference to the inported run-config file.
    dataset : ray.data.Dataset
        The dataset containing the input features and target labels. The input features are expected to be contained in
        a ``Input``-column where each row contains a 1D-array of the same length as the ``inputs_vars_list``. The target
        labels are expected to be contained in a ``Target``-column where each row contains a 1D-array with one-hot-encoded
        or binary-encoded class labels. If the dataset contains a ``Weight`` and/or ``ScaledWeight`` column containing
        float values, the corresponding enties are used to weight each row. If both columns are present, ``ScaledWeight``
        will be used.
    outdir : str
        Path of the output folder the plots will be saved into.
    input_vars_list : Optional[list]
        List of variable names. It must be in the same order as the input variables in the ``Input``-column in the
        dataset. If ``None``, the input variables are enumerated. (Default value = None)
    """
    # get the data to plot. This weird way to fetch the data from the dataset is needed due to a (probable?) bug in Ray
    # data. If any of the take...() functions is used, more Ray tasks are executed in parallel than allowed by the
    # Placement group for some reason. This does not occur when using iter_batches()
    inputs = list(dataset.select_columns(["Input"]).iter_batches(batch_size=dataset.count()))[0]["Input"]
    targets = list(dataset.select_columns(["Target"]).iter_batches(batch_size=dataset.count()))[0]["Target"]

    if "ScaledWeight" in dataset.columns():
        weights = list(dataset.select_columns(["ScaledWeight"]).iter_batches(batch_size=dataset.count()))[0][
            "ScaledWeight"
        ]
    elif "Weight" in dataset.columns():
        weights = list(dataset.select_columns(["Weight"]).iter_batches(batch_size=dataset.count()))[0]["Weight"]
    else:
        weights = None

    if input_vars_list is None:
        input_vars_list = [f"Input_{i}" for i in range(1, inputs.shape[1] + 1)]

    for i, var in enumerate(input_vars_list):
        vals_per_class = []
        if weights is not None:
            weights_per_class = []
        if targets.shape[1] == 1:
            vals_per_class.append(inputs[targets[:, 0] == 1, i])
            vals_per_class.append(inputs[targets[:, 0] == 0, i])
            if weights is not None:
                weights_per_class.append(weights[targets[:, 0] == 1])
                weights_per_class.append(weights[targets[:, 0] == 0])
        else:
            for j in range(targets.shape[1]):
                vals_per_class.append(inputs[targets[:, j] == 1, i])
                if weights is not None:
                    weights_per_class.append(weights[targets[:, j] == 1])

        fig, ax = plt.subplots(figsize=[8, 6], layout="constrained")
        if weights is not None:
            ax.hist(
                vals_per_class,
                bins=40,
                weights=weights_per_class,
                histtype="step",
                density=True,
                label=run_config.evaluation_class_labels,
            )
        else:
            ax.hist(
                vals_per_class,
                bins=40,
                histtype="step",
                density=True,
                label=run_config.evaluation_class_labels,
            )
        ax.set_xlabel(var)
        ax.legend()
        if not os.path.exists(outdir):
            os.makedirs(outdir, exist_ok=True)
        fig.savefig(os.path.join(outdir, "inputs_{}.pdf".format(var)))
        plt.close()


train_val_splitting_type = tuple[ray.data.Dataset, ray.data.Dataset]
train_val_test_splitting_type = tuple[ray.data.Dataset, ray.data.Dataset, ray.data.Dataset]
kfold_train_val_splitting_type = tuple[list[ray.data.Dataset], list[ray.data.Dataset]]
kfold_train_val_test_splitting_type = tuple[list[ray.data.Dataset], list[ray.data.Dataset], list[ray.data.Dataset]]


def get_training_data(
    dataset: ray.data.Dataset,
    splitting_cond: Union[tuple[Callable], tuple[float], list[Callable], list[float], Callable, float],
    do_kfold: bool = False,
    shuffle: bool = False,
    fixed_test_dataset: bool = True,
    disable_printing: bool = False,
) -> Union[
    train_val_splitting_type,
    train_val_test_splitting_type,
    kfold_train_val_splitting_type,
    kfold_train_val_test_splitting_type,
]:
    """Preprocesses and splits provided dataset into training, validation and testing datasets according to a splitting condition.

    The splitting condition can either be a float, a list or tuple of two floats, a callable or a list or tuple of two
    callables. The ``do_kfold``-parameter decides if the outputs for simple splitting or k-fold crossvalidation are
    returned.

    Since the kfold splitting (without event numbers) splits the dataset into splices without changing the order of the
    rows, the dataset can optionally be shuffled using the ``ray.data.Dataset.random_shuffle()``-function before the
    splitting by setting ``shuffle`` to ``True``. Keep in mind that this shuffling method can be slow.

    For ``float`` and ``Union[tuple[float, float], list[float, float]]``:

    - if ``do_kfold`` is ``False``:
        - ``float``: random split into training and validation using the ``ray.data.Dataset.train_test_split()``-function;
          the splitting condition controls the fraction of validation events.
        - ``Union[tuple[float, float], list[float, float]]``: random splits into training, validation and testing using
          the ``ray.data.Dataset.train_test_split()``-function; the first entry controls the fraction of testing events,
          the second entry the fraction of validation events.
    - if ``do_kfold`` is ``True``:
        - ``float``: the ``ray.data.Dataset.split()``-function is used to split the dataset into ``round(1 / splitting_cond)``
          splits, each of which is used once as the validation dataset. The remaining splits are combined into the
          corresponding training dataset of this fold using the ``ray.data.Dataset.union()``-function.
        - ``Union[tuple[float, float], list[float, float]]``: the behaviour depends on the value of ``fixed_test_dataset``:
            - if ``fixed_test_dataset`` is ``True``: the testing dataset is split from the full dataset using the
              ``ray.data.Dataset.train_test_split()``-function and kept constant for all folds; for the remaining
              training+validation dataset, the same procedure is used as for the ``float``-case.
            - if ``fixed_test_dataset`` is ``False``: the testing dataset is `not` kept constant and instead varied
              together with the validation dataset in a k-fold-like manner. Depending on the requested size of the
              validation and testing datasets, the dataset is split into ``N`` splits using the
              ``ray.data.Dataset.split()``-function. ``N`` is chosen so that the validation and testing sizes can be
              reached by combining a certain number of splits. E.g., if ``test_split=0.2`` and ``val_split=0.1`` are
              requested, ``N=10`` and the testing sets are build by combining two splits. For each fold, different
              splits are combined using the ``ray.data.Dataset.union()``-function to build the training, validation and
              testing sets. The total number of folds is given by the size of the testing dataset, i.e. in the example,
              five folds will be returned. As a result, while the concatenation of the testing datasets of all folds is
              guaranteed to reproduce the full dataset, for the validation datasets this is only true if ``val_split``
              = ``test_split``. Otherwise, the validation datasets may be overlapping (for ``val_split`` > ``test_split``)
              or may leave gaps (``val_split`` < ``test_split``). For ``val_split`` = ``test_split``, each sample is
              exactly once part of the validation and the testing datasets.

    For splitting conditions containing a callable, an ``EventNumber``-column must be present in the ``dataset``. The
    dataset is split according to:

    - ``callable``: ``splitting_cond``, when provided with the numpy array of event numbers, is expected to return an
      array (if ``do_kfold`` is ``False``) or a list of arrays (if ``do_kfold`` is ``True``) of the same shape as the
      provided event numbers, with values ``True`` for events that should be included in the validation dataset and
      ``False`` otherwise. A returned list of `k` arrays results in `k` pairs of training and validation datasets.
    - ``Union[tuple[Callable, Callable], list[Callable, Callable]]``: the return value of ``splitting_cond[0]``, when
      provided with the numpy array of event numbers, is used to split the full dataset into a testing and a
      training+validation set. The corresponding return value of ``splitting_cond[1]`` is used to split the
      training+validation set into a training and a validation set. As a result, both splitting conditions must either
      return an array (if ``do_kfold`` is ``False``) or a list of arrays (if ``do_kfold`` is ``True``). For each fold
      (when a list of arrays is returned), the `i`-th list entries from both lists is used to determine the splitting
      of the `i`-th fold.

    The return type of the split dataset differs if k-fold splitting was performed or not. If no k-fold was done, the
    training, validation and (if present) testing splits of the dataset are combined into a tuple. If k-fold splitting
    was done, the `k` training, validation and (if present) testing splits are each first combined into a list before
    combining them into a tuple. Thus, for k-fold, a tuple of 2 or 3 lists containing `k` ``ray.data.Datasets`` each are
    returned.

    Note: Ray does not ensure that the order of rows in the split datasets corresponds to the original order in the
    provided ``dataset``. If this order is critical, make sure to set
    ``ray.data.context.DatasetContext.get_current().execution_options.preserve_order`` to ``True`` before calling this
    function.

    Parameters
    ----------
    dataset : ray.data.Dataset
        The input dataset to split.
    splitting_cond : Union[tuple[Callable], tuple[float], list[Callable], list[float], Callable, float]
        Condition determining the splitting of inputs, targets, weights and normalized_weights into training, validation
        and (potentially) testing sets.
    do_kfold : bool
        If ``splitting_cond`` does not contain a callable, this controls if a simple splitting or k-fold splitting should be
        done. (Default value = False)
    shuffle : bool
        If ``True``, the provided dataset is shuffled before performing the splitting. (Default value = False)
    fixed_test_dataset : bool
        If ``True``, a fixed testing dataset will be used for all folds. If ``False``, the testing dataset will be shuffled in
        a k-fold-like manner. Only relevant if ``do_kfold`` is ``True``. (Default value = True)
    disable_printing : bool
        If ``True``, no output will be printed. (Default value = False)

    Returns
    -------
    Union[train_val_splitting_type,train_val_test_splitting_type,kfold_train_val_splitting_type,kfold_train_val_test_splitting_type,]
        Returns a tuples containing the training, validation and (potentially) testing datasets / lists of datasets.
    """
    if isinstance(splitting_cond, tuple) or isinstance(splitting_cond, list):
        use_testing_dataset = True
        splitting_cond_test, splitting_cond_val = splitting_cond
        if callable(splitting_cond_test) and callable(splitting_cond_val):
            assert (
                "EventNumber" in dataset.columns()
            ), "array of event numbers must be provided when using custom splitting condition"
            custom_splitting_condition = True
        elif isinstance(splitting_cond_test, float) and isinstance(splitting_cond_val, float):
            custom_splitting_condition = False
            test_split = splitting_cond_test
            val_split = splitting_cond_val
        else:
            if not disable_printing:
                print(
                    "Splitting condition must either be a float or a callable for both splitting_cond_test and "
                    "splitting_cond_val. Exiting..."
                )
            sys.exit(1)
    else:
        use_testing_dataset = False
        splitting_cond_val = splitting_cond
        if callable(splitting_cond):
            assert (
                "EventNumber" in dataset.columns()
            ), "array of event numbers must be provided when using custom splitting condition"
            custom_splitting_condition = True
        elif isinstance(splitting_cond, float):
            custom_splitting_condition = False
            val_split = splitting_cond_val
        else:
            if not disable_printing:
                print(
                    "Splitting condition must either be a float or a callable for both splitting_cond_test and "
                    "splitting_cond_val. Exiting..."
                )
            sys.exit(1)

    if shuffle:
        dataset = dataset.random_shuffle()

    # total number of events
    ntotal_evts = dataset.count()

    if not custom_splitting_condition:
        # random splitting
        if not do_kfold:
            if use_testing_dataset:
                # random splitting into training, validation and testing data. Rescale the validation split fraction
                # from a fraction of total events to a fraction of the remaining train+val events
                dataset_trainVal, dataset_test = dataset.train_test_split(test_size=test_split, seed=1234)
                dataset_train, dataset_val = dataset_trainVal.train_test_split(
                    test_size=val_split / (1 - test_split), seed=4321
                )
            else:
                # random splitting into training and validation data
                dataset_train, dataset_val = dataset.train_test_split(test_size=val_split, seed=1234)
        else:
            # when doing KFold splitting, create lists for all splits
            dataset_train, dataset_val = [], []

            # when a testing dataset is requested, a distinction needs to be made between fixed and non-fixed testing
            # dataset.
            if use_testing_dataset:
                dataset_test = []

                if fixed_test_dataset:
                    # If the testing dataset is required to be fixed, it is split off first using train_test_split.
                    dataset_trainVal, dataset_test_k = dataset.train_test_split(test_size=test_split, seed=1234)

                    # The remaining training+validation dataset is subsequently split into k folds where k is given by
                    # the requested size of the validation dataset. Each dataset is used once as the validation dataset.
                    num_folds = round((1 - test_split) / val_split)
                    dataset_trainVal_splits = dataset_trainVal.split(num_folds)
                    for k in range(num_folds):
                        # combine the splits into the training and validation datasets
                        datasets_train_k = dataset_trainVal_splits[:k] + dataset_trainVal_splits[k + 1 :]  # noqa: E203
                        dataset_train_k = datasets_train_k[0].union(*datasets_train_k[1:])
                        dataset_train.append(dataset_train_k)
                        dataset_val.append(dataset_trainVal_splits[k])

                        # add the fixed testing dataset
                        dataset_test.append(dataset_test_k)
                else:
                    # kfold is used for both the trainVal / test and the training/validation splits. Here, the test size
                    # defines the number of folds. To do that, the required number of splits to fulfill the requested
                    # test and validation sizes is calculated. From that, the Lowest Common Multiple defines the number
                    # of splits. As a result, the requested sizes of the validation and testing dataset can be achieved
                    # by combining a certain number of splits. E.g. if test_split=0.2, val_split=0.1, we need 5 splits
                    # for the test size, 10 splits for the validation size, thus 10 splits in total. We can then take
                    # 2 splits to get the testing size and just a single one to get the validation size.
                    num_splits = int(np.lcm(round(1 / test_split), round(1 / val_split)))
                    num_test_splits = int(num_splits / round(1 / test_split))
                    num_val_splits = int(num_splits / round(1 / val_split))
                    dataset_splits = dataset.split(num_splits)

                    # Since we (in general) don't need num_splits folds, we need to combine a certain number of folds to
                    # form the validation and testing dataset for each fold. The remaining folds are used for the
                    # training dataset. The number of folds we need is determined by the size of the testing dataset.
                    num_folds = int(num_splits / num_test_splits)
                    for k in range(0, num_splits, num_test_splits):
                        # get the indices of the block of splits that is to be used for testing
                        test_start = k
                        test_end = (
                            test_start + num_test_splits
                        ) % num_splits  # exclusive: test_end is not part of the test set anymore
                        if test_end > test_start:
                            test_indices = list(range(test_start, test_end))
                        else:
                            test_indices = list(range(test_start, num_splits)) + list(range(test_end))

                        # get the indices of the block of splits that is to be used for testing
                        val_start = test_end  # test_end is exclusive!
                        val_end = (val_start + num_val_splits) % num_splits  # exclusive
                        if val_end > val_start:
                            val_indices = list(range(val_start, val_end))
                        else:
                            val_indices = list(range(val_start, num_splits)) + list(range(val_end))

                        # the remaining splits are used for training
                        train_indices = [i for i in range(num_splits) if i not in test_indices + val_indices]

                        # build the datasets; giving empty argument list to union() results in an error, so check this
                        # manually.
                        if len(train_indices) > 1:
                            dataset_train_k = dataset_splits[train_indices[0]].union(
                                *[dataset_splits[i] for i in train_indices[1:]]
                            )
                        else:
                            dataset_train_k = dataset_splits[train_indices[0]]
                        if len(val_indices) > 1:
                            dataset_val_k = dataset_splits[val_indices[0]].union(
                                *[dataset_splits[i] for i in val_indices[1:]]
                            )
                        else:
                            dataset_val_k = dataset_splits[val_indices[0]]
                        if len(test_indices) > 1:
                            dataset_test_k = dataset_splits[test_indices[0]].union(
                                *[dataset_splits[i] for i in test_indices[1:]]
                            )
                        else:
                            dataset_test_k = dataset_splits[test_indices[0]]

                        # append to the lists
                        dataset_train.append(dataset_train_k)
                        dataset_val.append(dataset_val_k)
                        dataset_test.append(dataset_test_k)
            else:
                # The dataset is split into k folds where k is given by the requested size of the validation dataset.
                # Each dataset is used once as the validation dataset.
                num_folds = round(1 / val_split)
                dataset_splits = dataset.split(num_folds)
                for k in range(num_folds):
                    # combine the splits into the training and validation datasets
                    datasets_train_k = dataset_splits[:k] + dataset_splits[k + 1 :]  # noqa: E203
                    dataset_train_k = datasets_train_k[0].union(*datasets_train_k[1:])
                    dataset_train.append(dataset_train_k)
                    dataset_val.append(dataset_splits[k])
    else:
        # custom splitting based on EventNumber column
        # get the numpy array of event numbers and evaluate the splitting conditions
        # This weird way to fetch the data from the dataset is needed due to a (probable?) bug in Ray data. If
        # any of the take...() functions is used, more Ray tasks are executed in parallel than allowed by the
        # Placement group for some reason. This does not occur when using iter_batches()
        event_nums = list(dataset.select_columns(["EventNumber"]).iter_batches(batch_size=ntotal_evts))[0][
            "EventNumber"
        ]
        condition_val = splitting_cond_val(event_nums)
        if use_testing_dataset:
            condition_test = splitting_cond_test(event_nums)
            condition_train = [np.logical_not(c_v + c_t) for c_v, c_t in zip(condition_val, condition_test)]
        else:
            condition_train = np.logical_not(condition_val)
        if not do_kfold:
            if use_testing_dataset:
                # apply the splitting conditions as a single large batch
                dataset_train = dataset.map_batches(
                    lambda batch: {k: v[condition_train] for k, v in batch.items()}, batch_size=ntotal_evts
                ).materialize()
                dataset_val = dataset.map_batches(
                    lambda batch: {k: v[condition_val] for k, v in batch.items()}, batch_size=ntotal_evts
                ).materialize()
                dataset_test = dataset.map_batches(
                    lambda batch: {k: v[condition_test] for k, v in batch.items()}, batch_size=ntotal_evts
                ).materialize()
            else:
                # apply the splitting conditions as a single large batch
                dataset_train = dataset.map_batches(
                    lambda batch: {k: v[condition_train] for k, v in batch.items()}, batch_size=ntotal_evts
                ).materialize()
                dataset_val = dataset.map_batches(
                    lambda batch: {k: v[condition_val] for k, v in batch.items()}, batch_size=ntotal_evts
                ).materialize()
        else:
            # prepare empty lists for all datasets
            dataset_train, dataset_val = [], []
            if use_testing_dataset:
                dataset_test = []

            # apply the splitting conditions as a single large batch, for each fold individually
            num_folds = len(condition_val)
            for k in range(num_folds):
                dataset_train.append(
                    dataset.map_batches(
                        lambda batch, k_fold=k: {key: v[condition_train[k_fold]] for key, v in batch.items()},
                        batch_size=ntotal_evts,
                    ).materialize()
                )
                dataset_val.append(
                    dataset.map_batches(
                        lambda batch, k_fold=k: {key: v[condition_val[k_fold]] for key, v in batch.items()},
                        batch_size=ntotal_evts,
                    ).materialize()
                )
                if use_testing_dataset:
                    dataset_test.append(
                        dataset.map_batches(
                            lambda batch, k_fold=k: {key: v[condition_test[k_fold]] for key, v in batch.items()},
                            batch_size=ntotal_evts,
                        ).materialize()
                    )

    # write a summary
    if not do_kfold:
        if use_testing_dataset and not disable_printing:
            print(
                f"splitting the total number of {ntotal_evts} events in {dataset_train.count()} train, "
                f"{dataset_val.count()} validation and {dataset_test.count()} test events."
            )
        elif not disable_printing:
            print(
                f"splitting the total number of {ntotal_evts} events in {dataset_train.count()} train and "
                f"{dataset_val.count()} validation events."
            )
    else:
        if not disable_printing:
            print(f"splitting the total number of {ntotal_evts} events using {num_folds}-Fold splitting:")
            for i in range(num_folds):
                if use_testing_dataset:
                    print(
                        f"\tsplit {i+1}: {dataset_train[i].count()} train, {dataset_val[i].count()} validation "
                        f"and {dataset_test[i].count()} test events"
                    )
                else:
                    print(
                        f"\tsplit {i + 1}: {dataset_train[i].count()} train and {dataset_val[i].count()} validation "
                        f"events"
                    )

    # return the results
    if use_testing_dataset:
        return dataset_train, dataset_val, dataset_test
    else:
        return dataset_train, dataset_val
