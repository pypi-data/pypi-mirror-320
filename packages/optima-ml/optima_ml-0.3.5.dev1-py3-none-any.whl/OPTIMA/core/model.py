# -*- coding: utf-8 -*-
"""A module that provides abstract functionality to interact with models from different libraries."""
from types import ModuleType
from typing import Any, Optional, Union, Callable, Generator

import sys
import inspect

import ray.data

if sys.platform == "darwin":
    import multiprocess as mp
else:
    import multiprocessing as mp

import numpy as np

import importlib.util

import OPTIMA.builtin.inputs

model_config_type = dict[str, Union[int, float, str, Any]]

if importlib.util.find_spec("tensorflow") is not None:
    import tensorflow as tf
    import OPTIMA.keras.model

if importlib.util.find_spec("lightning") is not None:
    import torch
    import lightning
    import OPTIMA.lightning.inputs


class AbstractModel:
    """Simple wrapper to provide generic model functionality for different machine learning libraries.

    Supported are Keras and Lightning models.
    """

    def __init__(
        self,
        run_config: ModuleType,
        model: Any,
        model_config: model_config_type,
        input_handler: OPTIMA.builtin.inputs.InputHandler,
        pl_trainer: Optional["lightning.Trainer"] = None,
    ) -> None:
        """Constructor of AbstractModel.

        Parameters
        ----------
        run_config : ModuleType
            Reference to the imported `run-config`-file.
        model : Any
            The model that should be wrapped.
        model_config : model_config_type
            Dictionary containing the values for each hyperparameter
        input_handler : OPTIMA.builtin.inputs.InputHandler
            Instance of the ``OPTIMA.builtin.inputs.InputHandler``-class
        pl_trainer : Optional["lightning.Trainer"]
            When using Lightning, a Trainer is necessary to do the inference. (Default value = None)
        """
        self.run_config = run_config
        self.model = model
        self.model_config = model_config
        self.input_handler = input_handler

        if run_config.model_type == "Lightning":
            self.pl_trainer = pl_trainer

    def prepare_datasets(
        self,
        dataset_train: Optional[ray.data.Dataset] = None,
        dataset_val: Optional[ray.data.Dataset] = None,
        dataset_test: Optional[ray.data.Dataset] = None,
        dataset_predict: Optional[ray.data.Dataset] = None,
    ) -> Union[list["tf.data.Dataset"], "lightning.LightningDataModule"]:
        """Helper function that converts ray datasets to machine learning library native datasets.

        At least one of ``dataset_train``, ``dataset_val``, ``dataset_test`` or ``dataset_predict`` must not be ``None``.

        For Keras, individual Tensorflow datasets are built for each prodided ray dataset. If a
        ``build_tensorflow_dataset``-function is defined in the `run-config`, it is used. Otherwise, the datasets are
        assumed to contain the columns ``Input`` for the input features, ``Target`` for the target labels and optionally
        ``Weight`` containing sample weights. The Tensorflow datasets are built by calling the
        ``tf.data.Dataset.from_tensor_slices()``-function and providing the input features, target labels and optionally
        sample weights.

        For Lightning, a ``LightningDataModule`` is built. If a ``DataModule`` class is available in the `run-config`, it
        is used. Otherwise, the built-in ``LightningDataModule`` defined in ``OPTIMA.lightning.inputs.DefaultDataModule``
        is used. In both cases, the constructor of the ``LightningDataModule`` is provided with all ray datasets via
        keyword arguments ``dataset_train``, ``dataset_val``, ``dataset_test``, ``dataset_predict``, respectively.

        Parameters
        ----------
        dataset_train : Optional[ray.data.Dataset]
            The Ray dataset containing the training data. (Default value = None)
        dataset_val : Optional[ray.data.Dataset]
            The Ray dataset containing the validation data. (Default value = None)
        dataset_test : Optional[ray.data.Dataset]
            The Ray dataset containing the testing data. (Default value = None)
        dataset_predict : Optional[ray.data.Dataset]
            The Ray dataset containing the predict data. (Default value = None)

        Returns
        -------
        Union[list["tf.data.Dataset"], "lightning.LightningDataModule"]
            For Keras, a Tensorflow datasets is returned for every non-``None`` dataset provided, in the order
            ``dataset_train``, ``dataset_val``, ``dataset_test``, ``dataset_predict``. For Lightning, a
            ``LightningDataModule``-instance is returned.
        """
        # check if at least one dataset was provided
        assert (
            dataset_train is not None
            or dataset_val is not None
            or dataset_test is not None
            or dataset_predict is not None
        ), "At least one dataset must be provided!"

        # convert the ray datasets to tensorflow datasets or a lightning DataModule
        if self.run_config.model_type == "Keras":
            # collect the non-None datasets
            datasets = [d for d in [dataset_train, dataset_val, dataset_test, dataset_predict] if d is not None]

            # build the tensorflow datasets
            tf_datasets = []
            if hasattr(self.run_config, "build_tensorflow_dataset"):
                for dataset in datasets:
                    tf_datasets.append(
                        self.run_config.build_tensorflow_dataset(
                            dataset, self.input_handler, self.run_config, self.model_config
                        )
                    )
            else:
                import tensorflow as tf

                # fetch the input features, target labels and optional sample weights --> this saves everything into this
                # worker's memory. If OOM error occurs, define a build_tensorflow_dataset function in the run_config to
                # build a tensorflow dataset that streams the data from the object store as needed
                # This weird way to fetch the data from the dataset is needed due to a (probable?) bug in Ray data. If
                # any of the take...() functions is used, more Ray tasks are executed in parallel than allowed by the
                # Placement group for some reason. This does not occur when using iter_batches()
                data_list = []
                for dataset in datasets:
                    data_list.append(list(dataset.iter_batches(batch_size=dataset.count()))[0])
                for data in data_list:
                    inputs = data["Input"]
                    targets = data["Target"]
                    if "Weight" in dataset.columns():
                        weights = data["Weight"]
                        tf_dataset = tf.data.Dataset.from_tensor_slices((inputs, targets, weights))
                    else:
                        tf_dataset = tf.data.Dataset.from_tensor_slices((inputs, targets))

                    # batch the datasets
                    tf_datasets.append(tf_dataset.batch(self.model_config["batch_size"]))

            return tf_datasets

        elif self.run_config.model_type == "Lightning":
            if hasattr(self.run_config, "DataModule"):
                DataModule = self.run_config.DataModule
            else:
                DataModule = OPTIMA.lightning.inputs.DefaultDataModule
            pl_data_module = DataModule(
                run_config=self.run_config,
                model_config=self.model_config,
                input_handler=self.input_handler,
                dataset_train=dataset_train,
                dataset_val=dataset_val,
                dataset_test=dataset_test,
                dataset_predict=dataset_predict,
            )
            return pl_data_module

    def predict(
        self,
        data: Union[
            "tf.data.Dataset", tuple["tf.data.Dataset"], list["tf.data.Dataset"], "lightning.LightningDataModule"
        ],
        verbose: int = 0,
    ) -> Union[Any, tuple[Any]]:
        """Calculates the model prediction for the provided input data.

        Parameters
        ----------
        data : Union["tf.data.Dataset", tuple["tf.data.Dataset"], list["tf.data.Dataset"], "lightning.LightningDataModule"]
            For Keras, a Tensorflow dataset or a tuple or list of Tensorflow datasets. For Lightning, a
            ``LightningDataModule`` instance.
        verbose : int
            Parameter to control the verbosity of the prediction. This is currently only used for Keras. (Default value = 0)

        Returns
        -------
        Union[Any, tuple[Any]]
            The numpy array of model predictions.
        """
        if self.run_config.model_type == "Keras":
            if not isinstance(data, list) or isinstance(data, tuple):
                data = [data]

            # iterate over the provided tensorflow datasets
            preds = []
            for dataset in data:
                # add the predictions for this dataset
                preds.append(self.model.predict(dataset, verbose=verbose))

            if len(preds) == 1:
                return preds[0]
            else:
                return tuple(preds)
        elif self.run_config.model_type == "Lightning":
            # TODO: Doc string + typing!
            raise NotImplementedError
            # for stage in ["train", "val", "test", "predict"]:
            #     # check if the DataModule has data for this stage
            #     if not
            #
            #
            #
            #
            #
            #
            # # make a copy of the array to ensure it is writable (pytorch currently only supports converting from writable
            # # numpy arrays) and wrap the input in a dataloader
            # inputs = inputs.copy()
            # inputs_tensor = torch.from_numpy(inputs).type(torch.float)
            # dataloader = OPTIMA.lightning.inputs.get_dataloader(
            #     self.run_config, self.model.hparams.model_config, inputs_tensor
            # )
            #
            # # do the prediction. This returns a list of tensors that need to be converted to a numpy array.
            # prediction_list = self.pl_trainer.predict(self.model, dataloader)
            # prediction_array_list = [t.cpu().detach().numpy() for t in prediction_list]
            # prediction_array = np.concatenate(prediction_array_list, axis=0)
            # return prediction_array

    def batched_predict(
        self,
        dataset: Optional[Union["tf.data.Dataset", "lightning.LightningDataModule"]] = None,
        stage: Optional[str] = None,
    ) -> Generator[Any, None, None]:
        """Returns a generator that yields batches of model inputs and outputs for the provided datasets.

        If the data contains a conventional batch axis, i.e. the first axis of all tensors is the batch axis, this
        function allows to "re-batch" the inputs and outputs to a batch size just larger than
        ``self.predict_batch_size``. This is useful if the full dataset is too large to be kept in memory, but
        individual dataset batches are too small to be practical to e.g. calculate metrics. Therefore, this function
        combines multiple batches until the total batch size just exceeds the value given in ``self.predict_batch_size``.

        This function can handle arbitrarily nested structures of tensorflow / pytorch objects, e.g. tuples of dicts of
        tensors, for both the input data and the model predictions. A minimal set of assumptions is made, depending on
        the machine learning backend used:

        - Keras:

            - The input dataset is assumed to yield a tuple where the first element contains the input features (as is
              also assumed by default by Keras's ``model.fit()`` function).
            - If the data contains a conventional batch axis, i.e. if ``conventional_batch_axis`` is set to ``True`` in
              the run-config, the input dataset is assumed to be batched, i.e. it yields batches of inputs instead of
              individual samples. It is additionally assumed that the first axis of any contained tensor is the batch
              axis, and thus every tensor has the same dimensionality along the first axis. The batch size is allowed to
              vary from batch to batch.
            - If ``conventional_batch_axis`` is set to ``True`` in the run-config, it is assumed that when provided with
              an input batch, the model output is a batch of predictions. As such, it is assumed that the first axis of
              any contained tensor is the batch axis, and thus every tensor has the same dimensionality along the first
              axis. The batch size is assumed to correspond to the batch size of the input batch.

        - Lightning:

            - ``trainer.datamodule`` implements the ``train_dataloader()`` and ``val_dataloader()`` functions
            - The training and validation dataloaders yield a tuple where the first tuple element contains the input
              features.
            - The ``pl_module`` implements the ``predict_step()`` function, which accepts the input features as yielded
              by the dataloaders (i.e. without possible target labels or sample weights) and returns the corresponding
              model predictions.
            - If the data contains a conventional batch axis, i.e. if ``conventional_batch_axis`` is set to ``True`` in
              the run-config, the input datasets are assumed to be batched. As such, the first axis of any contained
              tensor contained in the batch yielded by the datalaoders is the batch axis, and thus every tensor has the
              same dimensionality along the first axis. The batch size is allowed to vary from batch to batch.
            - If ``conventional_batch_axis`` is set to ``True`` in the run-config, it is assumed that when provided with
              an input batch, the model output is a batch of predictions. As such, the first axis of any contained
              tensor is the batch axis, and thus every tensor has the same dimensionality along the first axis. The
              batch size is assumed to correspond to the batch size of the input batch.

        By default, the inputs and predictions are obtained as lists of structures of Tensorflow / Pytorch objects where
        each list element corresponds to a dataset batch. This allows maximal flexibility, as, besides the aforementioned
        assumptions, no assumptions on the structure of the input and output data are necessary. If possible, however,
        both inputs and predictions are converted to structures of NumPy arrays for more convenient usage in metrics.
        This is done in multiple steps, with slight differences depending on the machine learning backend used:

        1. For Keras: It is checked if the input dataset can be expressed using numpy arrays by calling the
           ``as_numpy_iterator()`` function of the dataset. Doing so allows expressing the input data using numpy arrays
           while conserving the structure of the data (i.e. tuples of tensors will become tuples of numpy arrays). If
           this raises a ``TypeError``, e.g. if the dataset contains non-tensor objects, both inputs and predictions are
           returned in the native Tensorflow format. In any case, the model is provided with the Tensorflow batches when
           calculating predictions.

           For Lightning: For each batch, the input data is tried to be converted to NumPy arrays. This conversion
           replaces Pytorch tensors with NumPy arrays while conserving the structure of the model outputs. If this
           conversion fails, e.g. if the batch contains sparse tensors, both inputs and outputs are returned in the
           native Pytorch format for this and all following batches (see 'Open issues' regarding an edge-case). If the
           conversion succeeds, the inputs are now expressed as lists of structures of NumPy arrays. Each list element
           corresponds to a dataset batch. In any case, to calculate the model predictions, the model is provided with
           the Pytorch batches.
        2. If the conversion in 1. succeeded, for each batch of the dataset, the corresponding predictions are tried to
           be converted to NumPy arrays. This conversion replaces Tensorflow / Pytorch tensors with NumPy arrays while
           conserving the structure of the model outputs. If this conversion fails, e.g. if the predictions contain
           objects other than tensors (e.g. sparse tensors), both inputs and outputs are returned in the native
           Tensorflow / Pytorch format for this and all following batches (see 'Open issues' regarding an edge-case). If
           the conversion succeeds, both the inputs and outputs are now expressed as lists of structures of NumPy arrays.
           Each list element corresponds to a dataset batch. If ``conventional_batch_axis`` is set to ``False`` in the
           run-config, each list element is yielded individually (while ensuring that only a single element is kept in
           memory at a time). Otherwise, step 3 is executed.
        3. If the conversion in 2. succeeded for all dataset batches until now, it is checked if multiple dataset
           batches can be combined into single NumPy arrays. This is possible if:

           - the structure of inputs and outputs is fixed across batches (e.g. the input is always a tuple of 3 arrays)
           - the shapes of all NumPy arrays is fixed for all axes except the batch axis (axis 0) across dataset batches,
             i.e. the model accepts inputs of a fixed shape and returns predictions of a fixed shape.

           This information needs to be provided in the run-config as parameters ``fixed_input_shape`` and
           ``fixed_output_shape``. The batch size is allowed to vary as concatenation of NumPy arrays along axis 0
           only requires the shapes of all axes other than 0 to be constant.

           If these conditions hold, the list of structures of NumPy arrays is converted to a single structure of NumPy
           arrays. This single structure is the same structure as the individual structures in the original list (i.e. a
           list of tuples of NumPy arrays will be converted to a single tuple of NumPy arrays, with the correct NumPy
           arrays concatenated along axis 0). If the conversion is not possible, the lists created in step 2 are
           returned instead.

        Open issues:

        - Keras: If the input dataset can be expressed using numpy arrays (i.e. dataset.as_numpy_iterator() does not
          raise a ``TypeError``), and the model output in the first batch can be expressed using numpy arrays, but the
          model output for a later batch cannot be converted to numpy arrays, the function will yield mixed data types.
          In this case all batches until the first batch where the model output cannot be converted will be expressed
          using numpy arrays while any following batches will contain Tensorflow objects. The predict batch where the
          conversion failed for the first time will likely contain a mix of numpy and Tensorflow objects. This problems
          cannot be solved without first calculating the model outputs for the entire dataset or introducing a flag that
          specifies if the model output can always be converted to numpy arrays (to be specified by the user).
        - Lightning: If the inputs and corresponding model outputs in the first batch can be expressed using NumPy
          arrays, but the inputs or outputs for a later batch cannot be converted to NumPy arrays, the function will
          yield mixed data types. In this case all batches until the first batch where the conversion was not possible
          will be expressed using NumPy arrays while any following batches will contain Pytorch objects. The predict
          batch where the conversion failed for the first time will likely contain a mix of NumPy and Pytorch objects.
          This problems cannot be solved without first calculating the model outputs for the entire dataset or
          introducing a flag that specifies if inputs and outputs can always be converted to NumPy arrays (to be
          specified by the user).

        Parameters
        ----------
        dataset : Optional[Union["tf.data.Dataset", "lightning.LightningDataModule"]]
            The Tensorflow datasets / Lightning data module to run the batched prediction on. It must be provided when
            using Keras as the backend. For Lightning, it may be omitted, in which case the ``datamodule`` member of the
            lightning trainer provided to the constructor is assumed to not be ``None``. (Default value = None)
        stage : Optional[str]
            Only used when using Lightning backend. Signifies for which dataset in the data module predictions should be
            calculated. Must be either ``'train'``, ``'val'`` or ``'test'``. If is assumed that the data module
            implements the corresponding dataloader getters. (Default value = None)

        Returns
        -------
        Generator[Any, None, None]
            The generator that yields batches of inputs and corresponding model predictions.
        """

        def _get_batch_size(batch):
            """_summary_.

            Parameters
            ----------
            batch : _type_
                _description_

            Returns
            -------
            _type_
                _description_
            """
            # Since we assume that the dimension of every tensor along the first axis is the same in the entire data
            # structure, we only need to find one tensor / numpy array to get the batch size.
            d = batch[0]
            while True:
                if self.run_config.model_type == "Keras" and (
                    isinstance(d, np.ndarray)
                    or isinstance(d, tf.Tensor)
                    or isinstance(d, tf.SparseTensor)
                    or isinstance(d, tf.RaggedTensor)
                ):
                    return d.shape[0]
                elif self.run_config.model_type == "Lightning" and (
                    isinstance(d, np.ndarray) or isinstance(d, torch.Tensor) or isinstance(d, torch.sparse.Tensor)
                ):
                    return d.shape[0]
                elif isinstance(d, dict):
                    # grab one dictionary value and repeat
                    d = next(iter(d.values()))
                elif isinstance(d, list) or isinstance(d, tuple):
                    # grab the first list / tuple entry and repeat
                    d = d[0]

        def _convert_tensors_to_numpy(structure):
            """_summary_.

            Parameters
            ----------
            structure : _type_
                _description_

            Returns
            -------
            _type_
                _description_
            """
            if self.run_config.model_type == "Keras" and isinstance(structure, tf.Tensor):
                return structure.numpy()
            elif self.run_config.model_type == "Lightning" and isinstance(structure, torch.Tensor):
                return structure.numpy()
            elif isinstance(structure, list):
                return [_convert_tensors_to_numpy(item) for item in structure]
            elif isinstance(structure, tuple):
                return tuple(_convert_tensors_to_numpy(item) for item in structure)
            elif isinstance(structure, dict):
                return {key: _convert_tensors_to_numpy(value) for key, value in structure.items()}
            else:
                raise TypeError("Unsupported data type: {}".format(type(structure)))

        def _concatenate_nested_structures(structures, axis=0):
            """_summary_.

            Parameters
            ----------
            structures : _type_
                _description_
            axis : _type_
                _description_ (Default value = 0)

            Returns
            -------
            _type_
                _description_
            """
            if not isinstance(structures, list) or not structures:
                raise ValueError("Input should be a non-empty list")

            def concatenate_recursive(items):
                """_summary_.

                Parameters
                ----------
                items : _type_
                    _description_

                Returns
                -------
                _type_
                    _description_
                """
                if isinstance(items[0], np.ndarray):
                    # We arrived at the lowest level and only have a list of numpy arrays. Concatenate and return.
                    return np.concatenate(items, axis=axis)
                elif isinstance(items[0], list):
                    # We have a list of lists. Fetch all ith elements in all lists, concatenate, and rebuild the list.
                    return [concatenate_recursive([item[i] for item in items]) for i in range(len(items[0]))]
                elif isinstance(items[0], tuple):
                    # We have a list of tuples. Fetch all ith elements in the tuples, concatenate, and rebuild the tuple.
                    return tuple(concatenate_recursive([item[i] for item in items]) for i in range(len(items[0])))
                elif isinstance(items[0], dict):
                    # We have a list of dictionaries. Fetch the keys of the dicts.
                    keys = items[0].keys()

                    # For each key, collect all values in the list, concatenate, and rebuild the dict.
                    return {key: concatenate_recursive([item[key] for item in items]) for key in keys}
                else:
                    raise TypeError("Unsupported data type: {}".format(type(items[0])))

            return concatenate_recursive(structures)

        def _get_batched_yield_values(data, preds, numpy_inputs, numpy_predictions):
            """_summary_.

            Parameters
            ----------
            data : _type_
                _description_
            preds : _type_
                _description_
            numpy_inputs : _type_
                _description_
            numpy_predictions : _type_
                _description_

            Returns
            -------
            _type_
                _description_
            """
            if self.run_config.conventional_batch_axis:
                # if possible, concatenate inputs and predictions across batches. This is done consistently,
                # i.e if the inputs can only be represented as a list, the predictions should not be concatenated
                # into a single array.
                # Start with the inputs. If the input data is available as numpy arrays and the shapes are fixed according
                # to the user, and the same is true for the model predictions, try to concatenate the data numpy arrays
                # across batches. This should be possible if the shapes of the arrays are fixed. Since the structure of the
                # input data is unknown and can be arbitrarily nested, and the concatenated result should still reflect this
                # structure, use a recursive approach. If the inputs cannot be concatenated, use the list directly.
                if (
                    numpy_inputs
                    and self.run_config.fixed_input_shape
                    and numpy_predictions
                    and self.run_config.fixed_output_shape
                ):
                    try:
                        ret_data = _concatenate_nested_structures(data)
                        concatenated_inputs = True
                    except ValueError:
                        # the concatenation has failed for an unknown reason, likely because the structure or shape of the
                        # inputs vary although the user said they wouldn't. Use the list of arrays directly.
                        ret_data = data
                        concatenated_inputs = False
                else:
                    # use the list of values directly. This is now either a list of numpy arrays (if the inputs can be
                    # converted to numpy arrays but the shapes vary) or a list of Tensorflow / Pytorch objects (if they
                    # cannot be converted to numpy arrays)
                    ret_data = data
                    concatenated_inputs = False

                # Next try the predictions. Only try if concatenating the inputs was successful.
                if concatenated_inputs and numpy_predictions and self.run_config.fixed_output_shape:
                    try:
                        ret_preds = _concatenate_nested_structures(preds)
                    except ValueError:
                        # the concatenation has failed for an unknown reason, likely because the structure or shape of the
                        # outputs vary although the user said they wouldn't. Use the list of arrays directly.
                        ret_preds = preds
                else:
                    # the output shapes can vary from batch to batch, or concatenating the inputs was unsuccessful, thus
                    # use the list of predictions directly
                    ret_preds = preds

                # if both concatenations succeeded, return the arrays. Otherwise, return the lists.
                return ret_data, ret_preds
            else:
                # there is no conventional batch axis, thus data and preds will be lists containing one element each.
                # without a batch axis, it does not make sense to return the list as is. Instead, return the elements
                # directly
                return data, preds

        if self.run_config.model_type == "Keras":
            # calculate the predictions in batches
            # holds the inputs and corresponding predictions for multiple dataset batches
            num_samples = 0
            data = []
            preds = []

            # try to convert the dataset to use numpy arrays instead of tensors
            try:
                dataset_numpy_it = dataset.as_numpy_iterator()
                numpy_inputs = True
            except TypeError:
                numpy_inputs = False

            # if a prediction could once not be converted to numpy arrays, it should also not be possible for the
            # remaining batches, so we only need to check this once.
            numpy_predictions = None

            # iterate over the dataset
            for batch in dataset:
                # add the batch to the list. Use the numpy arrays if available and if the predictions are not known to
                # not be convertable, otherwise use the values directly from the Tensorflow dataset.
                if numpy_inputs and numpy_predictions is not False:
                    data.append(next(dataset_numpy_it))
                else:
                    data.append(batch)

                # get the model predictions for this batch. This assumes that batch[0] contains the input features.
                pred = OPTIMA.keras.model.predict_batch(self.model, batch[0])

                # check if the output is a structure of Tensors that can be converted to a structure of numpy arrays.
                # If not, e.g. if the output is a structure of SparseTensors, use the predictions as they are. This is
                # only useful if the inputs can be expressed as numpy arrays.
                if numpy_inputs and numpy_predictions is not False:
                    try:
                        preds.append(_convert_tensors_to_numpy(pred))
                        numpy_predictions = True
                    except TypeError:
                        preds.append(pred)
                        numpy_predictions = False
                else:
                    preds.append(pred)
                    numpy_predictions = False

                # if a conventional batch axis is used, and the dataset cannot be consumed in a single batch, yield
                # intermediate values
                if self.run_config.predict_batch_size != -1 and self.run_config.conventional_batch_axis:
                    # remember how many samples were already consumed for this batch
                    num_samples += _get_batch_size(batch)

                    # check if enough samples were consumed to yield a batch
                    if num_samples >= self.run_config.predict_batch_size:
                        yield _get_batched_yield_values(data, preds, numpy_inputs, numpy_predictions)

                        # reset
                        num_samples = 0
                        data = []
                        preds = []
                elif not self.run_config.conventional_batch_axis:
                    # no conventional batch axis. Simply yield every batch individually.
                    yield _get_batched_yield_values(data, preds, numpy_inputs, numpy_predictions)

                    # reset
                    num_samples = 0
                    data = []
                    preds = []

            # yield the remaining predictions
            if self.run_config.conventional_batch_axis and (
                self.run_config.predict_batch_size == -1 or num_samples > 0
            ):
                yield _get_batched_yield_values(data, preds, numpy_inputs, numpy_predictions)
        elif self.run_config.model_type == "Lightning":
            # grab the dataloader
            if dataset is None:
                # if not data module is provided, assume the trainer has a data module
                if stage == "train":
                    dataloader = self.pl_trainer.datamodule.train_dataloader()
                elif stage == "val":
                    dataloader = self.pl_trainer.datamodule.val_dataloader()
                elif stage == "test":
                    dataloader = self.pl_trainer.datamodule.test_dataloader()
                else:
                    raise ValueError(f"Unknown stage {stage}.")
            else:
                # take the dataloader directly from the data module
                if stage == "train":
                    dataloader = dataset.train_dataloader()
                elif stage == "val":
                    dataloader = dataset.val_dataloader()
                elif stage == "test":
                    dataloader = dataset.test_dataloader()
                else:
                    raise ValueError(f"Unknown stage {stage}.")

            # calculate the predictions in batches
            # holds the inputs and corresponding predictions for multiple dataset batches
            num_samples = 0
            data = []
            preds = []

            # if an input or prediction batch could once not be converted to numpy arrays, it should also not be
            # possible for the remaining batches, so we only need to check this once.
            numpy_inputs = None
            numpy_predictions = None

            for batch in dataloader:
                # try to convert the batch to numpy arrays and append to the data list
                if numpy_inputs is not False:
                    try:
                        data.append(_convert_tensors_to_numpy(batch))
                        numpy_inputs = True
                    except TypeError:
                        data.append(batch)
                        numpy_inputs = False
                else:
                    data.append(batch)

                # move the batch to the correct device. This assumes that batch[0] contains the input features.
                inputs = self.model._apply_batch_transfer_handler(batch[0])

                # calculate the predictions for this batch.
                pred = self.model.predict_step(inputs)

                # check if the output is a structure of Tensors that can be converted to a structure of numpy arrays.
                # If not, e.g. if the output is a structure of torch.sparse.Tensors, use the predictions as they are.
                # This is only useful if the inputs can be expressed as numpy arrays.
                if numpy_inputs and numpy_predictions is not False:
                    try:
                        preds.append(_convert_tensors_to_numpy(pred))
                        numpy_predictions = True
                    except TypeError:
                        preds.append(pred)
                        numpy_predictions = False
                else:
                    preds.append(pred)
                    numpy_predictions = False

                # if the dataset cannot be consumed in a single batch, yield intermediate values
                if self.run_config.predict_batch_size != -1:
                    if self.run_config.conventional_batch_axis:
                        # remember how many samples were already consumed for this batch
                        num_samples += _get_batch_size(batch)

                        # check if enough samples were consumed to yield a batch
                        if num_samples >= self.run_config.predict_batch_size:
                            yield _get_batched_yield_values(data, preds, numpy_inputs, numpy_predictions)

                            # reset
                            num_samples = 0
                            data = []
                            preds = []
                    else:
                        # no conventional batch axis. Simply yield every batch individually.
                        yield _get_batched_yield_values(data, preds, numpy_inputs, numpy_predictions)

                        # reset
                        num_samples = 0
                        data = []
                        preds = []

            # yield the remaining predictions
            if self.run_config.predict_batch_size == -1 or num_samples > 0:
                yield _get_batched_yield_values(data, preds, numpy_inputs, numpy_predictions)

    def loss(
        self,
        data: Union[
            "tf.data.Dataset", tuple["tf.data.Dataset"], list["tf.data.Dataset"], "lightning.LightningDataModule"
        ],
    ) -> Union[float, tuple[float]]:
        """Calculates the loss for the provided arrays of targets and predictions using the loss function attached to the model.

        Which of the input parameters are necessary depends on the machine learning framework used:

        - Keras: The loss function is directly called using the targets and predictions, thus ``y_true`` and ``y_pred``
          are necessary, ``sample_weight`` is optionally used.
        - Lightning: No direct access to the loss function is possible, instead the ``Trainer`` is used to perform the
          evaluation. For this, the ``inputs`` and ``y_true`` are necessary, ``sample_weight`` is optionally used.

        Parameters
        ----------
        data : Union["tf.data.Dataset", tuple["tf.data.Dataset"], list["tf.data.Dataset"], "lightning.LightningDataModule"]
            _description_

        Returns
        -------
        Union[float, tuple[float]]
            The loss values.
        """
        if self.run_config.model_type == "Keras":
            if not isinstance(data, tuple) and not isinstance(data, list):
                data = [data]

            # check if the user has defined a function to get the loss
            if hasattr(self.run_config, "get_loss"):
                # no assumptions about the structure of the data and predictions are needed
                losses = []
                for dataset in data:
                    losses.append(
                        self.run_config.get_loss(
                            self.run_config, self.model_config, self.model, dataset, self.input_handler
                        )
                    )
            else:
                # here, we need to assume that the dataset yields tuples of length 2 or 3, and that batch[0] contains
                # the input features, batch[1] the target labels and batch[2] (if present) the sample weights
                @tf.function
                def _tensorflow_predict(inputs):
                    """_summary_.

                    Parameters
                    ----------
                    inputs : _type_
                        _description_

                    Returns
                    -------
                    _type_
                        _description_
                    """
                    return self.model(inputs, training=False)

                # check if the loss function accepts sample weights
                loss_accepts_weights = "sample_weight" in inspect.signature(self.model.loss).parameters

                # iterate over the datasets
                losses = []  # collects the final losses per dataset
                for dataset in data:
                    losses_it = []  # collects the losses per batch
                    for batch in dataset:
                        # get inputs, targets and optional sample weights
                        inputs = batch[0]
                        targets = batch[1]
                        if len(batch) > 2:
                            sample_weights = batch[2]
                        else:
                            sample_weights = None

                        # get the predictions
                        preds = _tensorflow_predict(inputs)

                        # check if the loss function accepts sample weights
                        if sample_weights is not None and loss_accepts_weights:
                            # calculate the loss and assume that sample weights are handled correctly
                            loss = self.model.loss(targets, preds, sample_weight=sample_weights).numpy()

                            # check if the reduction needs to be handled manually
                            if loss.shape == ():
                                losses_it.append(loss)
                            else:
                                losses_it.append(np.mean(loss))
                        else:
                            # calculate the loss value without sample weights
                            loss = self.model.loss(targets, preds).numpy()

                            # check if the reduction has already been applied
                            if loss.shape == ():
                                # since the loss has already been reduced, we cannot apply sample weights anymore, so
                                # use the loss as is
                                losses_it.append(loss)
                            else:
                                # reduction has not yet been applied, so we can apply sample weights if present
                                if sample_weights is not None:
                                    loss = sample_weights * loss

                                # average and add the loss
                                losses_it.append(np.mean(loss))

                    # average the losses over all batches in this dataset
                    losses.append(np.mean(losses_it))

            # return the list of losses
            if len(losses) == 1:
                return losses[0]
            else:
                return tuple(losses)

        elif self.run_config.model_type == "Lightning":
            # TODO: Doc string + typing!
            raise NotImplementedError
            # if y_true is None or inputs is None:
            #     raise ValueError("The input features `inputs` and target labels `y_true` need to be provided.")
            #
            # # wrap the numpy arrays in a dataloader
            # if sample_weight is None:
            #     dataset = OPTIMA.lightning.inputs.get_dataset(
            #         self.run_config, self.model.hparams.model_config, inputs, y_true
            #     )
            # else:
            #     dataset = OPTIMA.lightning.inputs.get_dataset(
            #         self.run_config, self.model.hparams.model_config, inputs, y_true, sample_weight
            #     )
            # dataloader = OPTIMA.lightning.inputs.get_dataloader(
            #     self.run_config, self.model.hparams.model_config, dataset
            # )
            #
            # # do the evaluation; this returns a list of dictionaries, one per dataloader used, i.e. one in this case.
            # loss = self.pl_trainer.validate(self.model, dataloader, verbose=False)[0].get("val_loss")
            #
            # # check if the validation loss was logged
            # if loss is None:
            #     raise RuntimeError(
            #         "To calculate the loss, the validation loss needs to log the loss value with key 'val_loss'!"
            #     )
            #
            # return loss

    def calc_native_metrics(
        self,
        native_metrics: Union[Any, list[Any]],
        data: Union[
            "tf.data.Dataset", tuple["tf.data.Dataset"], list["tf.data.Dataset"], "lightning.LightningDataModule"
        ],
        weighted: bool = True,
    ) -> Union[Union[int, float], list[Union[int, float]], tuple[list[Union[int, float]]]]:
        """Calculates the value of a list of native (stateful) metric for the provided targets and predictions.

        The type of metrics provided is assumed to correspond to the backend set in ``model_type`` in the `run-config`.
        This is not verified.

        Before and after the calculation, the state of the metrics is reset (if necessary).

        Parameters
        ----------
        native_metrics : Union[Any, list[Any]]
            The native metrics.
        data : Union["tf.data.Dataset", tuple["tf.data.Dataset"], list["tf.data.Dataset"], "lightning.LightningDataModule"]
            _description_
        weighted : bool
            If ``True``, the metric is provided with sample weights if they are available and if the metric accepts
            sample weights. (Default value = True)

        Returns
        -------
        Union[Union[int, float], list[Union[int, float]], tuple[list[Union[int, float]]]]
            The values of the native metrics.
        """
        if not isinstance(native_metrics, list):
            return_list = False
            native_metrics = [native_metrics]
        else:
            return_list = True

        if self.run_config.model_type == "Keras":
            # check if the user has defined a function to get the metric values
            if hasattr(self.run_config, "get_native_metric_values"):
                # no assumptions about the structure of the data and predictions are needed
                metric_values = []
                for dataset in data:
                    metric_values.append(
                        self.run_config.get_metric_values(
                            self.run_config, native_metrics, self.model_config, self.model, dataset, self.input_handler
                        )
                    )
            else:
                # here, we need to assume that the dataset yields tuples of length 2 or 3, and that batch[0] contains
                # the input features, batch[1] the target labels and batch[2] (if present) the sample weights
                @tf.function
                def _tensorflow_predict(inputs):
                    """_summary_.

                    Parameters
                    ----------
                    inputs : _type_
                        _description_

                    Returns
                    -------
                    _type_
                        _description_
                    """
                    return self.model(inputs, training=False)

                # check which metrics accept sample weights
                accepts_weights_list = [
                    "sample_weight" in inspect.signature(metric.update_state).parameters for metric in native_metrics
                ]

                # iterate over the datasets
                metric_values = []  # collects the metric values per dataset
                for dataset in data:
                    # reset the metrics
                    for metric in native_metrics:
                        metric.reset_state()

                    # iterate through the dataset
                    for batch in dataset:
                        # get inputs, targets and optional sample weights
                        inputs = batch[0]
                        targets = batch[1]
                        if len(batch) > 2:
                            sample_weights = batch[2]
                        else:
                            sample_weights = None

                        # get the predictions
                        preds = _tensorflow_predict(inputs)

                        # update the metrics
                        for metric, accepts_weights in zip(native_metrics, accepts_weights_list):
                            if accepts_weights and weighted:
                                metric.update_state(targets, preds, sample_weight=sample_weights)
                            else:
                                metric.update_state(targets, preds)

                    # get the metric values
                    metric_values_ds = [metric.result().numpy() for metric in native_metrics]
                    if return_list:
                        metric_values.append(metric_values_ds)
                    else:
                        metric_values.append(metric_values_ds[0])

                # reset the metric state before returning
                for metric in native_metrics:
                    metric.reset_state()

                if len(metric_values) == 1:
                    return metric_values[0]
                else:
                    return tuple(metric_values)
        elif self.run_config.model_type == "Lightning":
            # TODO: Doc string + typing!
            raise NotImplementedError
            # y_true = y_true.copy()
            # y_true_tensor = torch.from_numpy(y_true).type(torch.float)
            # y_pred_tensor = torch.from_numpy(y_pred).type(torch.float)
            # metric = native_metric(y_pred_tensor, y_true_tensor).cpu().detach().numpy()
            # return metric

    def calc_custom_metrics(
        self,
        custom_metrics: Union[Callable, tuple[Callable], list[Callable]],
        data: Optional[
            Union["tf.data.Dataset", tuple["tf.data.Dataset"], list["tf.data.Dataset"], "lightning.LightningDataModule"]
        ] = None,
        skip_test_dataset: bool = False,
    ) -> Union[
        Union[int, float, bool],
        tuple[Union[int, float, bool]],
        list[Union[int, float, bool]],
        tuple[list[Union[int, float, bool]]],
    ]:
        """Calculates the values of the `custom metrics` on the provided datasets.

        The predictions of the model are calculated in batches by calling ``self.batched_predict()``.

        Parameters
        ----------
        custom_metrics : Union[Callable, tuple[Callable], list[Callable]]
            The custom metrics whose values should be calculated.
        data : Optional[Union["tf.data.Dataset", tuple["tf.data.Dataset"], list["tf.data.Dataset"], "lightning.LightningDataModule"]]
            The datasets to be used to evaluate the custom metrics on. When using the Lightning backend, this may be
            ``None``, in which case the data module is taken from the lightning trainer provided to the constructor.
            (Default value = None)
        skip_test_dataset : bool
            Only used for Lightning. If ``False``, the metrics are evaluated on training, validation and testing data.
            If ``True``, the evaluation on the testing dataset is skipped. (Default value = False)

        Returns
        -------
        Union[Union[int, float, bool],tuple[Union[int, float, bool]],list[Union[int, float, bool]],tuple[list[Union[int, float, bool]]],]
            The values of the custom metrics on the provided datasets. If multiple metrics are provided, their values on
            each dataset are combined into a list, in the same order as in ``custom_metrics``. Otherwise, a single value
            is returned per dataset. If multiple datasets are provided, the corresponding custom metric values are
            combined in a tuple, with one entry per dataset. For Keras, the order corresponds to the order given in
            ``data``. For Lightning, the order (``train``, ``val``, ``test``) is used.
        """
        if not isinstance(custom_metrics, tuple) and not isinstance(custom_metrics, list):
            return_list = False
            custom_metrics = [custom_metrics]
        else:
            return_list = True

        if self.run_config.model_type == "Keras":
            if isinstance(data, tf.data.Dataset):
                data = [data]

            # loop over the datasets
            metric_values = []
            for d in data:
                # in case not all predictions can be held in memory, calculate the predictions in batches and later average the
                # custom metric values obtained for each batch
                temp_metric_values = [[] for _ in range(len(custom_metrics))]
                for batch, y_pred_batch in self.batched_predict(d):
                    for i, metric in enumerate(custom_metrics):
                        temp_metric_values[i].append(metric(batch, y_pred_batch))

                # average the metric values
                metric_values_ds = []
                for values in temp_metric_values:
                    metric_values_ds.append(np.average(values))

                # save the averaged metric values
                if return_list:
                    metric_values.append(metric_values_ds)
                else:
                    metric_values.append(metric_values_ds[0])

            if len(metric_values) == 1:
                return metric_values[0]
            else:
                return tuple(metric_values)

        elif self.run_config.model_type == "Lightning":
            # find out if testing data is available
            if not skip_test_dataset and hasattr(data, "test_dataloader"):
                target_datasets = ["train", "val", "test"]
            else:
                target_datasets = ["train", "val"]

            metric_values = []
            for stage in target_datasets:
                # in case not all predictions can be held in memory, calculate the predictions in batches and later average the
                # custom metric values obtained for each batch
                temp_metric_values = [[] for _ in range(len(custom_metrics))]
                for batch, y_pred_batch in self.batched_predict(data, stage=stage):
                    for i, metric in enumerate(custom_metrics):
                        temp_metric_values[i].append(metric(batch, y_pred_batch))

                # average the metric values
                metric_values_ds = []
                for values in temp_metric_values:
                    metric_values_ds.append(np.average(values))

                # save the averaged metric values
                if return_list:
                    metric_values.append(metric_values_ds)
                else:
                    metric_values.append(metric_values_ds[0])

            if len(metric_values) == 1:
                return metric_values[0]
            else:
                return tuple(metric_values)


