# -*- coding: utf-8 -*-
"""Collection of unit tests related to the loading, splitting and preprocessing of the input data; both core and built-in."""
import os
from functools import partial

import numpy as np

import pytest
import ray

from .context import inputs, builtin_inputs
from . import config as run_config


def get_input_handler():
    return builtin_inputs.InputHandler(run_config)


def test_input_handler():
    # get the input handler
    input_handler = get_input_handler()
    assert input_handler.get_vars() == run_config.input_vars
    for var, scaling in input_handler.get_nonlinear_scaling().items():
        assert scaling == run_config.input_scaling[var]

    # set a subset of input variables,
    small_var_set = run_config.input_vars[:5]
    input_handler.set_vars(small_var_set)
    assert input_handler.get_vars() == small_var_set
    for var, scaling in input_handler.get_nonlinear_scaling().items():
        assert scaling == run_config.input_scaling[var]

    # test the copy
    input_handler_copy = input_handler.copy()
    assert input_handler.get_vars() == input_handler_copy.get_vars()
    assert input_handler.get_nonlinear_scaling() == input_handler_copy.get_nonlinear_scaling()


def test_dummy_scaler():
    # get a dummy scaler
    dummy_scaler = builtin_inputs.DummyScaler()
    pseudo_data = np.array([1, 2, 3, 4])
    pseudo_weights = np.ones((4,))
    dummy_scaler.fit(pseudo_data, sample_weight=pseudo_weights)
    assert (pseudo_data == dummy_scaler.transform(pseudo_data)).all()


def test_manual_scaler():
    input_handler = get_input_handler()
    manual_scaler = builtin_inputs.ManualScaler(input_handler)

    assert len(input_handler.get_vars()) == 13
    pseudo_data = np.array([[1000., 1., 0., 100., 0., 1., 10., -2., 1., 1., 1., 100., -2.]])
    pseudo_weights = np.ones((1,))
    manual_scaler.fit(pseudo_data, sample_weight=pseudo_weights)
    assert (manual_scaler.transform(pseudo_data) == np.array([[3., 1., 0., 2., 0, 1., 1., -2., 0., 1., 1., 2., -2.]])).all()


