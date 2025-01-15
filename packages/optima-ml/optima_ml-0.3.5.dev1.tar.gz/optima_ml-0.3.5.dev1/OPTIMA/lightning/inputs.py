# -*- coding: utf-8 -*-
"""Collection of classes and functions specific to the handling of the training input for Lightning models."""
import lightning as pl
import torch

from typing import Optional, Tuple, Union, Any
from types import ModuleType

import ray

import OPTIMA.builtin.inputs

model_config_type = dict[str, Union[int, float, str, Any]]


class LightningDataset(torch.utils.data.Dataset):
    """Tensor dataset with in-memory batching to improve performance."""

    def __init__(
        self, inputs: torch.Tensor, targets: torch.Tensor, weights: Optional[torch.Tensor] = None, batch_size: int = 1
    ) -> None:
        """Constructor of ``LightningDataset``.

        Parameters
        ----------
        inputs : torch.Tensor
            Torch tensor of input features.
        targets : torch.Tensor
            Torch tensor of target labels.
        weights : Optional[torch.Tensor]
            Torch tensor of event weights. (Default value = None)
        batch_size : int
            The batch size of the dataset. (Default value = 1)
        """
        self.inputs = inputs
        self.targets = targets
        self.weights = weights

        self.len = len(inputs) // batch_size
        self.batch_size = batch_size

    def __len__(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        return self.len

    def __getitem__(
        self, idx: int
    ) -> Union[Tuple[torch.Tensor, torch.Tensor, torch.Tensor], Tuple[torch.Tensor, torch.Tensor]]:
        """_summary_.

        Parameters
        ----------
        idx : int
            _description_

        Returns
        -------
        Union[Tuple[torch.Tensor, torch.Tensor, torch.Tensor], Tuple[torch.Tensor, torch.Tensor]]
            _description_
        """
        start = self.batch_size * idx
        end = self.batch_size * (idx + 1)

        if self.weights is not None:
            return self.inputs[start:end], self.targets[start:end], self.weights[start:end]
        else:
            return self.inputs[start:end], self.targets[start:end]


def get_dataset(
    ray_dataset: ray.data.Dataset,
    run_config: ModuleType,
    model_config: Optional[model_config_type] = None,
) -> torch.utils.data.Dataset:
    """Helper function to build a Torch dataset from a Ray Dataset.

    If a ``LightningDataset`` class is defined in the `run-config`, its constructor is provided with the ``ray_dataset``
    and the ``model_config``. It is expected to return a Torch dataset.

    Otherwise, the Ray Dataset is assumed to have columns ``Input`` containing the input features, ``Target`` containing
    the target labels and optionally ``Weight`` containing sample weights. The columns are converted to Tensors and a
    Torch ``TensorDataset`` is built. Since in this case, the entire dataset is loaded into memory, an OOM error may
    occur for very large datasets. If this is the case, a ``LightningDataset`` class must be defined in the `run-config`
    to dynamically stream the data from the Ray Dataset.

    Parameters
    ----------
    ray_dataset : ray.data.Dataset
        The Ray Dataset from which a Torch dataset should be built.
    run_config : ModuleType
        Reference to the imported run-config file.
    model_config : Optional[model_config_type]
        The model-config of the Lightning model this dataset is to be built for. This is only provided to the
        ``LightningDataset``-class in the `run-config` (if present). (Default value = None)

    Returns
    -------
    torch.utils.data.Dataset
        The built dataset.
    """
    if hasattr(run_config, "LightningDataset"):
        dataset = run_config.LightningDataset(ray_dataset, model_config)
    else:
        # fetch the input features, target labels and optional sample weights --> this saves everything into this
        # worker's memory. If OOM error occurs, define a LightningDataset class in the run_config to build a torch
        # dataset that streams the data from the object store as needed
        # This weird way to fetch the data from the dataset is needed due to a (probable?) bug in Ray data. If
        # any of the take...() functions is used, more Ray tasks are executed in parallel than allowed by the
        # Placement group for some reason. This does not occur when using iter_batches()
        data = list(ray_dataset.iter_batches(batch_size=ray_dataset.count()))[0]
        inputs = torch.from_numpy(data["Input"].copy()).type(torch.float)
        targets = torch.from_numpy(data["Target"].copy()).type(torch.float)
        if "Weight" in ray_dataset.columns():
            weights = torch.from_numpy(data["Weight"].copy()).type(torch.float)
            dataset = torch.utils.data.TensorDataset(inputs, targets, weights)
        else:
            dataset = torch.utils.data.TensorDataset(inputs, targets)
    return dataset


def get_dataloader(
    run_config: ModuleType, model_config: model_config_type, dataset: torch.utils.data.Dataset
) -> torch.utils.data.DataLoader:
    """Helper function to build a dataloader from a torch dataset.

    By default, a ``torch.utils.data.DataLoader`` is instantiated, with the ``batch_size`` set to the ``"batch_size"``
    entry in the provided ``model_config``. To overwrite this behavior, a ``Dataloader``-class can be defined in the
    `run-config`. It is provided with the Torch ``dataset`` and the ``model_config``.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported run-config file.
    model_config : model_config_type
        The model-config of the Lightning model this dataset is to be built for. If a ``Dataloader``-class is defined
        in the `run-config`, it is provided directly to the constructor. If this is not the case, it is expected to
        contain a ``"batch_size"``-entry that is provided to the ``torch.utils.data.DataLoader``.
    dataset : torch.utils.data.Dataset
        The dataset to be wrapped in a dataloader.

    Returns
    -------
    torch.utils.data.DataLoader
        The built dataloader.
    """
    if hasattr(run_config, "DataLoader"):
        dataloader = run_config.DataLoader(dataset, model_config)
    else:
        dataloader = torch.utils.data.DataLoader(dataset, batch_size=model_config["batch_size"])
    return dataloader


class DefaultDataModule(pl.LightningDataModule):
    """A LightningDataModule that provides default functionality."""

    def __init__(
        self,
        run_config: ModuleType,
        model_config: model_config_type,
        input_handler: Optional[OPTIMA.builtin.inputs.InputHandler] = None,
        dataset_train: Optional[ray.data.Dataset] = None,
        dataset_val: Optional[ray.data.Dataset] = None,
        dataset_test: Optional[ray.data.Dataset] = None,
        dataset_predict: Optional[ray.data.Dataset] = None,
    ):
        """Constructor of ``DefaultDataModule``.

        It represents the easiest possible implementation of a ``LightningDataModule``. The datasets are built by calling
        the ``get_dataset``-function. The dataloaders are provided by ``get_dataloader``.

        Parameters
        ----------
        run_config : ModuleType
            Reference to the imported run-config file.
        model_config : model_config_type
            The model-config of the Lightning model this data module is to be built for.
        input_handler : Optional[OPTIMA.builtin.inputs.InputHandler]
            Instance of the ``InputHandler``-class. While not needed for the built-in DataModule, a DataModule defined
            in the `run-config` may need to know the inputs they are provided with, and will, thus, be provided with the
            ``input_handler``. (Default value = None)
        dataset_train : Optional[ray.data.Dataset]
            A Ray dataset containing the training data. (Default value = None)
        dataset_val : Optional[ray.data.Dataset]
            A Ray dataset containing the validation data. (Default value = None)
        dataset_test : Optional[ray.data.Dataset]
            A Ray dataset containing the testing data. (Default value = None)
        dataset_predict : Optional[ray.data.Dataset]
            A Ray dataset containing the predict data. (Default value = None)
        """
        super().__init__()

        self.ray_dataset_train = dataset_train
        self.ray_dataset_val = dataset_val
        self.ray_dataset_test = dataset_test
        self.ray_dataset_predict = dataset_predict

        self.run_config = run_config
        self.model_config = model_config

        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None
        self.predict_dataset = None

    def prepare_data(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        pass

    def setup(self, stage: str = None):
        """_summary_.

        Parameters
        ----------
        stage : str
            _description_ (Default value = None)

        Returns
        -------
        _type_
            _description_
        """
        # get the datasets
        if stage == "fit":
            self.train_dataset = get_dataset(self.ray_dataset_train, self.run_config, self.model_config)
            self.val_dataset = get_dataset(self.ray_dataset_val, self.run_config, self.model_config)
        elif stage == "validate":
            self.val_dataset = get_dataset(self.ray_dataset_val, self.run_config, self.model_config)
        elif stage == "test":
            self.test_dataset = get_dataset(self.ray_dataset_test, self.run_config, self.model_config)
        elif stage == "predict":
            self.predict_dataset = get_dataset(self.ray_dataset_predict, self.run_config, self.model_config)

    def train_dataloader(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        dataloader = get_dataloader(self.run_config, self.model_config, self.train_dataset)
        return dataloader

    def val_dataloader(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        dataloader = get_dataloader(self.run_config, self.model_config, self.val_dataset)
        return dataloader

    def test_dataloader(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        dataloader = get_dataloader(self.run_config, self.model_config, self.test_dataset)
        return dataloader

    def predict_dataloader(self):
        """_summary_.

        Returns
        -------
        _type_
            _description_
        """
        dataloader = get_dataloader(self.run_config, self.model_config, self.predict_dataset)
        return dataloader