def load_model(
    run_config: ModuleType,
    model_config: model_config_type,
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    path: str,
    cpus: int,
) -> AbstractModel:
    """Helper function that abstracts the model loading for different machine learning libraries.

    In addition to loading the model, the environment will also be configured to use the correct number of cpus and set
    automatic VRAM scaling by calling the ``configure_environment``-function.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported `run-config`-file.
    model_config : model_config_type
        Dictionary containing the values for each hyperparameter
    input_handler : OPTIMA.builtin.inputs.InputHandler
        Instance of the ``OPTIMA.builtin.inputs.InputHandler``-class
    path : str
        Path to the model to load. The following file extensions are assumed:
        - ``'.keras'``: Keras model
        - ``'.ckpt'``: Torch / Lightning-model
        If the provided path does not contain a file extension, the correct extension will be inferred from the
        ``model_type`` setting in the `run_config` and appended to the file path.
    cpus : int
        The number of cpu cores available for this instance.

    Returns
    -------
    AbstractModel
        The reloaded model wrapped in an ``AbstractModel`` instance.
    """
    # configure the environment
    if run_config.model_type == "Keras":
        # for Keras, this means specifying some settings to Tensorflow
        configure_environment(run_config, cpus)
    if run_config.model_type == "Lightning":
        # for Lightning, this means getting a Trainer with the correct settings
        pl_trainer = configure_environment(run_config, cpus)

    if run_config.model_type == "Keras":
        if path[-6:] != ".keras":
            path += ".keras"
        return AbstractModel(
            run_config=run_config,
            model=tf.keras.models.load_model(path),
            model_config=model_config,
            input_handler=input_handler,
        )
    elif run_config.model_type == "Lightning":
        if path[-5:] != ".ckpt":
            path += ".ckpt"
        return AbstractModel(
            run_config=run_config,
            model=run_config.LitModel.load_from_checkpoint(path),
            model_config=model_config,
            input_handler=input_handler,
            pl_trainer=pl_trainer,
        )
    # elif run_config.model_type == "Torch":
    #     if path[-5:] != ".ckpt":
    #         path += ".ckpt"
    #     ...