def test_custom_manual_plus_standard_scaler():
    input_handler = get_input_handler()
    scaler = builtin_inputs.CustomManualPlusStandardScaler(input_handler)

    # constant values should be shifted to zero
    pseudo_data = np.array(3 * [[1000., 1., 0., 100., 0., 1., 10., -2., 1., 1., 1., 100., -2.]])
    pseudo_weights = np.ones((3,))
    scaler.fit(pseudo_data, sample_weight=pseudo_weights)
    scaled_pseudo_data = np.array(3*[[0., 0., 0., 0., 0, 0., 0., 0., 0., 0., 0., 0., 0.]])
    assert (scaler.transform(pseudo_data) == scaled_pseudo_data).all()

    # now with simple pseudo data
    pseudo_data = np.array(
        [
            [1000., 2., -2., 1000., 0., 0., 1000., 2., 10., 2., -2., 10., 0.],
            [100., 1., -1., 100., 1., 1., 100., 1., 100., 1., -1., 100., -1.],
            [10., 0., 0., 10., 2., 2., 10., 0., 1000., 0., 0., 1000., -2.],
        ]
    )
    x = np.sqrt(3 / 2)
    scaled_pseudo_data = np.array(
        [
            [x, x, -x, x, -x, -x, x, x, -x, x, -x, -x, x],
            [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
            [-x, -x, x, -x, x, x, -x, -x, x, -x, x, x, -x],
        ]
    )
    scaler.fit(pseudo_data, sample_weight=pseudo_weights)
    assert (scaler.transform(pseudo_data) == scaled_pseudo_data).all()

    # test sample weights
    pseudo_weights = np.array([1., 1., 0])
    scaled_pseudo_data = np.array(
        [
            [1, 1, -1, 1, -1, -1, 1, 1, -1, 1, -1, -1, 1],
            [-1, -1, 1, -1, 1, 1, -1, -1, 1, -1, 1, 1, -1],
            [-3, -3, 3, -3, 3, 3, -3, -3, 3, -3, 3, 3, -3],
        ]
    )
    scaler.fit(pseudo_data, sample_weight=pseudo_weights)
    assert (scaler.transform(pseudo_data) == scaled_pseudo_data).all()

    # test saving and reloading
    scaler_path = "temp_scaler.pickle"
    scaler.save(scaler_path)
    del scaler
    with pytest.raises(UnboundLocalError):
        scaler.transform(pseudo_data)
    scaler = builtin_inputs.CustomManualPlusStandardScaler(input_handler)
    with pytest.raises(AssertionError):
        scaler.transform(pseudo_data)
    scaler.load(scaler_path)
    assert (scaler.transform(pseudo_data) == scaled_pseudo_data).all()
    os.remove("temp_scaler.pickle")


def test_load_input_data():
    input_handler = get_input_handler()

    # load test dataset of 10000 events, 5000 signal and 5000 background. 13 input variables are set in test config.
    dataset = builtin_inputs.get_inputs(run_config,
                                        nevts=run_config.max_num_events,
                                        input_vars_list=input_handler.get_vars()).take_batch(batch_size=10000)
    inputs = dataset["Input"]
    targets = dataset["Target"]
    normalized_weights = dataset["Weight"]
    weights = dataset["ScaledWeight"]
    event_nums = dataset["EventNumber"]

    # verify shapes
    nevents = 10000
    assert inputs.shape == (nevents, 13)
    assert targets.shape == (nevents, 1)
    assert weights.shape == (nevents,)
    assert normalized_weights.shape == (nevents,)
    assert event_nums.shape == (nevents,)

    # verify first few entries
    assert np.max(inputs[:2, :2] - np.array([[118.25695, 1.89344], [153.33139, 3.37611]])) < 1e-5
    assert (targets[:5, 0] == np.array([0., 1., 1., 1., 1.])).all()
    assert np.max(weights[:5] - np.array([3.34210e-4, 1.26920e-4, 1.10627e-4, 9.5176e-5, 1.11107e-4])) < 1e-9
    assert np.max(normalized_weights[:5] - np.array([0.916951, 1.23007,  1.07217,  0.92242,  1.07682])) < 1e-5
    assert (event_nums[:5] == np.array([2146094, 1273346, 3395091, 855136, 2947049])).all()

    # verify nevts
    nevents_list = [10000, 30, (5000, 5000), (30, 30), (30, 10)]
    for nevents in nevents_list:
        dataset = builtin_inputs.get_inputs(run_config,
                                            nevts=nevents,
                                            input_vars_list=input_handler.get_vars()).take_batch(batch_size=10000)
        inputs = dataset["Input"]
        targets = dataset["Target"]
        normalized_weights = dataset["Weight"]
        weights = dataset["ScaledWeight"]
        event_nums = dataset["EventNumber"]

        if isinstance(nevents, int):
            num = nevents
        else:
            num = nevents[0] + nevents[1]
        assert inputs.shape == (num, 13)
        assert targets.shape == (num, 1)
        assert weights.shape == (num,)
        assert normalized_weights.shape == (num,)
        assert event_nums.shape == (num,)

        if isinstance(nevents, tuple):
            for i in range(2):
                assert inputs[targets[:, 0] == i].shape == (nevents[1-i], 13)
                assert targets[targets[:, 0] == i].shape == (nevents[1-i], 1)
                assert weights[targets[:, 0] == i].shape == (nevents[1-i],)
                assert normalized_weights[targets[:, 0] == i].shape == (nevents[1-i],)
                assert event_nums[targets[:, 0] == i].shape == (nevents[1-i],)

    # verify input variables
    nevents = 10000
    dataset = builtin_inputs.get_inputs(run_config,
                                        nevts=run_config.max_num_events,
                                        input_vars_list=run_config.input_vars[:5]).take_batch(batch_size=10000)
    inputs = dataset["Input"]
    targets = dataset["Target"]
    normalized_weights = dataset["Weight"]
    weights = dataset["ScaledWeight"]
    event_nums = dataset["EventNumber"]

    # verify shapes
    assert inputs.shape == (nevents, 5)
    assert targets.shape == (nevents, 1)
    assert weights.shape == (nevents,)
    assert normalized_weights.shape == (nevents,)
    assert event_nums.shape == (nevents,)

    # verify first few entries
    assert np.max(inputs[:2, :2] - np.array([[118.25695, 1.89344], [153.33139, 3.37611]])) < 1e-5
    assert (targets[:5, 0] == np.array([0., 1., 1., 1., 1.])).all()
    assert np.max(weights[:5] - np.array([3.34210e-4, 1.26920e-4, 1.10627e-4, 9.5176e-5, 1.11107e-4])) < 1e-9
    assert np.max(normalized_weights[:5] - np.array([0.916951, 1.23007, 1.07217, 0.92242, 1.07682])) < 1e-5
    assert (event_nums[:5] == np.array([2146094, 1273346, 3395091, 855136, 2947049])).all()

    # verify max event weight
    # for 1.1, two of 20 events are duplicated
    run_config.max_event_weight = 1.1
    dataset = builtin_inputs.get_inputs(run_config,
                                        nevts=20,
                                        input_vars_list=run_config.input_vars).take_batch(batch_size=10000)
    inputs = dataset["Input"]
    targets = dataset["Target"]
    normalized_weights = dataset["Weight"]
    weights = dataset["ScaledWeight"]
    event_nums = dataset["EventNumber"]

    run_config.max_event_weight = np.inf
    assert inputs.shape == (22, 13)
    assert targets.shape == (22, 1)
    assert weights.shape == (22,)
    assert normalized_weights.shape == (22,)
    assert event_nums.shape == (22,)

    # total weight (not normalized weight!) should be unchanged
    dataset = builtin_inputs.get_inputs(run_config,
                                        nevts=run_config.max_num_events,
                                        input_vars_list=run_config.input_vars).take_batch(10000)
    total_weight_no_duplication = np.sum(dataset["ScaledWeight"])
    run_config.max_event_weight = 1.3
    dataset = builtin_inputs.get_inputs(run_config,
                                        nevts=run_config.max_num_events,
                                        input_vars_list=run_config.input_vars).take_batch(10000)
    run_config.max_event_weight = np.inf
    assert np.sum(dataset["ScaledWeight"]) - total_weight_no_duplication < 1e-8


def test_get_training_data():
    # TODO: add more thorough checks if random splitting is correct, i.e. no overlap between train, val and test + KFold
    #       is doing what it is expected to do

    # set a flag that ensures that Ray data keeps the order of items in the dataset consistent
    ray.data.context.DatasetContext.get_current().execution_options.preserve_order = True

    input_handler = get_input_handler()

    # load test dataset of 10000 events, 5000 signal and 5000 background. 13 input variables are set in test config.
    dataset = builtin_inputs.get_inputs(run_config,
                                        nevts=run_config.max_num_events,
                                        input_vars_list=input_handler.get_vars())
    dataset_numpy = dataset.take_batch(dataset.count())
    input_data = dataset_numpy["Input"]
    targets = dataset_numpy["Target"]
    normalized_weights = dataset_numpy["Weight"]
    weights = dataset_numpy["ScaledWeight"]
    event_nums = dataset_numpy["EventNumber"]

    # randomly split into training and validation data
    dataset_split = builtin_inputs.get_training_data(dataset, splitting_cond=0.2, shuffle=False)

    # check splitting
    assert len(dataset_split) == 2
    assert dataset_split[0].count() == 8000
    assert dataset_split[1].count() == 2000

    # randomly split into training, validation and testing data
    dataset_split = builtin_inputs.get_training_data(dataset, splitting_cond=(0.2, 0.1), shuffle=False)

    # check splitting
    assert len(dataset_split) == 3
    assert dataset_split[0].count() == 7000
    assert dataset_split[1].count() == 1000
    assert dataset_split[2].count() == 2000

    # split into training and validation using custom splitting condition
    val_condition = lambda x: ((x+1) % 3) == 0
    test_condition = lambda x: (x % 3) == 0
    dataset_split = builtin_inputs.get_training_data(dataset, splitting_cond=test_condition, shuffle=False)
    # dataset_split = [d.materialize() for d in dataset_split]
    dataset_split_numpy = [d.take_batch(d.count()) for d in dataset_split]
    inputs_split = [d["Input"] for d in dataset_split_numpy]
    targets_split = [d["Target"] for d in dataset_split_numpy]
    normalized_weights_split = [d["Weight"] for d in dataset_split_numpy]
    weights_split = [d["ScaledWeight"] for d in dataset_split_numpy]

    # check splitting
    exp_train = np.logical_not(test_condition(event_nums))
    exp_val = test_condition(event_nums)
    assert len(dataset_split) == 2

    # check correct event assignment
    assert (input_data[exp_train, :] == inputs_split[0]).all()
    assert (targets[exp_train, :] == targets_split[0]).all()
    assert (weights[exp_train] == weights_split[0]).all()
    assert (normalized_weights[exp_train] == normalized_weights_split[0]).all()
    assert (input_data[exp_val, :] == inputs_split[1]).all()
    assert (targets[exp_val, :] == targets_split[1]).all()
    assert (weights[exp_val] == weights_split[1]).all()
    assert (normalized_weights[exp_val] == normalized_weights_split[1]).all()

    # split into training, validation and testing using custom splitting condition
    dataset_split = builtin_inputs.get_training_data(dataset, splitting_cond=(test_condition, val_condition), shuffle=False)
    dataset_split = [d.materialize() for d in dataset_split]
    dataset_split_numpy = [d.take_batch(d.count()) for d in dataset_split]
    inputs_split = [d["Input"] for d in dataset_split_numpy]
    targets_split = [d["Target"] for d in dataset_split_numpy]
    normalized_weights_split = [d["Weight"] for d in dataset_split_numpy]
    weights_split = [d["ScaledWeight"] for d in dataset_split_numpy]

    # check splitting
    exp_train = np.logical_not(test_condition(event_nums) + val_condition(event_nums))
    exp_val = val_condition(event_nums)
    exp_test = test_condition(event_nums)
    assert len(dataset_split) == 3

    # check correct event assignment
    assert (input_data[exp_train, :] == inputs_split[0]).all()
    assert (targets[exp_train, :] == targets_split[0]).all()
    assert (weights[exp_train] == weights_split[0]).all()
    assert (normalized_weights[exp_train] == normalized_weights_split[0]).all()
    assert (input_data[exp_val, :] == inputs_split[1]).all()
    assert (targets[exp_val, :] == targets_split[1]).all()
    assert (weights[exp_val] == weights_split[1]).all()
    assert (normalized_weights[exp_val] == normalized_weights_split[1]).all()
    assert (input_data[exp_test, :] == inputs_split[2]).all()
    assert (targets[exp_test, :] == targets_split[2]).all()
    assert (weights[exp_test] == weights_split[2]).all()
    assert (normalized_weights[exp_test] == normalized_weights_split[2]).all()

    # test k-fold for sklearn train/val splitting
    dataset_split = builtin_inputs.get_training_data(dataset, splitting_cond=0.2, do_kfold=True, shuffle=False)

    # check splitting
    assert len(dataset_split) == 2

    # check folds
    for i_fold in range(5):
        dataset_split_i = [d[i_fold].materialize() for d in dataset_split]
        dataset_split_numpy_i = [d.take_batch(d.count()) for d in dataset_split_i]
        inputs_split_i = [d["Input"] for d in dataset_split_numpy_i]
        targets_split_i = [d["Target"] for d in dataset_split_numpy_i]
        normalized_weights_split_i = [d["Weight"] for d in dataset_split_numpy_i]
        weights_split_i = [d["ScaledWeight"] for d in dataset_split_numpy_i]

        # check event assignment
        # validation datasets
        assert (inputs_split_i[1] == input_data[2000 * i_fold:2000 * (i_fold + 1)]).all()
        assert (targets_split_i[1] == targets[2000 * i_fold:2000 * (i_fold + 1)]).all()
        assert (weights_split_i[1] == weights[2000 * i_fold:2000 * (i_fold + 1)]).all()
        assert (normalized_weights_split_i[1] == normalized_weights[2000 * i_fold:2000 * (i_fold + 1)]).all()

        # training datasets
        assert (inputs_split_i[0] == np.concatenate((input_data[:2000 * i_fold], input_data[2000 * (i_fold + 1):]))).all()
        assert (targets_split_i[0] == np.concatenate((targets[:2000 * i_fold], targets[2000 * (i_fold + 1):]))).all()
        assert (weights_split_i[0] == np.concatenate((weights[:2000 * i_fold], weights[2000 * (i_fold + 1):]))).all()
        assert (normalized_weights_split_i[0] == np.concatenate((normalized_weights[:2000 * i_fold], normalized_weights[2000 * (i_fold + 1):]))).all()

    # test k-fold for sklearn train/val/test splitting
    dataset_split = builtin_inputs.get_training_data(dataset, splitting_cond=(0.2, 0.2), do_kfold=True, shuffle=False)

    # check splitting
    assert len(dataset_split) == 3

    # check folds; testing dataset is split randomly, thus event assignment can only be checked by concatenating training and
    # validation sets
    dataset_split = [[d[i].materialize() for i in range(4)] for d in dataset_split]
    dataset_split_numpy = [[d[i].take_batch(d[i].count()) for i in range(4)] for d in dataset_split]
    inputs_split = [[d[i]["Input"] for i in range(4)] for d in dataset_split_numpy]
    targets_split = [[d[i]["Target"] for i in range(4)] for d in dataset_split_numpy]
    normalized_weights_split = [[d[i]["Weight"] for i in range(4)] for d in dataset_split_numpy]
    weights_split = [[d[i]["ScaledWeight"] for i in range(4)] for d in dataset_split_numpy]
    for i_fold in range(4):
        # check event assignments; the inputs are not expected to be identical due to the
        # different scalers
        assert (np.concatenate((inputs_split[1][0], inputs_split[0][0])) ==
                np.concatenate((inputs_split[0][i_fold][:2000 * i_fold], inputs_split[1][i_fold], inputs_split[0][i_fold][2000 * i_fold:]))).all
        assert (np.concatenate((targets_split[1][0], targets_split[0][0])) ==
                np.concatenate((targets_split[0][i_fold][:2000 * i_fold], targets_split[1][i_fold], targets_split[0][i_fold][2000 * i_fold:]))).all()
        assert (np.concatenate((weights_split[1][0], weights_split[0][0])) ==
                np.concatenate((weights_split[0][i_fold][:2000 * i_fold], weights_split[1][i_fold], weights_split[0][i_fold][2000 * i_fold:]))).all()
        assert (np.concatenate((normalized_weights_split[1][0], normalized_weights_split[0][0])) ==
                np.concatenate((normalized_weights_split[0][i_fold][:2000 * i_fold], normalized_weights_split[1][i_fold], normalized_weights_split[0][i_fold][2000 * i_fold:]))).all()

        # verify that test set is the same for all folds; the inputs are not expected to be identical due to the
        # different scalers
        assert np.max(np.abs(inputs_split[2][i_fold] - inputs_split[2][0])) < 0.06
        assert (np.abs(targets_split[2][i_fold] == targets_split[2][0])).all()
        assert (np.abs(weights_split[2][i_fold] == weights_split[2][0])).all()
        assert (np.abs(normalized_weights_split[2][i_fold] == normalized_weights_split[2][0])).all()

    # test k-fold for random train/val/test splitting with fixed_test_dataset == False
    dataset_split = builtin_inputs.get_training_data(
        dataset,
        splitting_cond=(0.2, 0.2),
        do_kfold=True,
        fixed_test_dataset=False,
        shuffle = False
    )

    # check splitting
    assert len(dataset_split) == 3

    # check folds
    dataset_split = [[d[i].materialize() for i in range(5)] for d in dataset_split]
    dataset_split_numpy = [[d[i].take_batch(d[i].count()) for i in range(5)] for d in dataset_split]
    inputs_split = [[d[i]["Input"] for i in range(5)] for d in dataset_split_numpy]
    targets_split = [[d[i]["Target"] for i in range(5)] for d in dataset_split_numpy]
    normalized_weights_split = [[d[i]["Weight"] for i in range(5)] for d in dataset_split_numpy]
    weights_split = [[d[i]["ScaledWeight"] for i in range(5)] for d in dataset_split_numpy]
    for i_fold in range(5):
        # check event assignment
        # training datasets
        if i_fold != 4:
            assert (inputs_split[0][i_fold] == np.concatenate((input_data[:2000 * i_fold], input_data[2000 * (i_fold + 2):]))).all()
            assert (targets_split[0][i_fold] == np.concatenate((targets[:2000 * i_fold], targets[2000 * (i_fold + 2):]))).all()
            assert (weights_split[0][i_fold] == np.concatenate((weights[:2000 * i_fold], weights[2000 * (i_fold + 2):]))).all()
            assert (normalized_weights_split[0][i_fold] == np.concatenate((normalized_weights[:2000 * i_fold], normalized_weights[2000 * (i_fold + 2):]))).all()
        else:
            assert (inputs_split[0][i_fold] == input_data[2000:8000]).all()
            assert (targets_split[0][i_fold] == targets[2000:8000]).all()
            assert (weights_split[0][i_fold] == weights[2000:8000]).all()
            assert (normalized_weights_split[0][i_fold] == normalized_weights[2000:8000]).all()

        # validation datasets
        assert np.max(inputs_split[1][i_fold] - inputs_split[2][(i_fold+1) % 5] < 0.04)
        assert (targets_split[1][i_fold] == targets_split[2][(i_fold+1) % 5]).all()
        assert (weights_split[1][i_fold] == weights_split[2][(i_fold+1) % 5]).all()
        assert (normalized_weights_split[1][i_fold] == normalized_weights_split[2][(i_fold+1) % 5]).all()

        # testing datasets
        assert (inputs_split[2][i_fold] == input_data[2000 * i_fold:2000 * (i_fold + 1)]).all()
        assert (targets_split[2][i_fold] == targets[2000 * i_fold:2000 * (i_fold + 1)]).all()
        assert (weights_split[2][i_fold] == weights[2000 * i_fold:2000 * (i_fold + 1)]).all()
        assert (normalized_weights_split[2][i_fold] == normalized_weights[2000 * i_fold:2000 * (i_fold + 1)]).all()

    # now test with custom splitting conditions
    val_condition = partial(inputs._event_nums_splitting_cond_kfold, run_config=run_config, split='val', use_testing_set=False)
    val_withTest_condition = partial(inputs._event_nums_splitting_cond_kfold, run_config=run_config, split='val', use_testing_set=True)
    test_condition = partial(inputs._event_nums_splitting_cond_kfold, run_config=run_config, split='test', use_testing_set=True)
    val_withVariableTest_condition = partial(inputs._event_nums_splitting_cond_kfold, run_config=run_config, split='val', use_testing_set=True, fixed_testing_set=False)
    variableTest_condition = partial(inputs._event_nums_splitting_cond_kfold, run_config=run_config, split='test', use_testing_set=True, fixed_testing_set=False)

    # test train/val splitting
    dataset_split = builtin_inputs.get_training_data(dataset, splitting_cond=val_condition, do_kfold=True, shuffle = False)

    # check splitting
    assert len(dataset_split) == 2

    # check folds
    exp_train = np.logical_not(val_condition(event_nums))
    exp_val = val_condition(event_nums)
    for i_fold in range(5):
        dataset_split_i = [d[i_fold].materialize() for d in dataset_split]
        dataset_split_numpy_i = [d.take_batch(d.count()) for d in dataset_split_i]
        inputs_split_i = [d["Input"] for d in dataset_split_numpy_i]
        targets_split_i = [d["Target"] for d in dataset_split_numpy_i]
        normalized_weights_split_i = [d["Weight"] for d in dataset_split_numpy_i]
        weights_split_i = [d["ScaledWeight"] for d in dataset_split_numpy_i]

        # check correct event assignment
        assert (input_data[exp_train[i_fold], :] == inputs_split_i[0]).all()
        assert (targets[exp_train[i_fold], :] == targets_split_i[0]).all()
        assert (weights[exp_train[i_fold]] == weights_split_i[0]).all()
        assert (normalized_weights[exp_train[i_fold]] == normalized_weights_split_i[0]).all()
        assert (input_data[exp_val[i_fold], :] == inputs_split_i[1]).all()
        assert (targets[exp_val[i_fold], :] == targets_split_i[1]).all()
        assert (weights[exp_val[i_fold]] == weights_split_i[1]).all()
        assert (normalized_weights[exp_val[i_fold]] == normalized_weights_split_i[1]).all()

    # now train/val/test splitting
    dataset_split = builtin_inputs.get_training_data(
        dataset,
        splitting_cond=(test_condition, val_withTest_condition),
        do_kfold=True,
        shuffle=False
    )

    # check splitting
    assert len(dataset_split) == 3

    # check folds
    exp_train = np.logical_not(np.logical_or(val_withTest_condition(event_nums), test_condition(event_nums)))
    exp_val = val_withTest_condition(event_nums)
    exp_test = test_condition(event_nums)
    for i_fold in range(4):
        dataset_split_i = [d[i_fold].materialize() for d in dataset_split]
        dataset_split_numpy_i = [d.take_batch(d.count()) for d in dataset_split_i]
        inputs_split_i = [d["Input"] for d in dataset_split_numpy_i]
        targets_split_i = [d["Target"] for d in dataset_split_numpy_i]
        normalized_weights_split_i = [d["Weight"] for d in dataset_split_numpy_i]
        weights_split_i = [d["ScaledWeight"] for d in dataset_split_numpy_i]

        # check correct event assignment
        assert (input_data[exp_train[i_fold], :] == inputs_split_i[0]).all()
        assert (targets[exp_train[i_fold], :] == targets_split_i[0]).all()
        assert (weights[exp_train[i_fold]] == weights_split_i[0]).all()
        assert (normalized_weights[exp_train[i_fold]] == normalized_weights_split_i[0]).all()
        assert (input_data[exp_val[i_fold], :] == inputs_split_i[1]).all()
        assert (targets[exp_val[i_fold], :] == targets_split_i[1]).all()
        assert (weights[exp_val[i_fold]] == weights_split_i[1]).all()
        assert (normalized_weights[exp_val[i_fold]] == normalized_weights_split_i[1]).all()
        assert (input_data[exp_test[i_fold], :] == inputs_split_i[2]).all()
        assert (targets[exp_test[i_fold], :] == targets_split_i[2]).all()
        assert (weights[exp_test[i_fold]] == weights_split_i[2]).all()
        assert (normalized_weights[exp_test[i_fold]] == normalized_weights_split_i[2]).all()

    # train/val/test splitting with NOT fixed testing set
    dataset_split = builtin_inputs.get_training_data(
        dataset,
        splitting_cond=(variableTest_condition, val_withVariableTest_condition),
        do_kfold=True,
        shuffle=False
    )

    # check splitting
    assert len(dataset_split) == 3

    # check folds
    exp_train = np.logical_not(np.logical_or(val_withVariableTest_condition(event_nums), variableTest_condition(event_nums)))
    exp_val = val_withVariableTest_condition(event_nums)
    exp_test = variableTest_condition(event_nums)
    for i_fold in range(5):
        dataset_split_i = [d[i_fold].materialize() for d in dataset_split]
        dataset_split_numpy_i = [d.take_batch(d.count()) for d in dataset_split_i]
        inputs_split_i = [d["Input"] for d in dataset_split_numpy_i]
        targets_split_i = [d["Target"] for d in dataset_split_numpy_i]
        normalized_weights_split_i = [d["Weight"] for d in dataset_split_numpy_i]
        weights_split_i = [d["ScaledWeight"] for d in dataset_split_numpy_i]

        # check correct event assignment
        assert (input_data[exp_train[i_fold], :] == inputs_split_i[0]).all()
        assert (targets[exp_train[i_fold], :] == targets_split_i[0]).all()
        assert (weights[exp_train[i_fold]] == weights_split_i[0]).all()
        assert (normalized_weights[exp_train[i_fold]] == normalized_weights_split_i[0]).all()
        assert (input_data[exp_val[i_fold], :] == inputs_split_i[1]).all()
        assert (targets[exp_val[i_fold], :] == targets_split_i[1]).all()
        assert (weights[exp_val[i_fold]] == weights_split_i[1]).all()
        assert (normalized_weights[exp_val[i_fold]] == normalized_weights_split_i[1]).all()
        assert (input_data[exp_test[i_fold], :] == inputs_split_i[2]).all()
        assert (targets[exp_test[i_fold], :] == targets_split_i[2]).all()
        assert (weights[exp_test[i_fold]] == weights_split_i[2]).all()
        assert (normalized_weights[exp_test[i_fold]] == normalized_weights_split_i[2]).all()


def test_custom_splitting_cond_kfold():
    condition_list_val = inputs._event_nums_splitting_cond_kfold(
        np.array([1, 2, 3, 4, 5, 6, 7]),
        run_config,
        split='val',
        use_testing_set=False
    )
    condition_list_val_withTest = inputs._event_nums_splitting_cond_kfold(
        np.array([1, 2, 3, 4, 5, 6, 7]),
        run_config,
        split='val',
        use_testing_set=True
    )
    condition_list_test = inputs._event_nums_splitting_cond_kfold(
        np.array([1, 2, 3, 4, 5, 6, 7]),
        run_config,
        split='test',
        use_testing_set=True
    )
    condition_list_val_withVariableTest = inputs._event_nums_splitting_cond_kfold(
        np.array([1, 2, 3, 4, 5, 6, 7]),
        run_config,
        split='val',
        use_testing_set=True,
        fixed_testing_set=False
    )
    condition_list_variableTest = inputs._event_nums_splitting_cond_kfold(
        np.array([1, 2, 3, 4, 5, 6, 7]),
        run_config,
        split='test',
        use_testing_set=True,
        fixed_testing_set=False
    )
    condition_list_val_exp = np.array(
        [
            [False, False, False, False, True, False, False],
            [True, False, False, False, False, True, False],
            [False, True, False, False, False, False, True],
            [False, False, True, False, False, False, False],
            [False, False, False, True, False, False, False],
        ]
    )
    condition_list_val_withTest_exp = np.array(
        np.array(
            [
                [False, False, False, False, True, False, False],
                [True, False, False, False, False, True, False],
                [False, True, False, False, False, False, True],
                [False, False, True, False, False, False, False],
            ]
        )
    )
    condition_list_test_exp = np.array(
        np.array(
            [
                [False, False, False, True, False, False, False],
                [False, False, False, True, False, False, False],
                [False, False, False, True, False, False, False],
                [False, False, False, True, False, False, False],
            ]
        )
    )
    condition_list_variableTest_exp = np.array(
        np.array(
            [
                [False, False, False, True, False, False, False],
                [False, False, False, False, True, False, False],
                [True, False, False, False, False, True, False],
                [False, True, False, False, False, False, True],
                [False, False, True, False, False, False, False],
            ]
        )
    )
    assert (condition_list_val == condition_list_val_exp).all()
    assert (condition_list_val_withTest == condition_list_val_withTest_exp).all()
    assert (condition_list_test == condition_list_test_exp).all()
    assert (condition_list_val_withVariableTest == condition_list_val_exp).all()
    assert (condition_list_variableTest == condition_list_variableTest_exp).all()


def test_get_experiment_inputs():
    # set a flag that ensures that Ray data keeps the order of items in the dataset consistent
    ray.data.context.DatasetContext.get_current().execution_options.preserve_order = True

    input_handler = builtin_inputs.InputHandler(run_config)

    # run-config currently says train/val split with custom splitting condition, C_val = 0
    dataset_split = inputs.get_experiment_inputs(run_config, input_handler)
    assert len(dataset_split) == 2

    # verify that event splitting is correct
    dataset = builtin_inputs.get_inputs(
        run_config,
        nevts=run_config.max_num_events,
        input_vars_list=input_handler.get_vars()
    )
    dataset_numpy = dataset.take_batch(dataset.count())
    input_data = dataset_numpy["Input"]
    targets = dataset_numpy["Target"]
    normalized_weights = dataset_numpy["Weight"]
    weights = dataset_numpy["ScaledWeight"]
    event_nums = dataset_numpy["EventNumber"]

    train_condition = lambda x: np.mod(x, 5) != 0
    val_condition = lambda x: np.mod(x, 5) == 0
    dataset_split_numpy = [d.take_batch(d.count()) for d in dataset_split]
    inputs_split = [d["Input"] for d in dataset_split_numpy]
    targets_split = [d["Target"] for d in dataset_split_numpy]
    normalized_weights_split = [d["Weight"] for d in dataset_split_numpy]
    weights_split = [d["ScaledWeight"] for d in dataset_split_numpy]
    assert input_data[train_condition(event_nums), :].shape == inputs_split[0].shape
    assert input_data[val_condition(event_nums), :].shape == inputs_split[1].shape
    assert targets[train_condition(event_nums)].shape == targets_split[0].shape
    assert targets[val_condition(event_nums)].shape == targets_split[1].shape
    assert weights[train_condition(event_nums)].shape == weights_split[0].shape
    assert weights[val_condition(event_nums)].shape == weights_split[1].shape
    assert normalized_weights[train_condition(event_nums)].shape == normalized_weights_split[0].shape
    assert normalized_weights[val_condition(event_nums)].shape == normalized_weights_split[1].shape

    # now use random splitting
    run_config.use_eventNums_splitting = False
    dataset_split = inputs.get_experiment_inputs(run_config, input_handler)
    dataset_split_numpy = [d.take_batch(d.count()) for d in dataset_split]
    inputs_split = [d["Input"] for d in dataset_split_numpy]
    targets_split = [d["Target"] for d in dataset_split_numpy]
    normalized_weights_split = [d["Weight"] for d in dataset_split_numpy]
    weights_split = [d["ScaledWeight"] for d in dataset_split_numpy]
    assert len(dataset_split) == 2
    assert inputs_split[0].shape == (8000, 13)
    assert inputs_split[1].shape == (2000, 13)
    assert targets_split[0].shape == (8000, 1)
    assert (targets_split[0][:10] == [[0.], [1.], [1.], [1.], [1.], [0.], [1.], [0.], [0.], [1.]]).all()  # verify that loading inputs is deterministic
    assert targets_split[1].shape == (2000, 1)
    assert weights_split[0].shape == (8000,)
    assert weights_split[1].shape == (2000,)
    assert normalized_weights_split[0].shape == (8000,)
    assert normalized_weights_split[1].shape == (2000,)
    run_config.use_eventNums_splitting = True

    # now also use testing set; C_test is 1
    run_config.use_testing_dataset = True
    dataset_split = inputs.get_experiment_inputs(run_config, input_handler)
    assert len(dataset_split) == 3
    dataset_split_numpy = [d.take_batch(d.count()) for d in dataset_split]
    inputs_split = [d["Input"] for d in dataset_split_numpy]
    targets_split = [d["Target"] for d in dataset_split_numpy]
    normalized_weights_split = [d["Weight"] for d in dataset_split_numpy]
    weights_split = [d["ScaledWeight"] for d in dataset_split_numpy]
    train_condition = lambda x: np.mod(x, 5) * np.mod(x + 1, 5) != 0
    val_condition = lambda x: np.mod(x, 5) == 0
    test_condition = lambda x: np.mod(x + 1, 5) == 0
    assert input_data[train_condition(event_nums), :].shape == inputs_split[0].shape
    assert input_data[val_condition(event_nums), :].shape == inputs_split[1].shape
    assert input_data[test_condition(event_nums), :].shape == inputs_split[2].shape
    assert targets[train_condition(event_nums)].shape == targets_split[0].shape
    assert targets[val_condition(event_nums)].shape == targets_split[1].shape
    assert targets[test_condition(event_nums)].shape == targets_split[2].shape
    assert weights[train_condition(event_nums)].shape == weights_split[0].shape
    assert weights[val_condition(event_nums)].shape == weights_split[1].shape
    assert weights[test_condition(event_nums)].shape == weights_split[2].shape
    assert normalized_weights[train_condition(event_nums)].shape == normalized_weights_split[0].shape
    assert normalized_weights[val_condition(event_nums)].shape == normalized_weights_split[1].shape
    assert normalized_weights[test_condition(event_nums)].shape == normalized_weights_split[2].shape

    # and now use random splitting with testing dataset
    run_config.use_eventNums_splitting = False
    dataset_split = inputs.get_experiment_inputs(run_config, input_handler)
    assert len(dataset_split) == 3
    dataset_split_numpy = [d.take_batch(d.count()) for d in dataset_split]
    inputs_split = [d["Input"] for d in dataset_split_numpy]
    targets_split = [d["Target"] for d in dataset_split_numpy]
    normalized_weights_split = [d["Weight"] for d in dataset_split_numpy]
    weights_split = [d["ScaledWeight"] for d in dataset_split_numpy]
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3
    assert inputs_split[0].shape == (6000, 13)
    assert inputs_split[1].shape == (2000, 13)
    assert inputs_split[2].shape == (2000, 13)
    assert targets_split[0].shape == (6000, 1)
    assert (targets_split[0][:10] == [[0.], [1.], [1.], [1.], [1.], [0.], [1.], [0.], [0.], [1.]]).all()  # verify that loading inputs is deterministic
    assert targets_split[1].shape == (2000, 1)
    assert targets_split[2].shape == (2000, 1)
    assert weights_split[0].shape == (6000,)
    assert weights_split[1].shape == (2000,)
    assert weights_split[2].shape == (2000,)
    assert normalized_weights_split[0].shape == (6000,)
    assert normalized_weights_split[1].shape == (2000,)
    assert normalized_weights_split[2].shape == (2000,)
    run_config.use_eventNums_splitting = True
    run_config.use_testing_dataset = False

    # now try inputs for crossvalidation with custom splitting, no testing dataset
    dataset_split = inputs.get_experiment_inputs(run_config, input_handler, inputs_for_crossvalidation=True)
    dataset_split_numpy = [[d[i].take_batch(d[i].count()) for i in range(5)] for d in dataset_split]
    inputs_split = [[d[i]["Input"] for i in range(5)] for d in dataset_split_numpy]
    targets_split = [[d[i]["Target"] for i in range(5)] for d in dataset_split_numpy]
    normalized_weights_split = [[d[i]["Weight"] for i in range(5)] for d in dataset_split_numpy]
    weights_split = [[d[i]["ScaledWeight"] for i in range(5)] for d in dataset_split_numpy]
    splitting_cond_val = inputs._event_nums_splitting_cond_kfold(
        event_nums,
        run_config,
        split='val',
        use_testing_set=False,
    )
    splitting_cond_train = np.logical_not(splitting_cond_val)
    assert len(inputs_split) == 2
    assert len(targets_split) == 2
    assert len(weights_split) == 2
    assert len(normalized_weights_split) == 2

    for split in range(run_config.eventNums_splitting_N):
        assert input_data[splitting_cond_train[split]].shape == inputs_split[0][split].shape
        assert targets[splitting_cond_train[split]].shape == targets_split[0][split].shape
        assert weights[splitting_cond_train[split]].shape == weights_split[0][split].shape
        assert normalized_weights[splitting_cond_train[split]].shape == normalized_weights_split[0][split].shape
        assert input_data[splitting_cond_val[split]].shape == inputs_split[1][split].shape
        assert targets[splitting_cond_val[split]].shape == targets_split[1][split].shape
        assert weights[splitting_cond_val[split]].shape == weights_split[1][split].shape
        assert normalized_weights[splitting_cond_val[split]].shape == normalized_weights_split[1][split].shape

    # with testing dataset
    run_config.use_testing_dataset = True
    dataset_split = inputs.get_experiment_inputs(run_config, input_handler, inputs_for_crossvalidation=True)
    dataset_split_numpy = [[d[i].take_batch(d[i].count()) for i in range(4)] for d in dataset_split]
    inputs_split = [[d[i]["Input"] for i in range(4)] for d in dataset_split_numpy]
    targets_split = [[d[i]["Target"] for i in range(4)] for d in dataset_split_numpy]
    normalized_weights_split = [[d[i]["Weight"] for i in range(4)] for d in dataset_split_numpy]
    weights_split = [[d[i]["ScaledWeight"] for i in range(4)] for d in dataset_split_numpy]
    splitting_cond_val = inputs._event_nums_splitting_cond_kfold(
        event_nums,
        run_config,
        split='val',
        use_testing_set=True,
    )
    splitting_cond_test = inputs._event_nums_splitting_cond_kfold(
        event_nums,
        run_config,
        split='test',
        use_testing_set=True,
    )
    splitting_cond_train = np.logical_not(np.logical_or(splitting_cond_val, splitting_cond_test))
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3

    for split in range(run_config.eventNums_splitting_N-1):
        assert input_data[splitting_cond_train[split]].shape == inputs_split[0][split].shape
        assert targets[splitting_cond_train[split]].shape == targets_split[0][split].shape
        assert weights[splitting_cond_train[split]].shape == weights_split[0][split].shape
        assert normalized_weights[splitting_cond_train[split]].shape == normalized_weights_split[0][split].shape
        assert input_data[splitting_cond_val[split]].shape == inputs_split[1][split].shape
        assert targets[splitting_cond_val[split]].shape == targets_split[1][split].shape
        assert weights[splitting_cond_val[split]].shape == weights_split[1][split].shape
        assert normalized_weights[splitting_cond_val[split]].shape == normalized_weights_split[1][split].shape
        assert input_data[splitting_cond_test[split]].shape == inputs_split[2][split].shape
        assert targets[splitting_cond_test[split]].shape == targets_split[2][split].shape
        assert weights[splitting_cond_test[split]].shape == weights_split[2][split].shape
        assert normalized_weights[splitting_cond_test[split]].shape == normalized_weights_split[2][split].shape
    run_config.use_testing_dataset = False

    # with variable testing dataset
    run_config.use_testing_dataset = True
    run_config.fixed_testing_dataset = False
    dataset_split = inputs.get_experiment_inputs(run_config, input_handler, inputs_for_crossvalidation=True)
    dataset_split_numpy = [[d[i].take_batch(d[i].count()) for i in range(5)] for d in dataset_split]
    inputs_split = [[d[i]["Input"] for i in range(5)] for d in dataset_split_numpy]
    targets_split = [[d[i]["Target"] for i in range(5)] for d in dataset_split_numpy]
    normalized_weights_split = [[d[i]["Weight"] for i in range(5)] for d in dataset_split_numpy]
    weights_split = [[d[i]["ScaledWeight"] for i in range(5)] for d in dataset_split_numpy]
    splitting_cond_val = inputs._event_nums_splitting_cond_kfold(
        event_nums,
        run_config,
        split='val',
        use_testing_set=True,
        fixed_testing_set=False
    )
    splitting_cond_test = inputs._event_nums_splitting_cond_kfold(
        event_nums,
        run_config,
        split='test',
        use_testing_set=True,
        fixed_testing_set=False
    )
    splitting_cond_train = np.logical_not(np.logical_or(splitting_cond_val, splitting_cond_test))
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3

    for split in range(run_config.eventNums_splitting_N):
        assert input_data[splitting_cond_train[split]].shape == inputs_split[0][split].shape
        assert targets[splitting_cond_train[split]].shape == targets_split[0][split].shape
        assert weights[splitting_cond_train[split]].shape == weights_split[0][split].shape
        assert normalized_weights[splitting_cond_train[split]].shape == normalized_weights_split[0][split].shape
        assert input_data[splitting_cond_val[split]].shape == inputs_split[1][split].shape
        assert targets[splitting_cond_val[split]].shape == targets_split[1][split].shape
        assert weights[splitting_cond_val[split]].shape == weights_split[1][split].shape
        assert normalized_weights[splitting_cond_val[split]].shape == normalized_weights_split[1][split].shape
        assert input_data[splitting_cond_test[split]].shape == inputs_split[2][split].shape
        assert targets[splitting_cond_test[split]].shape == targets_split[2][split].shape
        assert weights[splitting_cond_test[split]].shape == weights_split[2][split].shape
        assert normalized_weights[splitting_cond_test[split]].shape == normalized_weights_split[2][split].shape
    run_config.fixed_testing_dataset = True
    run_config.use_testing_dataset = False

    # now random splitting, no testing dataset
    run_config.use_eventNums_splitting = False
    dataset_split = inputs.get_experiment_inputs(run_config, input_handler, inputs_for_crossvalidation=True)
    dataset_split_numpy = [[d[i].take_batch(d[i].count()) for i in range(5)] for d in dataset_split]
    inputs_split = [[d[i]["Input"] for i in range(5)] for d in dataset_split_numpy]
    targets_split = [[d[i]["Target"] for i in range(5)] for d in dataset_split_numpy]
    normalized_weights_split = [[d[i]["Weight"] for i in range(5)] for d in dataset_split_numpy]
    weights_split = [[d[i]["ScaledWeight"] for i in range(5)] for d in dataset_split_numpy]
    assert len(inputs_split) == 2
    assert len(targets_split) == 2
    assert len(weights_split) == 2
    assert len(normalized_weights_split) == 2
    assert (targets_split[0][0][:10] == [[0.], [1.], [1.], [0.], [0.], [0.], [0.], [0.], [1.], [1.]]).all()  # verify that loading inputs is deterministic
    for split in range(round(run_config.test_fraction / run_config.validation_fraction)):
        assert inputs_split[0][split].shape == (8000, 13)
        assert inputs_split[1][split].shape == (2000, 13)
        assert targets_split[0][split].shape == (8000, 1)
        assert targets_split[1][split].shape == (2000, 1)
        assert weights_split[0][split].shape == (8000,)
        assert weights_split[1][split].shape == (2000,)
        assert normalized_weights_split[0][split].shape == (8000,)
        assert normalized_weights_split[1][split].shape == (2000,)
    run_config.use_eventNums_splitting = True

    # with testing dataset
    run_config.use_eventNums_splitting = False
    run_config.use_testing_dataset = True
    dataset_split = inputs.get_experiment_inputs(run_config, input_handler, inputs_for_crossvalidation=True)
    dataset_split_numpy = [[d[i].take_batch(d[i].count()) for i in range(4)] for d in dataset_split]
    inputs_split = [[d[i]["Input"] for i in range(4)] for d in dataset_split_numpy]
    targets_split = [[d[i]["Target"] for i in range(4)] for d in dataset_split_numpy]
    normalized_weights_split = [[d[i]["Weight"] for i in range(4)] for d in dataset_split_numpy]
    weights_split = [[d[i]["ScaledWeight"] for i in range(4)] for d in dataset_split_numpy]
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3
    assert (targets_split[0][0][:10] == [[0.], [1.], [1.], [0.], [0.], [0.], [0.], [0.], [1.], [1.]]).all()  # verify that loading inputs is deterministic
    for split in range(round((1 - run_config.test_fraction) / run_config.validation_fraction)):
        assert inputs_split[0][split].shape == (6000, 13)
        assert inputs_split[1][split].shape == (2000, 13)
        assert inputs_split[2][split].shape == (2000, 13)
        assert np.max(inputs_split[2][split] - inputs_split[2][0]) < 0.05
        assert targets_split[0][split].shape == (6000, 1)
        assert targets_split[1][split].shape == (2000, 1)
        assert targets_split[2][split].shape == (2000, 1)
        assert (targets_split[2][split] == targets_split[2][0]).all()
        assert weights_split[0][split].shape == (6000,)
        assert weights_split[1][split].shape == (2000,)
        assert weights_split[2][split].shape == (2000,)
        assert (weights_split[2][split] == weights_split[2][0]).all()
        assert normalized_weights_split[0][split].shape == (6000,)
        assert normalized_weights_split[1][split].shape == (2000,)
        assert normalized_weights_split[2][split].shape == (2000,)
        assert (normalized_weights_split[2][split] == normalized_weights_split[2][0]).all()
    run_config.use_eventNums_splitting = True
    run_config.use_testing_dataset = False

    # with variable testing dataset
    run_config.use_eventNums_splitting = False
    run_config.use_testing_dataset = True
    run_config.fixed_testing_dataset = False
    dataset_split = inputs.get_experiment_inputs(run_config, input_handler, inputs_for_crossvalidation=True)
    dataset_split_numpy = [[d[i].take_batch(d[i].count()) for i in range(5)] for d in dataset_split]
    inputs_split = [[d[i]["Input"] for i in range(5)] for d in dataset_split_numpy]
    targets_split = [[d[i]["Target"] for i in range(5)] for d in dataset_split_numpy]
    normalized_weights_split = [[d[i]["Weight"] for i in range(5)] for d in dataset_split_numpy]
    weights_split = [[d[i]["ScaledWeight"] for i in range(5)] for d in dataset_split_numpy]
    assert len(inputs_split) == 3
    assert len(targets_split) == 3
    assert len(weights_split) == 3
    assert len(normalized_weights_split) == 3
    for split in range(round(1 / run_config.test_fraction)):
        assert inputs_split[0][split].shape == (6000, 13)
        assert inputs_split[1][split].shape == (2000, 13)
        assert inputs_split[2][split].shape == (2000, 13)
        if split > 0: assert np.max(inputs_split[2][split] - inputs_split[2][0]) > 0.05
        assert targets_split[0][split].shape == (6000, 1)
        assert targets_split[1][split].shape == (2000, 1)
        assert targets_split[2][split].shape == (2000, 1)
        if split > 0: assert np.max(targets_split[2][split] - targets_split[2][0]) > 0.01
        assert weights_split[0][split].shape == (6000,)
        assert weights_split[1][split].shape == (2000,)
        assert weights_split[2][split].shape == (2000,)
        if split > 0: assert np.max(weights_split[2][split] - weights_split[2][0]) > 0.01 * np.mean(weights_split[2][split])
        assert normalized_weights_split[0][split].shape == (6000,)
        assert normalized_weights_split[1][split].shape == (2000,)
        assert normalized_weights_split[2][split].shape == (2000,)
        if split > 0: assert np.max(normalized_weights_split[2][split] - normalized_weights_split[2][0]) > 0.01
    run_config.use_eventNums_splitting = True
    run_config.use_testing_dataset = False
    run_config.fixed_testing_dataset = True
