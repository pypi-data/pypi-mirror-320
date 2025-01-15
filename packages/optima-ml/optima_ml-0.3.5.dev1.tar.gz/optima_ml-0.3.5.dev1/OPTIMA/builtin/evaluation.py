# -*- coding: utf-8 -*-
"""Provides a collection of classes and functions to evaluate the performance of classifiers."""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import roc_curve, auc

import OPTIMA.core.model
import OPTIMA.core.evaluation


def evaluate(
    run_config,
    model_path,
    model_config,
    dataset_split,
    input_handler,
    fig_dir,
    native_metrics=None,
    weighted_native_metrics=None,
    custom_metrics=None,
    composite_metrics=None,
    class_labels=None,
    cpus=1,
    results_dir=None,
    N_bins=40,
    print_results=True,
    return_unfilled=False,
    ratio=True,
):
    """Built-in evaluation for classification tasks.

    This function assumes that the entire dataset and the model predictions can fit into memory.

    Parameters
    ----------
    run_config : _type_
        _description_
    model_path : _type_
        _description_
    model_config : _type_
        _description_
    dataset_split : _type_
        _description_
    input_handler : _type_
        _description_
    fig_dir : _type_
        _description_
    native_metrics : _type_
        _description_ (Default value = [])
    weighted_native_metrics : _type_
        _description_ (Default value = [])
    custom_metrics : _type_
        _description_ (Default value = [])
    composite_metrics : _type_
        _description_ (Default value = None)
    class_labels : _type_
        _description_ (Default value = None)
    cpus : _type_
        _description_ (Default value = 1)
    results_dir : _type_
        _description_ (Default value = None)
    N_bins : _type_
        _description_ (Default value = 40)
    print_results : _type_
        _description_ (Default value = True)
    return_unfilled : _type_
        _description_ (Default value = False)
    ratio : _type_
        _description_ (Default value = True)

    Returns
    -------
    _type_
        _description_
    """
    if native_metrics is None:
        native_metrics = []
    if weighted_native_metrics is None:
        weighted_native_metrics = []
    if custom_metrics is None:
        custom_metrics = []
    if composite_metrics is None:
        composite_metrics = []

    # fetch the target labels and optional sample weights --> this saves everything into this worker's memory. If OOM
    # error occurs, define an evaluate-function in the run-config.
    if len(dataset_split) == 2:
        explicit_testing_dataset = False
        dataset_train, dataset_val = dataset_split
        train_data = list(dataset_train.iter_batches(batch_size=dataset_train.count()))[0]
        val_data = list(dataset_val.iter_batches(batch_size=dataset_val.count()))[0]
        targets_train = train_data["Target"]
        targets_val = val_data["Target"]
        if "ScaledWeight" in dataset_train.columns():
            weights_train = train_data["ScaledWeight"]
            weights_val = val_data["ScaledWeight"]
        elif "Weight" in dataset_train.columns():
            weights_train = train_data["Weight"]
            weights_val = val_data["Weight"]
        else:
            weights_train = np.ones((targets_train.shape[0],))
            weights_val = np.ones((targets_val.shape[0],))
        print(
            "testing model using {} training and {} validation events".format(
                targets_train.shape[0], targets_val.shape[0]
            )
        )
    else:
        explicit_testing_dataset = True
        dataset_train, dataset_val, dataset_test = dataset_split
        train_data = list(dataset_train.iter_batches(batch_size=dataset_train.count()))[0]
        val_data = list(dataset_val.iter_batches(batch_size=dataset_val.count()))[0]
        test_data = list(dataset_test.iter_batches(batch_size=dataset_test.count()))[0]
        targets_train = train_data["Target"]
        targets_val = val_data["Target"]
        targets_test = test_data["Target"]
        if "ScaledWeight" in dataset_train.columns():
            weights_train = train_data["ScaledWeight"]
            weights_val = val_data["ScaledWeight"]
            weights_test = test_data["ScaledWeight"]
        elif "Weight" in dataset_train.columns():
            weights_train = train_data["Weight"]
            weights_val = val_data["Weight"]
            weights_test = test_data["Weight"]
        else:
            weights_train = np.ones((targets_train.shape[0],))
            weights_val = np.ones((targets_val.shape[0],))
            weights_test = np.ones((targets_test.shape[0],))
        print(
            "testing model using {} training, {} validation and {} testing events".format(
                targets_train.shape[0], targets_val.shape[0], targets_test.shape[0]
            )
        )

    # create the output folders if they do not exist
    if not os.path.exists(fig_dir):
        os.makedirs(fig_dir, exist_ok=True)
    if results_dir is not None:
        if not os.path.exists(results_dir):
            os.makedirs(results_dir, exist_ok=True)

    # load the model, prepare the datasets (i.e. convert from ray datasets to ML native datasets) and get the model
    # predictions
    model = OPTIMA.core.model.load_model(run_config, model_config, input_handler, model_path, cpus)
    native_datasets = model.prepare_datasets(
        dataset_train,
        dataset_val,
        dataset_test if explicit_testing_dataset else None,
    )
    preds = model.predict(native_datasets, verbose=0)
    if explicit_testing_dataset:
        pred_train, pred_val, pred_test = preds
    else:
        pred_train, pred_val = preds
    num_outputs = pred_train.shape[1]

    # check if we have binary or multiclass classification
    if targets_train.shape[1] == 1:
        binary_classification = True
        num_classes = 2
    else:
        binary_classification = False
        num_classes = targets_train.shape[1]

    # for each class, calculate the train, validation and test weights, scaled weights where the sum of the weights is
    # scaled to the total weight for each class, and split the model predictions into the different classes
    weights_train_classes = []
    scaled_weights_train_classes = []
    pred_train_classes = []
    weights_val_classes = []
    scaled_weights_val_classes = []
    pred_val_classes = []
    if explicit_testing_dataset:
        weights_test_classes = []
        scaled_weights_test_classes = []
        pred_test_classes = []
    total_weight_classes = []
    for i in range(num_classes if not binary_classification else 1):
        for t in range(
            1 if not binary_classification else 0, 2
        ):  # for binary classification, both 0 and 1 are important target values
            # get class weights and total weight for this class
            weights_train_classes.append(weights_train[targets_train[:, i] == t])
            weights_val_classes.append(weights_val[targets_val[:, i] == t])
            if explicit_testing_dataset:
                weights_test_classes.append(weights_test[targets_test[:, i] == t])
                total_weight_classes.append(
                    np.sum(weights_train_classes[-1])
                    + np.sum(weights_val_classes[-1])
                    + np.sum(weights_test_classes[-1])
                )
            else:
                total_weight_classes.append(np.sum(weights_train_classes[-1]) + np.sum(weights_val_classes[-1]))

            # calculate scaled weights
            scaled_weights_train_classes.append(
                weights_train_classes[-1] / np.sum(weights_train_classes[-1]) * total_weight_classes[-1]
            )
            scaled_weights_val_classes.append(
                weights_val_classes[-1] / np.sum(weights_val_classes[-1]) * total_weight_classes[-1]
            )
            if explicit_testing_dataset:
                scaled_weights_test_classes.append(
                    weights_test_classes[-1] / np.sum(weights_test_classes[-1]) * total_weight_classes[-1]
                )

            # get the model predictions for this class
            pred_train_classes.append(pred_train[targets_train[:, i] == t])
            pred_val_classes.append(pred_val[targets_val[:, i] == t])
            if explicit_testing_dataset:
                pred_test_classes.append(pred_test[targets_test[:, i] == t])

    # get the ROC curves in the One-vs.-Rest scheme; this does only make sense for binary classification (one output,
    # two classes) or multiclass (multiple outputs, same number of classes), but not for anything in between (e.g. one
    # output, multiple classes)
    do_roc = binary_classification or num_classes == num_outputs
    if do_roc:
        auc_train_classes = []
        auc_val_classes = []
        if explicit_testing_dataset:
            auc_test_classes = []
        for i in range(num_classes if not binary_classification else 1):
            fig, ax = plt.subplots(figsize=[6, 4.5], layout="constrained")

            # ignore negative sample weights
            fpr_train, tpr_train, _ = roc_curve(
                y_true=targets_train[:, i].ravel()[weights_train > 0],
                y_score=pred_train[:, i].ravel()[weights_train > 0],
                sample_weight=weights_train[weights_train > 0],
            )
            fpr_val, tpr_val, _ = roc_curve(
                y_true=targets_val[:, i].ravel()[weights_val > 0],
                y_score=pred_val[:, i].ravel()[weights_val > 0],
                sample_weight=weights_val[weights_val > 0],
            )
            auc_train = auc(fpr_train, tpr_train)
            auc_val = auc(fpr_val, tpr_val)
            ax.plot(fpr_train, tpr_train, label=f"training (AUC = {auc_train:.4f}")
            ax.plot(fpr_val, tpr_val, label=f"validation (AUC = {auc_val:.4f}")
            if explicit_testing_dataset:
                fpr_test, tpr_test, _ = roc_curve(
                    y_true=targets_test[:, i].ravel()[weights_test > 0],
                    y_score=pred_test[:, i].ravel()[weights_test > 0],
                    sample_weight=weights_test[weights_test > 0],
                )
                auc_test = auc(fpr_test, tpr_test)
                ax.plot(fpr_test, tpr_test, label=f"testing (AUC = {auc_test:.4f}")
            ax.set_xlim((0.0, 1.0))
            ax.set_ylim((0.0, 1.0))
            ax.set_xlabel("False Positive Rate")
            ax.set_ylabel("True Positive Rate")
            class_name = class_labels[i] if class_labels is not None else f"Class {i}"
            ax.set_title(
                "Receiver Operating Characteristic" + (f" ({class_name} vs. Rest)" if not binary_classification else "")
            )
            ax.legend()
            fig.savefig(
                os.path.join(fig_dir, f"ROC_{class_name}_vs_rest.pdf" if not binary_classification else "ROC.pdf")
            )

            auc_train_classes.append(auc_train)
            auc_val_classes.append(auc_val)
            if explicit_testing_dataset:
                auc_test_classes.append(auc_test)

    def _weighted_hists_with_uncertainty(arrays_tuple, weights_tuple, N_bins, hist_range=None, stacked=False):
        """_summary_.

        Parameters
        ----------
        arrays_tuple : _type_
            _description_
        weights_tuple : _type_
            _description_
        N_bins : _type_
            _description_
        hist_range : _type_
            _description_ (Default value = None)
        stacked : _type_
            _description_ (Default value = False)

        Returns
        -------
        _type_
            _description_
        """
        bin_contents, bin_edges, _ = plt.hist(arrays_tuple, bins=N_bins, range=hist_range, weights=weights_tuple)
        plt.clf()
        uncertainties = []
        if not stacked:
            for values, weights, _ in zip(arrays_tuple, weights_tuple, bin_contents):
                # get the index of the bin each value belongs in; then expand the array of bin indices along a new axis,
                # substract the new axis index from the values so that each bin index is zero in the corresponding subarray.
                # Convert to boolean array by checking which entry is zero
                conditions_array = (
                    pd.cut(values, bins=bin_edges, labels=False)
                    - np.linspace(0, N_bins, N_bins, endpoint=False, dtype=int).reshape((N_bins, 1))
                ) == 0

                # tile the weight array to get the same shape as the conditions array; assumes 1D weights
                weights_tiled = np.tile(weights, reps=N_bins).reshape((N_bins, weights.shape[0]))

                # calculate uncertainties by replacing all values in weights_tiled with weights_tiled^2 where conditions_array
                # is True, else replace with zero. then calculate sum along the values axis to get the uncertainty for this bin
                delta = np.sqrt(
                    np.sum(np.where(conditions_array, np.square(weights_tiled), np.zeros_like(weights_tiled)), axis=1)
                )

                uncertainties.append(delta)
        else:
            # only the final entry in bin_contents should have errors, which then come from all entries together
            uncertainties = [np.zeros_like(b) for b in bin_contents[:-1]]
            values = np.concatenate(arrays_tuple)
            weights = np.concatenate(weights_tuple)
            conditions_array = (
                pd.cut(values, bins=bin_edges, labels=False)
                - np.linspace(0, N_bins, N_bins, endpoint=False, dtype=int).reshape((N_bins, 1))
            ) == 0
            weights_tiled = np.tile(weights, reps=N_bins).reshape((N_bins, weights.shape[0]))
            delta = np.sqrt(
                np.sum(np.where(conditions_array, np.square(weights_tiled), np.zeros_like(weights_tiled)), axis=1)
            )
            uncertainties.append(delta)

        return bin_contents, bin_edges, uncertainties

    def _draw_hist_with_ratios(
        bin_edges,
        bin_contents_with_type,
        uncertainties,
        ratio_refs,
        ratio_refs_uncertainties,
        text_boxes,
        colors,
        colors_errors,
        title,
        x_label,
        y_labels,
        legend_labels,
        x_range=None,
        figpath=None,
        stacked=False,
    ):
        """_summary_.

        Parameters
        ----------
        bin_edges : _type_
            _description_
        bin_contents_with_type : _type_
            _description_
        uncertainties : _type_
            _description_
        ratio_refs : _type_
            _description_
        ratio_refs_uncertainties : _type_
            _description_
        text_boxes : _type_
            _description_
        colors : _type_
            _description_
        colors_errors : _type_
            _description_
        title : _type_
            _description_
        x_label : _type_
            _description_
        y_labels : _type_
            _description_
        legend_labels : _type_
            _description_
        x_range : _type_
            _description_ (Default value = None)
        figpath : _type_
            _description_ (Default value = None)
        stacked : _type_
            _description_ (Default value = False)

        Returns
        -------
        _type_
            _description_
        """
        fig, axs = plt.subplots(
            1 + len(ratio_refs),
            1,
            gridspec_kw={"height_ratios": [4] + [1] * len(ratio_refs)},
            sharex="col",
            layout="constrained",
        )
        if not isinstance(axs, np.ndarray):
            axs = np.array([axs])
        fig.set_figheight(4.5 + 0.6 * len(ratio_refs))
        fig.set_figwidth(5.5)

        cumsum = np.append(np.zeros_like(uncertainties[0]), 0.0)
        plot_objects = []
        error_objects = []
        hatch_linewidth_before = plt.rcParams["hatch.linewidth"]
        plt.rcParams["hatch.linewidth"] = 0.6
        for i, (bin_content_with_type, delta) in enumerate(zip(bin_contents_with_type, uncertainties)):
            content_type, ratio_ref_index, bin_content = bin_content_with_type
            bin_centers = (bin_edges[1:] + bin_edges[:-1]) / 2
            bin_content_extended = np.append(bin_content, bin_content[-1])
            delta_extended = np.append(delta, delta[-1])

            if content_type == "scatter":
                plot_objects.append(
                    axs[0].scatter(bin_centers, bin_content, color=colors[i], s=10, label=legend_labels[i])
                )
                if (delta > 0).any():
                    error_objects.append(
                        axs[0].errorbar(
                            bin_centers,
                            bin_content,
                            xerr=1 / (2 * N_bins),
                            yerr=delta,
                            color=colors_errors[i],
                            ls="none",
                            linewidth=0.8,
                        )
                    )

                if len(ratio_refs) > 0:
                    ratio_ref = ratio_refs[ratio_ref_index]
                    ratio_ref_uncertainty = ratio_refs_uncertainties[ratio_ref_index]
                    axs[1 + ratio_ref_index].scatter(
                        bin_centers[ratio_ref != 0],
                        bin_content[ratio_ref != 0] / ratio_ref[ratio_ref != 0],
                        color=colors[i],
                        s=10,
                    )
                    if (delta > 0).any():
                        axs[1 + ratio_ref_index].errorbar(
                            bin_centers[ratio_ref != 0],
                            bin_content[ratio_ref != 0] / ratio_ref[ratio_ref != 0],
                            xerr=1 / (2 * N_bins),
                            yerr=np.sqrt(
                                (delta[ratio_ref != 0] / ratio_ref[ratio_ref != 0]) ** 2
                                + (
                                    bin_content[ratio_ref != 0]
                                    / ratio_ref[ratio_ref != 0] ** 2
                                    * ratio_ref_uncertainty[ratio_ref != 0]
                                )
                                ** 2
                            ),  # assume the two hists are independent
                            color=colors_errors[i],
                            ls="none",
                            linewidth=0.8,
                        )
            else:
                if not stacked:
                    this_value = bin_content_extended
                    plot_objects.append(
                        axs[0].step(
                            bin_edges, this_value, where="post", color=colors[i], linewidth=0.8, label=legend_labels[i]
                        )
                    )
                else:
                    this_value = cumsum + bin_content_extended
                    plot_objects.append(
                        axs[0].fill_between(
                            bin_edges,
                            cumsum,
                            this_value,
                            step="post",
                            alpha=1.0,
                            facecolor=colors[i],
                            linewidth=0.8,
                            label=legend_labels[i],
                        )
                    )
                    cumsum = this_value
                if (delta_extended > 0).any():
                    error_objects.append(
                        axs[0].fill_between(
                            bin_edges,
                            this_value - delta_extended,
                            this_value + delta_extended,
                            step="post",
                            alpha=1.0,
                            hatch="///////",
                            facecolor="none",
                            edgecolor=colors_errors[i],
                            linewidth=0.0,
                        )
                    )

                if len(ratio_refs) > 0:
                    ratio_ref_extended = np.append(ratio_refs[ratio_ref_index], ratio_refs[ratio_ref_index][-1])
                    ratio_ref_uncertainties_extended = np.append(
                        ratio_refs_uncertainties[ratio_ref_index], ratio_refs_uncertainties[ratio_ref_index][-1]
                    )
                    axs[1 + ratio_ref_index].step(
                        bin_edges[ratio_ref_extended != 0],
                        bin_content_extended[ratio_ref_extended != 0] / ratio_ref_extended[ratio_ref_extended != 0],
                        where="post",
                        color=colors[i],
                        linewidth=0.8,
                    )
                    delta_ratio = np.sqrt(
                        (delta_extended[ratio_ref_extended != 0] / ratio_ref_extended[ratio_ref_extended != 0]) ** 2
                        + (
                            bin_content_extended[ratio_ref_extended != 0]
                            / ratio_ref_extended[ratio_ref_extended != 0] ** 2
                            * ratio_ref_uncertainties_extended[ratio_ref_extended != 0]
                        )
                        ** 2
                    )
                    if (delta_extended > 0).any():
                        axs[1 + ratio_ref_index].fill_between(
                            bin_edges[ratio_ref_extended != 0],
                            bin_content_extended[ratio_ref_extended != 0] / ratio_ref_extended[ratio_ref_extended != 0]
                            - delta_ratio,
                            bin_content_extended[ratio_ref_extended != 0] / ratio_ref_extended[ratio_ref_extended != 0]
                            + delta_ratio,
                            step="post",
                            alpha=1.0,
                            hatch="///////",
                            facecolor="none",
                            edgecolor=colors_errors[i],
                            linewidth=0.0,
                        )

        # error bar only for legend
        axs[0].fill_between(
            [],
            [],
            [],
            step="post",
            alpha=1.0,
            hatch="///////",
            facecolor="none",
            edgecolor="black",
            linewidth=0.0,
            label="Stat. Unc.",
        )

        # text boxes on axes
        for i, text in enumerate(text_boxes):
            if i > len(ratio_refs):
                break

            # check if empty string
            if not text:
                continue

            props = dict(alpha=0.0)
            # place a text box in upper left
            axs[i].text(
                0.01, 1.01, text, transform=axs[i].transAxes, fontsize=8, verticalalignment="bottom", bbox=props
            )

        if x_range is not None:
            axs[0].set_xlim(x_range)
        axs[0].set_ylim(bottom=0)
        for i in range(1, len(ratio_refs) + 1):
            axs[i].set_ylabel(y_labels[i])
            axs[i].set_ylim((0.5, 1.6))

        # legend in two columns if more than three labels
        handles, labels = axs[0].get_legend_handles_labels()
        n_labels = len(handles)
        if n_labels > 3:
            handles = np.concatenate((handles[::2], handles[1::2]), axis=0)
            labels = np.concatenate((labels[::2], labels[1::2]), axis=0)
            axs[0].legend(handles, labels, loc=1, ncol=2)
        else:
            axs[0].legend(loc=1)

        # set y-limit to fit the legend
        ax_ylim = axs[0].get_ylim()[1]
        scale_ylim = 0.1
        scale_ylim *= n_labels if n_labels <= 3 else (n_labels / 2 + n_labels % 2)
        axs[0].set_ylim(top=ax_ylim * (1 + scale_ylim))

        axs[0].set_ylabel(y_labels[0])
        axs[-1].set_xlabel(x_label)
        fig.suptitle(title)
        if figpath is not None:
            plt.savefig(figpath, dpi=600)
        else:
            fig.set_dpi(300)
            plt.show()
        plt.rcParams["hatch.linewidth"] = hatch_linewidth_before

    # create stacked histograms for each of the DNN outputs with all classes
    # first define tuples of predictions and corresponding weights for both the stacked and the normalized histogram.
    # For the stacked histogram, the order in the tuple defines the order of the contributions in the stack, from the
    # bottom upwards.
    for i in range(num_outputs):
        # get the predictions of output i for all classes
        if not explicit_testing_dataset:
            pred_i = [p[:, i] for p in pred_val_classes]
        else:
            pred_i = [p[:, i] for p in pred_test_classes]

        # create the stacked histogram with poisson uncertainties for each bin
        bin_contents, bin_edges, uncertainties = _weighted_hists_with_uncertainty(
            pred_i,
            weights_tuple=scaled_weights_val_classes if not explicit_testing_dataset else scaled_weights_test_classes,
            N_bins=N_bins,
            # range=(0, 1),
            stacked=True,
        )

        # draw the histogram
        # for each contribution to the histogram, we need to provide the type of contribution (step or scatter), the
        # index of the reference to use for the ratio subplot, and bin content itself..
        bin_contents_with_type = zip(["step"] * num_classes, [None] * num_classes, bin_contents)
        if (num_classes <= 10 and not explicit_testing_dataset) or num_classes <= 5:
            colors = sns.color_palette()
        else:
            colors = sns.color_palette("husl", num_classes if not explicit_testing_dataset else 2 * num_classes)
        colors_errors = [None] * (num_classes - 1) + ["0.4"]  # only the uppermost contribution should have error bars
        if class_labels is not None:
            legend_labels = class_labels if not binary_classification else class_labels[::-1]
        else:
            legend_labels = (
                [f"Class {k}" for k in range(num_classes)] if not binary_classification else ["Background", "Signal"]
            )
        _draw_hist_with_ratios(
            bin_edges,
            bin_contents_with_type,
            uncertainties,
            ratio_refs=[],
            ratio_refs_uncertainties=[],
            text_boxes=[],
            colors=colors,
            colors_errors=colors_errors,
            legend_labels=legend_labels,
            title=f"Neural Network Output {i} (scaled)" if num_outputs > 1 else "Neural Network Output (scaled)",
            x_label="DNN Output",
            y_labels=["Events"],
            x_range=(bin_edges[0], bin_edges[-1]),
            stacked=True,
            figpath=os.path.join(fig_dir, f"DNN_output_{i}.pdf" if num_outputs > 1 else "DNN_output.pdf"),
        )
        plt.clf()

    # create normalized histograms for each of the DNN outputs with all classes
    # get the normalized event weights
    weights_normalized = [w / np.sum(w) for w in weights_train_classes + weights_val_classes]
    if explicit_testing_dataset:
        weights_normalized += [w / np.sum(w) for w in weights_test_classes]

    for i in range(num_outputs):
        # get the predictions of output i for all classes and the normalized weights
        pred_i = [p[:, i] for p in pred_train_classes + pred_val_classes]
        if explicit_testing_dataset:
            pred_i += [p[:, i] for p in pred_test_classes]

        # get the histogram for each class with Poisson uncertainties
        bin_contents_normal, bin_edges_normal, uncertainties_normal = _weighted_hists_with_uncertainty(
            pred_i,
            weights_tuple=weights_normalized,
            N_bins=N_bins,
            # range=(0, 1)
        )

        # construct the bin contents with type. We want the training predictions to be drawn as scatter and the validation
        # and test prediction as step. For all contributions, the training prediction of the same class should be used
        # as the reference for the ratio.
        bin_contents_normal_with_type = [("scatter", i, bin_contents_normal[i]) for i in range(num_classes)]
        bin_contents_normal_with_type += [("step", i, bin_contents_normal[num_classes + i]) for i in range(num_classes)]
        if explicit_testing_dataset:
            bin_contents_normal_with_type += [
                ("step", i, bin_contents_normal[int(2 * num_classes) + i]) for i in range(num_classes)
            ]

        # we can choose the training and validation components of each class to have the same color and choose the testing
        # colors to be different
        colors_normal = 2 * [colors[i] for i in range(num_classes)]
        if explicit_testing_dataset:
            colors_normal += [colors[num_classes + i] for i in range(num_classes)]
        colors_errors_normal = colors_normal

        # build the labels for each contribution. Again we need to pay attention if we have binary classification or not.
        # Order of labels needs to be the same as the order of contributions in bin_contents_normal_with_type.
        legend_labels = []
        for phase in ["training", "validation", "testing"] if explicit_testing_dataset else ["training", "validation"]:
            for k in range(num_classes):
                if not binary_classification:
                    if class_labels is not None:
                        legend_labels.append(f"{class_labels[k]} ({phase})")
                    else:
                        legend_labels.append(f"Class {k} ({phase})")
                else:
                    if class_labels is not None:
                        legend_labels.append(f"{class_labels[-(k+1)]} ({phase})")
                    else:
                        c = ["Background", "Signal"][k]
                        legend_labels.append(f"{c} ({phase})")

        # build the titels for the ratio plots. We need to provide a title for the main plots as well, but we can leave
        # that blank
        if class_labels is not None:
            ratio_titles = [""] + class_labels
        else:
            ratio_titles = [""] + (
                [f"Class {k}" for k in range(num_classes)] if not binary_classification else ["Background", "Signal"]
            )

        _draw_hist_with_ratios(
            bin_edges_normal,
            bin_contents_normal_with_type,
            uncertainties_normal,
            ratio_refs=bin_contents_normal[:num_classes] if ratio else [],  # training for ratio
            ratio_refs_uncertainties=uncertainties_normal[:num_classes] if ratio else [],
            text_boxes=ratio_titles,
            colors=colors_normal,
            colors_errors=colors_errors_normal,
            legend_labels=legend_labels,
            title=f"Neural Network Output {i}" if not binary_classification else "Neural Network Output",
            x_label="DNN Output",
            y_labels=["Normalized Prediction"] + ["Pred. / Train"] * num_classes,
            x_range=(bin_edges_normal[0], bin_edges_normal[-1]),
            figpath=os.path.join(
                fig_dir, f"DNN_output_{i}_normalized.pdf" if not binary_classification else "DNN_output_normalized.pdf"
            ),
        )

    # write AUC values to results string
    results_string = ""
    results_string_args = []
    if do_roc:
        for i in range(num_classes if not binary_classification else 1):
            if binary_classification:
                results_string += " AUC (training): {:.4f}\n"
                results_string += " AUC (validation): {:.4f}\n"
                if explicit_testing_dataset:
                    results_string += " AUC (testing): {:.4f}\n"
            else:
                results_string += (
                    f" AUC ({class_labels[i]} vs. rest):\n"
                    if class_labels is not None
                    else f" AUC (class {i} vs. rest):\n"
                )
                results_string += "\ttraining: {:.4f}\n"
                results_string += "\tvalidation: {:.4f}\n"
                if explicit_testing_dataset:
                    results_string += "\ttesting: {:.4f}\n"

            results_string_args += [auc_train_classes[i], auc_val_classes[i]]
            if explicit_testing_dataset:
                results_string_args.append(auc_test_classes[i])

    # keep track of the calculated metrics to evaluate composite metrics
    metric_values_dict = {}

    # loss
    results_string += " Loss:\n"
    losses = model.loss(native_datasets)
    if explicit_testing_dataset:
        train_loss, val_loss, test_loss = losses
    else:
        train_loss, val_loss = losses
    results_string += "\ttraining: {}\n".format("{:.3f}")
    results_string += "\tvalidation: {}\n".format("{:.3f}")
    if explicit_testing_dataset:
        results_string += "\ttesting: {}\n".format("{:.3f}")
        metric_values_dict["loss"] = train_loss
        metric_values_dict["val_loss"] = val_loss
        metric_values_dict["test_loss"] = test_loss
        results_string_args += [train_loss, val_loss, test_loss]
    else:
        metric_values_dict["loss"] = train_loss
        metric_values_dict["val_loss"] = val_loss
        results_string_args += [train_loss, val_loss]

    if native_metrics != []:
        # instantiate native metrics
        native_metrics = [(name, metric(**kwargs)) for name, (metric, kwargs) in native_metrics]

        # calculate the metric values
        metric_values = model.calc_native_metrics(
            native_metrics=[metric for (_, metric) in native_metrics],
            data=native_datasets,
            weighted=False,
        )
        if explicit_testing_dataset:
            metric_values_train, metric_values_val, metric_values_test = metric_values
        else:
            metric_values_train, metric_values_val = metric_values

        results_string += " Native metrics:\n"
        for i, (metric_name, _) in enumerate(native_metrics):
            metric_value_train = metric_values_train[i]
            metric_value_val = metric_values_val[i]
            if explicit_testing_dataset:
                metric_value_test = metric_values_test[i]

            results_string += "\t{} (training): {}\n".format(metric_name, "{:.3f}")
            results_string += "\t{} (validation): {}\n".format(metric_name, "{:.3f}")
            if explicit_testing_dataset:
                results_string += "\t{} (testing): {}\n".format(metric_name, "{:.3f}")
                metric_values_dict[f"{metric_name}"] = metric_value_train
                metric_values_dict[f"val_{metric_name}"] = metric_value_val
                metric_values_dict[f"test_{metric_name}"] = metric_value_test
                results_string_args += [metric_value_train, metric_value_val, metric_value_test]
            else:
                metric_values_dict[f"{metric_name}"] = metric_value_train
                metric_values_dict[f"val_{metric_name}"] = metric_value_val
                results_string_args += [metric_value_train, metric_value_val]

    if weighted_native_metrics != []:
        # instantiate weighted native metrics
        weighted_native_metrics = [(name, metric(**kwargs)) for name, (metric, kwargs) in weighted_native_metrics]

        # calculate the metric values
        metric_values = model.calc_native_metrics(
            native_metrics=[metric for (_, metric) in weighted_native_metrics],
            data=native_datasets,
            weighted=True,
        )
        if explicit_testing_dataset:
            metric_values_train, metric_values_val, metric_values_test = metric_values
        else:
            metric_values_train, metric_values_val = metric_values

        results_string += " Weighted native metrics:\n"
        for i, (metric_name, _) in enumerate(weighted_native_metrics):
            metric_value_train = metric_values_train[i]
            metric_value_val = metric_values_val[i]
            if explicit_testing_dataset:
                metric_value_test = metric_values_test[i]

            results_string += "\t{} (training): {}\n".format(metric_name, "{:.3f}")
            results_string += "\t{} (validation): {}\n".format(metric_name, "{:.3f}")
            if explicit_testing_dataset:
                results_string += "\t{} (testing): {}\n".format(metric_name, "{:.3f}")
                metric_values_dict[f"{metric_name}"] = metric_value_train
                metric_values_dict[f"val_{metric_name}"] = metric_value_val
                metric_values_dict[f"test_{metric_name}"] = metric_value_test
                results_string_args += [metric_value_train, metric_value_val, metric_value_test]
            else:
                metric_values_dict[f"{metric_name}"] = metric_value_train
                metric_values_dict[f"val_{metric_name}"] = metric_value_val
                results_string_args += [metric_value_train, metric_value_val]

    if custom_metrics != []:
        results_string += " Custom metrics:\n"
        custom_metric_values = model.calc_custom_metrics(
            custom_metrics=[metric for (_, metric) in custom_metrics],
            data=native_datasets,
            skip_test_dataset=False,
        )
        for i, (metric_name, _) in enumerate(custom_metrics):
            results_string += "\t{} (training): {}\n".format(metric_name, "{:.3f}")
            results_string += "\t{} (validation): {}\n".format(metric_name, "{:.3f}")
            if explicit_testing_dataset:
                results_string += "\t{} (testing): {}\n".format(metric_name, "{:.3f}")
                metric_values_dict[f"train_{metric_name}"] = custom_metric_values[0][i]
                metric_values_dict[f"val_{metric_name}"] = custom_metric_values[1][i]
                metric_values_dict[f"test_{metric_name}"] = custom_metric_values[2][i]
                results_string_args += [
                    custom_metric_values[0][i],
                    custom_metric_values[1][i],
                    custom_metric_values[2][i],
                ]
            else:
                metric_values_dict[f"train_{metric_name}"] = custom_metric_values[0][i]
                metric_values_dict[f"val_{metric_name}"] = custom_metric_values[1][i]
                results_string_args += [custom_metric_values[0][i], custom_metric_values[1][i]]

    if composite_metrics != []:
        results_string += " Composite metrics:\n"
        for metric_name, dep_metric_names, metric in composite_metrics:
            dep_metric_values = (metric_values_dict[dep_metric_name] for dep_metric_name in dep_metric_names)
            results_string += "\t{}: {}\n".format(metric_name, "{:.3f}")
            results_string_args.append(metric(*dep_metric_values))

    if print_results:
        print(results_string.format(*results_string_args))

    if results_dir is not None:
        with open(os.path.join(results_dir, "results_eval.txt"), "w") as results_file:
            results_file.write(results_string.format(*results_string_args))

    if not return_unfilled:
        return results_string.format(*results_string_args)
    else:
        results_string = results_string.replace("{:.3f}", "{}").replace("{:.4f}", "{}")
        return results_string, results_string_args