def configure_environment(run_config: ModuleType, cpus: int) -> None:
    """Helper function that abstracts away the configuration of the machine learning library.

    It sets the number of CPU cores to use to the provided ``cpus`` value, and enables automatic VRAM scaling for `Keras`.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported `run-config`-file.
    cpus : int
        The number of cpu cores available for this instance.
    """
    if run_config.model_type == "Keras":
        from tensorflow import config as tf_config

        try:
            # set automatic scaling of the VRAM allocation
            gpus = tf_config.experimental.list_physical_devices("GPU")
            for gpu in gpus:
                tf_config.experimental.set_memory_growth(gpu, True)

            # reduce number of threads
            tf_config.threading.set_inter_op_parallelism_threads(min(cpus, 2))
            tf_config.threading.set_intra_op_parallelism_threads(cpus)
        except RuntimeError:
            pass
    elif run_config.model_type == "Lightning":
        # set correct number of cpu cores; TODO: this for some reason currently only works with pytorch-gpu and is ignored by pytorch??
        from torch import get_num_threads, get_num_interop_threads, set_num_threads, set_num_interop_threads

        if get_num_threads() != cpus:
            set_num_threads(cpus)
        if get_num_interop_threads() != min(cpus, 2):
            set_num_interop_threads(min(cpus, 2))
        pl_trainer = lightning.Trainer(
            devices="auto",
            accelerator="auto",
            enable_progress_bar=False,
            logger=False,  # we don't need logging here
            enable_checkpointing=False,  # also disable checkpointing
        )
        return pl_trainer


def is_model(
    run_config: ModuleType,
    model_config: model_config_type,
    input_handler: OPTIMA.builtin.inputs.InputHandler,
    path: str
) -> bool:
    """Helper function that checks if a path corresponds to a model file.

    The file ending is automatically appended based on the machine learning framework used, i.e. ``'.keras'`` for `Keras`
    and ``'.ckpt'`` for `Lightning`.

    Parameters
    ----------
    run_config : ModuleType
        Reference to the imported `run-config`-file.
    path : str
        Path to the suspected model file.

    Returns
    -------
    bool
        ``True`` if the provided path corresponds to a valid model file, ``False`` otherwise.
    """
    # add the file ending
    if run_config.model_type == "Keras":
        if path[-6:] != ".keras":
            path += ".keras"
    elif run_config.model_type == "Lightning":
        if path[-5:] != ".ckpt":
            path += ".ckpt"

    # try to load the model
    def _check_model_path(
        run_config: ModuleType,
        model_config: model_config_type,
        input_handler: OPTIMA.builtin.inputs.InputHandler,
        path: str,
        mp_queue: mp.Queue
    ) -> None:
        """Helper function that calls the ``load_model`` function.

        It is expected to be executed in a subprocess. The communication to the parent process is done using the provided
        queue. A queue value of ``True`` indicates the loading was successful, a value of ``False`` indicates the loading
        failed.

        Parameters
        ----------
        run_config : ModuleType
            Reference to the imported `run-config`-file.
        path : str
            Path to the suspected model file.
        mp_queue : mp.Queue
            Multiprocessing queue for the communication to the parent process.
        """
        try:
            load_model(run_config, model_config, input_handler, path, cpus=1)
            mp_queue.put(True)
        except BaseException:  # noqa: B036
            # something happened during loading, assume it's not a valid model file
            mp_queue.put(False)

    # start the subprocess and try to load the model
    queue = mp.Queue()
    p = mp.Process(target=_check_model_path, args=(run_config, model_config, input_handler, path, queue))
    p.daemon = True
    p.start()
    success = queue.get()
    return success
